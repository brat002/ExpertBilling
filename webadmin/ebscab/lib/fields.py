# -*- coding: utf-8 -*-

import base64
import decimal
import struct
from hashlib import md5

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import fields, widgets
from django.forms.widgets import PasswordInput
from ipaddr import _IPAddrBase, IPAddress, IPNetwork


class IPNetworkWidget(widgets.TextInput):

    def render(self, name, value, attrs=None):
        if isinstance(value, _IPAddrBase):
            value = u'%s' % value
            value = value.replace('/32', '')
        return super(IPNetworkWidget, self).render(name, value, attrs)


class IPNetworkManager(models.Manager):
    use_for_related_fields = True

    def __init__(self, qs_class=models.query.QuerySet):
        self.queryset_class = qs_class
        super(IPNetworkManager, self).__init__()

    def get_query_set(self):
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)


class IPNetworkQuerySet(models.query.QuerySet):

    net = None

    def network(self, key, value):
        if not isinstance(value, _IPAddrBase):
            value = IPNetwork(value)
        self.net = (key, value)
        return self

    def iterator(self):
        for obj in super(IPNetworkQuerySet, self).iterator():
            try:
                net = IPNetwork(getattr(obj, self.net[0]))
            except (ValueError, TypeError):
                pass
            else:
                if not self.net[1] in net:
                    continue
            yield obj

    @classmethod
    def as_manager(cls, ManagerClass=IPNetworkManager):
        return ManagerClass(cls)


class IPNetworkField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "IP Network Field with CIDR support"
    empty_strings_allowed = False

    def db_type(self, connection):
        return 'varchar(45)'

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddrBase):
            return value

        try:
            return IPNetwork(value.encode('latin-1'))
        except Exception, e:
            raise ValidationError(e)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def get_prep_value(self, value):
        if isinstance(value, _IPAddrBase):
            value = '%s' % value

        return unicode(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': fields.CharField,
            'widget': IPNetworkWidget,
        }
        defaults.update(kwargs)
        return super(IPNetworkField, self).formfield(**defaults)


class IPAddressField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "IP Address Field with IPv6 support"

    def db_type(self, connection):
        return 'varchar(42)'

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddrBase):
            return value

        try:
            return IPAddress(value.encode('latin-1'))
        except Exception, e:
            raise ValidationError(e)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def get_prep_value(self, value):
        if isinstance(value, _IPAddrBase):
            value = '%s' % value
        return unicode(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': fields.CharField,
            'widget': IPNetworkWidget
        }
        defaults.update(kwargs)
        return super(IPAddressField, self).formfield(**defaults)


class PasswordHashField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "Store password as hash"

    def db_type(self, connection):
        return 'varchar(128)'

    def to_python(self, value):
        if not value:
            return None

    def get_prep_value(self, value):
        if value:
            value = md5(md5(value).hexdigest()).hexdigest()
        return value

    def formfield(self, **kwargs):
        defaults = {
            'form_class': fields.CharField,
            'widget': PasswordInput,
        }
        defaults.update(kwargs)
        return super(PasswordHashField, self).formfield(**defaults)

# django-pgcrypto
# Dan Watson
#
# A pure python implementation of ASCII Armor, along with various
# padding and unpadding functions, all compatible with pgcrypto.
#
# Additionally, this module defines Django fields that automatically
# encrypt and armor (and decrypt and dearmor) values for storage
# in text fields. Values stored using these fields may be read by
# pgcrypto using decrypt(dearmor(col),...), and values stored by
# pgcrypto using armor(encrypt(col,...)) may be read by these fields.
#
# See http://www.ietf.org/rfc/rfc2440.txt for ASCII Armor specs.

__version_info__ = (1, 1, 0)
__version__ = '.'.join(str(i) for i in __version_info__)

has_django = True

CRC24_INIT = 0xB704CE
CRC24_POLY = 0x1864CFB


