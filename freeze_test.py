from base64 import b64decode as _x_
from zlib import decompress as _z_
import sys, zlib
import imp
import modulefinder
import marshal

def _2_( __0, __1 ):
    # local variables:
    #  __0 - string argument
    #  __1 - segment length
    #  __2 - result
    #  __3 - start index
    #  __4 - end index
    #  __5 - temporary variable
    __2 = []
    import math
    __3, __4 = 0, __1
    for __5 in xrange( int( math.ceil( float( len( __0 ) ) / __1 ) ) ):
        __2.append( __0[ __3 : __4 ] )
        __3 += __1
        __4 += __1
    return __2

def _3_( __0, __1 ):
    # local variables:
    #  __0 - string argument
    #  __1 - string key
    #  __2 - result
    #  __3 - part of a string
    #  __4 - character in a string
    #  __5 - masking character
    __2 = ''
    for __3 in _2_( __0, len( __1 ) ): # split_string()
        for __4, __5 in zip( __3, __1 ):
            __2 += chr( 0xff & ( ord( __4 ) ^ ord( __5 ) ) )
    return __2



def _dump_code( code ):
    import marshal
    return marshal.dumps( code )

# Returns compressed bytecode
def _pack_code( bytecode ):
    result = zlib.compress( bytecode, 9 )
    print( 'Compressing bytecode %d -> %d' % ( len( bytecode ), len( result ) ) )
    return result

# Returns a list containing segments of 'string' -
# each has length 'seg_len'
def _split_str( string, seglen ):
    result = []
    import math
    si, di = 0, seglen
    for i in xrange( int( math.ceil( float( len( string ) ) / seglen ) ) ):
        result.append( string[ si : di ] )
        si += seglen
        di += seglen
    return result

# Returns encrypted version of 'string'
# Bit-encryption algorithm: 76543210 -> ~(75316420)
def _encrypt_str( string, key = None ):
    result = ''
    if key:
        # encrypting each character in chunk with corresponding character from key
        for s in _split_str( string, len( key ) ):
            for ch, mask in zip( s, key ):
                result += chr( 0xff & ( ord( ch ) ^ ord( mask ) ) ) # simple, but effective encoding
    else:
        for ch in string:
            ch = ord( ch )
            result += chr( 0xff & ~(
                ( ch & 0x80 ) | ( ( ch << 1 ) & 0x40 ) | ( ( ch << 2 ) & 0x20 ) | ( ( ch << 3 ) & 0x10 ) | \
                ( ch & 0x01 ) | ( ( ch >> 1 ) & 0x02 ) | ( ( ch >> 2 ) & 0x04 ) | ( ( ch >> 3 ) & 0x08 )
            ) )
    return result

if __name__ == '__main__':
    fobj = open('test_module.pyc','rb')
    print fobj.read(8)
    print imp.get_magic()
    a1 = fobj.read()
    fobj.close()
    cmpl = marshal.loads(a1)
    kkey='2'
    
    dmpcode = _dump_code(cmpl)
    pckcode = _pack_code(dmpcode)
    enccode = _encrypt_str(pckcode, kkey)
    
    decccode = _3_(enccode, kkey)
    depccode = _z_(decccode)
    dedmcode = marshal.loads(depccode)
    
    '''nm = imp.new_module('test_module')
    setattr(nm, '__code__', cmpl)
    print nm.__dict__
    sys.modules['test_module'] = nm
    exec getattr( nm, '__code__' ) in nm.__dict__
    #sys.modules['test_module'] = nm

    cbl = 'print test_module.hello()'
    ccmp = compile(cbl, "", 'exec')
    print sorted(sys.modules.iterkeys())'''