def ord_safe(ch):
    if isinstance(ch, int):
        return ch
    return ord(ch)


def crc24(data):
    crc = CRC24_INIT
    for byte in data:
        crc ^= (ord_safe(byte) << 16)
        for _i in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= CRC24_POLY
    return crc & 0xFFFFFF


def armor(data):
    """
    Returns a string in ASCII Armor format, for the given binary data. The
    output of this is compatiple with pgcrypto's armor/dearmor functions.
    """
    template = ('-----BEGIN PGP MESSAGE-----\n%(headers)s\n\n%(body)s\n='
                '%(crc)s\n-----END PGP MESSAGE-----')
    headers = ['Version: django-pgcrypto %s' % __version__]
    body = base64.b64encode(data)
    # The 24-bit CRC should be in big-endian, strip off the first byte (it's
    # already masked in crc24).
    crc = base64.b64encode(struct.pack('>L', crc24(data))[1:])
    return template % {
        'headers': '\n'.join(headers),
        'body': body.decode('ascii'),
        'crc': crc.decode('ascii'),
    }


class BadChecksumError (Exception):
    pass


def dearmor(text, verify=True):
    """
    Given a string in ASCII Armor format, returns the decoded binary data.
    If verify=True (the default), the CRC is decoded and checked against that
    of the decoded data, otherwise it is ignored. If the checksum does not
    match, a BadChecksumError exception is raised.
    """
    lines = text.strip().split('\n')
    data_lines = []
    check_data = None
    started = False
    in_body = False
    for line in lines:
        if line.startswith('-----BEGIN'):
            started = True
        elif line.startswith('-----END'):
            break
        elif started:
            if in_body:
                if line.startswith('='):
                    # Once we get the checksum data, we're done.
                    check_data = line[1:5].encode('ascii')
                    break
                else:
                    # This is part of the base64-encoded data.
                    data_lines.append(line)
            else:
                if line.strip():
                    # This is a header line, which we basically ignore for now.
                    pass
                else:
                    # The data starts after an empty line.
                    in_body = True
    b64_str = ''.join(data_lines)
    # Python 3's b64decode expects bytes, not a string. We know base64 is
    # ASCII, though.
    data = base64.b64decode(b64_str.encode('ascii'))
    if verify and check_data:
        # The 24-bit CRC is in big-endian, so we add a null byte to the
        # beginning.
        crc = struct.unpack('>L', b'\0' + base64.b64decode(check_data))[0]
        if crc != crc24(data):
            raise BadChecksumError()
    return data


def unpad(text, block_size):
    """
    Takes the last character of the text, and if it is less than the block_size,
    assumes the text is padded, and removes any trailing zeros or bytes with the
    value of the pad character. See http://www.di-mgt.com.au/cryptopad.html for
    more information (methods 1, 3, and 4).
    """
    end = len(text)
    if end == 0:
        return text
    padch = ord_safe(text[end - 1])
    if padch > block_size:
        # If the last byte value is larger than the block size, it's not
        # padded.
        return text
    while end > 0 and ord_safe(text[end - 1]) in (0, padch):
        end -= 1
    return text[:end]


def pad(text, block_size, zero=False):
    """
    Given a text string and a block size, pads the text with bytes of the same value
    as the number of padding bytes. This is the recommended method, and the one used
    by pgcrypto. See http://www.di-mgt.com.au/cryptopad.html for more information.
    """
    num = block_size - (len(text) % block_size)
    ch = '\0' if zero else chr(num)
    return text + (ch * num)


def aes_pad_key(key):
    """
    AES keys must be either 16, 24, or 32 bytes long. If a key is provided that is not
    one of these lengths, pad it with zeroes (this is what pgcrypto does).
    """
    if len(key) in (16, 24, 32):
        return key
    if len(key) < 16:
        return pad(key, 16, zero=True)
    elif len(key) < 24:
        return pad(key, 24, zero=True)
    else:
        return pad(key[:32], 32, zero=True)

if has_django:
    class BaseEncryptedField (models.Field):

        def __init__(self, *args, **kwargs):
            # Just in case pgcrypto and/or pycrypto support more than
            # AES/Blowfish.
            valid_ciphers = getattr(
                settings, 'PGCRYPTO_VALID_CIPHERS', ('AES', 'Blowfish'))
            cipher_name = kwargs.pop('cipher',
                                     getattr(settings,
                                             'PGCRYPTO_DEFAULT_CIPHER',
                                             'AES'))
            assert cipher_name in valid_ciphers
            self.cipher_key = kwargs.pop('key',
                                         getattr(settings,
                                                 'PGCRYPTO_DEFAULT_KEY',
                                                 ''))
            self.charset = 'utf-8'
            if cipher_name == 'AES':
                self.cipher_key = aes_pad_key(self.cipher_key)
            mod = __import__('Crypto.Cipher',
                             globals(),
                             locals(),
                             [cipher_name], -1)
            self.cipher_class = getattr(mod, cipher_name)
            self.check_armor = kwargs.pop('check_armor', True)
            models.Field.__init__(self, *args, **kwargs)

        def get_internal_type(self):
            return 'TextField'

        def south_field_triple(self):
            """
            Describe the field to south for use in migrations.
            """
            from south.modelsinspector import introspector

            args, kwargs = introspector(self)
            return ("django.db.models.fields.TextField", args, kwargs)

        def get_cipher(self):
            """
            Return a new Cipher object for each time we want to encrypt/decrypt. This is because
            pgcrypto expects a zeroed block for IV (initial value), but the IV on the cipher
            object is cumulatively updated each time encrypt/decrypt is called.
            """
            return self.cipher_class.new(self.cipher_key,
                                         self.cipher_class.MODE_CBC,
                                         b'\0' * self.cipher_class.block_size)

        def is_encrypted(self, value):
            return (isinstance(value, basestring) and
                    value.startswith('-----BEGIN'))

        def to_python(self, value):
            if self.is_encrypted(value):
                # If we have an encrypted (armored, really) value, do the following when accessing it as a python value:
                #    1. De-armor the value to get an encrypted bytestring.
                #    2. Decrypt the bytestring using the specified cipher.
                #    3. Unpad the bytestring using the cipher's block size.
                # 4. Decode the bytestring to a unicode string using the
                # specified charset.
                return unpad(self.get_cipher()
                             .decrypt(dearmor(value, verify=self.check_armor)),
                             self.cipher_class.block_size).decode(self.charset)
            return value or ''

        def get_prep_value(self, value):
            if value and not self.is_encrypted(value):
                # If we have a value and it's not encrypted, do the following before storing in the database:
                #    1. Convert it to a unicode string (by calling unicode).
                #    2. Encode the unicode string according to the specified charset.
                #    3. Pad the bytestring for encryption, using the cipher's block size.
                #    4. Encrypt the padded bytestring using the specified cipher.
                # 5. Armor the encrypted bytestring for storage in the text
                # field.
                return armor(self.get_cipher().encrypt(
                    pad(unicode(value).encode(self.charset),
                        self.cipher_class.block_size)))
            return value or ''

    class EncryptedTextField (BaseEncryptedField):
        __metaclass__ = models.SubfieldBase

        def formfield(self, **kwargs):
            defaults = {'widget': forms.TextInput}
            defaults.update(kwargs)
            return super(EncryptedTextField, self).formfield(**defaults)

    class EncryptedDecimalField (BaseEncryptedField):
        __metaclass__ = models.SubfieldBase

        def formfield(self, **kwargs):
            defaults = {'form_class': forms.DecimalField}
            defaults.update(kwargs)
            return super(EncryptedDecimalField, self).formfield(**defaults)

        def to_python(self, value):
            if value:
                return decimal.Decimal(
                    super(EncryptedDecimalField, self).to_python(value))
            return value
