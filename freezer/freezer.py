#!/usr/bin/env python2.5
####################################################################################################
"""\
This module provides a functionality that allows you
to freeze one or several dependent Python modules in
a single binary executable file which is linked with
a Python library, so it can be successfully ran later.\
"""
####################################################################################################
_DEFAULT_PROT_KEY = '\0'

_PROTECTION_CHUNK_0 = r"""
import sys
sys.path = [ sys.path[ 0 ] + '/modules' ]
from base64 import b64decode as _x_
from zlib import decompress as _z_
_1i = lambda: ''
def _1fi_():
        global _1i
        ____1i = open(_x_('bGljZW5zZS5saWM=')).read() #license.lic
	_1i =  lambda: ____1i
	
# get_key():
#  returns string hash of concatented
#  serial numbers of harddrives, architecture,
#  machine type, computer's network name,
#  platform type, processor's name, system's
#  version, OS name and user login
def _1_():"""

_PROTECTION_CHUNK_1_L = r"""
	# local variables:
	#  __0 - string constants
	#  __1 - exit code of a command
	#  __2 - output of the command
	#  __3 - list of serials
	#  __4 - temporary variable
	#  __5 - module
	#  __6 - key data
	global _1i
	__0 = [
		_x_( 'L2Rldi9kaXNrL2J5LXV1aWQv' ),         # '/dev/disk/by-uuid'
		_x_( 'Y2FuJ3QgaWRlbnRpZnkgaGFyZHdhcmU=' ), # "can't identify hardware"
		_x_( 'cGFydA==' ),                         # 'part'
		_x_( 'b3M=' ),                             # 'os'
		_x_( 'bGlzdGRpcg==' ),                     # 'listdir'
		_x_( 'bWQ1' ),                             # 'md5'
		_x_( 'bmV3' ),                             # 'new'
		_x_( 'aGV4ZGlnZXN0' ),                     # 'hexdigest'
		_x_( 'ZG1pZGVjb2RlIC1zIHN5c3RlbS11dWlk'),
		_x_( 'Y29tbWFuZHM='),                      #'9' 'commands'
		_x_( 'cGF0aA=='),                           #$10 'path'
		_x_( 'cmVhbHBhdGg='),                      #$11 'realpath'
		_x_( 'Z2V0Y3dk'),                          #$12 'getcwd'
		_x_( 'L2Jpbi9kZiA='),                      #$13 '/bin/df '
		_x_( 'Z2V0c3RhdHVzb3V0cHV0'),              #$14 'getstatusoutput'
		_x_( 'c3lz'),                              #$15 'sys
		_x_( 'ZXhpdA=='),                           #$16 'exit'
	]
	
	__5 = __import__( __0[ 3 ] ) # import os
	_5c = __import__( __0[ 9 ] )
	_5s = __import__( __0[ 15 ] )
	try:
	    _3f = getattr( _5c, __0[14] )(__0[13] + getattr(__5, __0[12])())[1].split('\n')[1].split(' ')[0]
            __3 = filter(lambda x: getattr(getattr(__5, __0[10]), __0[11])(__0[0] + x) == _3f, getattr( __5, __0[4] )( __0[0] ))
        except:
            print "error 66004"; getattr(_5s, __0[16])()
        if not __3:
            print "error 11294"; getattr(_5s, __0[16])()
        else:
            __3 = __3[0]
	    
	__6 = str.join('', __3)
	__5 = __import__(__0[5]) # import md5
	__6 = getattr(getattr(__5, __0[6])(__6), __0[7])() # ... = md5.new(...).hexdigest()
	__6 = __6[:-1] + 'L'
	_1fi_()
	__6 += _1i()
	#del __0
	return __6.upper()
"""

_PROTECTION_CHUNK_1_D = r"""
	# local variables:
	#  __0 - string constants
	#  __1 - exit code of a command
	#  __2 - output of the command
	#  __3 - list of serials
	#  __4 - temporary variable
	#  __5 - module
	#  __6 - key data
	global _1i
	__0 = [
		_x_( 'L2Rldi9kaXNrL2J5LXV1aWQv' ),         # '/dev/disk/by-uuid'
		_x_( 'Y2FuJ3QgaWRlbnRpZnkgaGFyZHdhcmU=' ), # "can't identify hardware"
		_x_( 'cGFydA==' ),                         # 'part'
		_x_( 'b3M=' ),                             # 'os'
		_x_( 'bGlzdGRpcg==' ),                     # 'listdir'
		_x_( 'bWQ1' ),                             # 'md5'
		_x_( 'bmV3' ),                             # 'new'
		_x_( 'aGV4ZGlnZXN0' ),                     # 'hexdigest'
		_x_( 'ZG1pZGVjb2RlIC1zIHN5c3RlbS11dWlk'),
		_x_( 'Y29tbWFuZHM='),                      #$9 'commands'
		_x_( 'L3NiaW4vc3lzY3RsIGRldi4lcy4lcy4lJWRlc2M='), #$10 '/sbin/sysctl dev.%s.%s.%%desc'
		_x_( 'dmlydHVhbA=='),                      #$11 'virtual'
		_x_( 'Z2V0Y3dk'),                          #$12 'getcwd'
		_x_( 'L2Jpbi9kZiA='),                      #$13 '/bin/df '
		_x_( 'Z2V0c3RhdHVzb3V0cHV0'),              #$14 'getstatusoutput'
		_x_( 'c3lz'),                              #$15 'sys
		_x_( 'ZXhpdA=='),                          #$16 'exit'
	]
	__5 = __import__( __0[ 3 ] ) # import os
	_5c = __import__( __0[ 9 ] )
	_5s = __import__( __0[ 15 ] )
	try:
	    _3f = getattr( _5c, __0[14] )(__0[13] + getattr(__5, __0[12])())[1].split('\n')[1].split(' ')[0]
	    _3d = _3f[:2]; _3n = _3f[2]
            __3 = getattr( _5c, __0[14] )(__0[10] % (_3d, _3n))
	    if not __3: print "error 77075"; getattr(_5s, __0[16])()
	    #if __3.lower().find(__0[11]) != -1: print "error 77088"; getattr(_5s, __0[16])()
	    __3 = __3.split(': ')[1]
        except:
            print "error 77004"; getattr(_5s, __0[16])()
	__6 = str.join('', __3)
	__5 = __import__(__0[5]) # import md5
	__6 = getattr(getattr(__5, __0[6])(__6), __0[7])() # ... = md5.new(...).hexdigest()
	__6 = __6[:-1] + 'D'
	_1fi_()
	__6 += _1i()
	#del __0
	return __6.upper()
"""

_PROTECTION_CHUNK_2 = """
	return %r
""" % _DEFAULT_PROT_KEY

_PROTECTION_CHUNK_3 = r"""
# split_string( string, seglen ):
#  splits 'string' into segments of
#  length 'seglen' and returns them
#  as a list
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

# decrypt_string( string, key ):
#  returns a decrypted string
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

# load_modules():
#  unpacks and loads strored modules
def _4_():
	# local variables:
	#  __0 - string constants
	#  __1 - descryption key
	#  __2 - temporary module name
	#  __3 - unpacked module name
	#  __4 - main module code
	#  __5 - module
	#  __6 - list of modules
	global _0_, _1_, _2_, _3_, _0om_
	__0 = [
		_x_( 'X19tYWluX18=' ), # '__main__'
		_x_( 'X19jb2RlX18=' ), # '__code__'
	]
	import imp, marshal
	__1 = _1_()
	__6 = []
	__od = {}
	# unpacking modules
	for __2 in _0_:
		__3 = _z_( __2 )
		if __3 != __0[ 0 ]:
			__5 = imp.new_module( __3 )
			setattr( __5, __0[ 1 ], marshal.loads( _z_( _3_( _0_[ __2 ], __1 ) ) ) ) # setting a code object
			if __2 in _0om_:
			    __od[__2] = __5
			else:
			    __6.append( __5 )
			sys.modules[ __3 ] = __5
		else:
			__4 = marshal.loads( _z_( _3_( _0_[ __2 ], __1 ) ) )
	del __1, _0_, _1_, _2_, _3_ # deleting all traces from the memory
	# loading modules
	for __5 in __6: exec getattr( __5, __0[ 1 ] ) in __5.__dict__
	for __omk in _0om_:
	    __5 = __od[__omk]
	    exec getattr( __5, __0[ 1 ] ) in __5.__dict__
	exec __4 in globals() # running main module

# main()
def _5_():
	# local variables:
	#  __0 - error
	try:
		_4_() # load_modules()
	except Exception, __0:
		sys.stderr.write( '%s: %s\n' % ( sys.argv[ 0 ], str( __0 ) ) )
		sys.exit( 1 )

_5_()
"""

_CODE_CHUNK_0 = r"""
typedef struct {
	char
		*name,
		*code;
	int
		size;
} FrozenModule;

static FrozenModule modules[] = {
"""

_CODE_CHUNK_1 = r"""	{ 0 }
};

static
void
decrypt_buffer( char * buf, int count )
{
	for ( register int idx = 0; idx < count; idx++, buf++ ) {
		*buf = ~*buf;
		*buf = ( *buf & 0x80 ) | ( ( *buf >> 1 ) & 0x20 ) | ( ( *buf >> 2 ) & 0x08 ) | ( ( *buf >> 3 ) & 0x02 ) |
		       ( *buf & 0x01 ) | ( ( *buf << 1 ) & 0x04 ) | ( ( *buf << 2 ) & 0x10 ) | ( ( *buf << 3 ) & 0x40 );
	}
}

int main( int argc, char ** argv )
{
	extern FrozenModule * PyImport_FrozenModules;
	extern int Py_NoSiteFlag;
	int Py_FrozenMain( int, char ** );

	Py_NoSiteFlag = 1;
	decrypt_buffer( modules->code, modules->size );
	PyImport_FrozenModules = modules;
	return Py_FrozenMain( argc, argv );
}
"""

####################################################################################################

import sys, os, os.path, modulefinder, zlib, traceback

_PY_VER = float( sys.version[ : 3 ] )
if _PY_VER < 2.4 or _PY_VER >= 3.0: raise RuntimeError( 'Python of version 2.x (>=2.4) required' )

_DEBUGGING = False

if _DEBUGGING:
	def _WRITE2LOG( arg, log = open( '/tmp/freezer.log', 'w' ) ): print >> log, arg
else:
	def _WRITE2LOG( arg, log = None ): pass

def _reset_flags():
	global _flags
	_flags = {
		'SHOW_HELP': False,        # show help and quit
		'PY_FILE': None,           # name of a .py file for freezing
		'C_FILE': None,            # name of a generated .c file
		'PROTECTION_KEY':
			_DEFAULT_PROT_KEY,    # protection key for encryption
		'IGNORE_MISSING': False,   # ignore missing modules
		'SEARCH_PATH': None,       # path to search local modules
		'INIT_ORDER': [],          # impose some order on modules initialization
		'ADDITIONAL_MODULES': {    # additional modules that will be freezed
			'os': None,
			'commands': None,
			'platform': None,
			'zlib': None,
			'base64': None,
			'md5': None,
		},
		'NONLOCAL': [              # names of modules that should be treated as non-local
			'os',
			'commands',
			'platform',
			'zlib',
			'base64',
			'md5',
		],
		'LOCATION': os.getcwd() + os.sep, # current working directory
		'SCRIPT_DIR': os.path.dirname( sys.modules[ __name__ ].__file__ ), # location of this script
		'FREEZEFILE_VARS': {},     # variables in Freezefile
	}

_USAGE = r"""
Usage: freezer [options] [PY_FILE [C_FILE ]]
 Freezes a Python program and creates a binary
 executable with an optional anti-copy protection.
Options:
  -h,     --help         show this and quit
  -k KEY, --key=KEY      a key for encryption
  --amods=MODS           include additional modules MODS that
                         cannot be found by introspection.
                         MODS are separated by commas pairs
                         MODNAME:FILENAME (for example
                         --amods='pkg.io:io.py,data:data.py')
  --nloc=NAMES           separated by commas list of names of
                         modules that must not be frozen
  --order=NAMES          separated by commas ordered list of names of
                         modules that must be initialized in that order
  -i                     ignore missing modules
 Without any arguments freezer attempts to locate and
 execute a file 'Freezefile' in the current directory.
Freezefile variables:
  PY_FILE            - name of a main module (str)
  C_FILE             - name of generated .c file (str)
  PROTECTION_KEY     - key for encryption (str)
  IGNORE_MISSING     - ignore missing modules (bool)
  ADDITIONAL_MODULES - modules that also must be frozen (dict)
  NONLOCAL           - names of modules that must be treated
                       as non-local (list)
"""

####################################################################################################

class FreezerError( RuntimeError ): pass

# Returns a bytecode of compiled object
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

# Writes frozen in 'string' module to file 'f'
def _write2file( file, string, arrname ):
	def repr_str( string ):
		result = '"'
		for ch in string: result += '\\x%02X' % ord( ch )
		return result + '"'
	file.write( '\nstatic char %s[] =\n' % arrname )
	for s in _split_str( string, 16 ):
		file.write( '\t%s\n' % repr_str( s ) )
	file.write( ';\n' )

# Compiles a .c file into an executable
def _compile_proj():
	incdir = os.path.join( _flags[ 'SCRIPT_DIR' ], 'include' )
	import distutils.sysconfig
	extraopts = distutils.sysconfig.get_config_var( 'LINKFORSHARED' )
	if not extraopts: extraopts = ''
	args = {
		'CC': 'gcc',
		'CFLAGS': '-std=gnu99 -O3 -mtune=i386 -I"%s"' % incdir,
		'SRC': _flags[ 'C_FILE' ],
		'LFLAGS': '-lpython%s -lz -Wl,-rpath=./ %s' % (
			_PY_VER,
			extraopts
		),
		'TARGET': _flags[ 'C_FILE' ][ : -2 ],
	}
	cmd = '%(CC)s %(CFLAGS)s %(SRC)s %(LFLAGS)s -o %(TARGET)s' % args
	print '=================================================='
	print 'Compiling: ' + cmd
	if os.system( cmd ): raise OSError( 'can not compile program' )
	cmd = 'strip %(TARGET)s' % args
	print '=================================================='
	print 'Stripping: ' + cmd
	if os.system( cmd ): raise OSError( 'can not strip program' )

# Tries to find modules that modulefinder did not
def _find_mods( modsnames, modules ):
	print '=================================================='
	print 'Looking for modules:'
	_WRITE2LOG( '@ looking for %r' % modsnames )
	def get_deps( mname, fname ):
		_WRITE2LOG( "* getting dependencies of '%s' in '%s'" % ( mname, fname ) )
		mf = modulefinder.ModuleFinder()
		mf.run_script( fname )
		m = mf.modules[ '__main__' ]
		m.__name__ = mname
		mf.modules[ mname ] = m
		del mf.modules[ '__main__' ]
		modules.update( mf.modules )
	def find_one( mname, searchpath = None ):
		print '-> %s' % mname
		basename = mname.replace( '.', os.path.sep )
		extensions = ( '.py', '.pyc', '.so' )
		if not searchpath: path = sys.path
		else: path = ( searchpath, )
		_WRITE2LOG( "? searching for a module '%s' in %r" % ( mname, searchpath ) )
		for p in path:
			for rest in ( '__init__.py', '__init__.pyc' ):
				fname = os.path.join( p, basename, rest )
				_WRITE2LOG( "checking a file '%s'" % fname )
				if os.path.exists( fname ):
					searchpath = p
					_WRITE2LOG( '! found' )
					break
			else:
				for ext in extensions:
					fname = os.path.join( p, basename + ext )
					_WRITE2LOG( "checking a file '%s'" % fname )
					if os.path.exists( fname ):
						searchpath = p
						_WRITE2LOG( '! found' )
						break
				else: continue
			break
		else: return False
		if '.' in mname: # compoud package - looking for parent
			if not find_one( mname[ : mname.rindex( '.' ) ], searchpath ): return False
		print ' : ' + fname
		_WRITE2LOG( "+ module is in '%s'" % fname )
		if fname.endswith( extensions[ 2 ] ): modules[ mname ] = modulefinder.Module( mname, fname )
		else: get_deps( mname, fname )
		return True
	_WRITE2LOG( '/ modules to find %r' % modsnames )
	found = []
	for modname in modsnames:
		_WRITE2LOG( "going to find '%s'" % modname )
		if find_one( modname ): found.append( modname )
	_WRITE2LOG( '>> found modules %r' % found )
	for modname in found:
		del modsnames[ modsnames.index( modname ) ]
	_WRITE2LOG( '^ couldn\'t to find %r' % modsnames )

# Returns loaded modules
def _get_mods():
	mf = modulefinder.ModuleFinder( [ _flags[ 'SEARCH_PATH' ] ], False, sys.path )
	missing = []
	for modname, filename in _flags[ 'ADDITIONAL_MODULES' ].iteritems():
		if not filename: missing.append( modname )
		elif not filename.endswith( '.so' ):
			mf.run_script( filename )
			m = mf.modules[ '__main__' ]
			m.__name__ = modname
			mf.modules[ modname ] = m
			del mf.modules[ '__main__' ]
	#for modname in _flags[ 'NONLOCAL' ]:
	#	missing.append( modname )
	mf.run_script( _flags[ 'PY_FILE' ] )
	missing.extend( mf.any_missing() )
	_WRITE2LOG( '- missing modules before compiling %r' % missing )
	_find_mods( missing, mf.modules )
	if missing:
		if _flags[ 'IGNORE_MISSING' ]:
			print '=================================================='
			print >> sys.stderr, 'WARNING: missing modules %r' % missing
		else: raise FreezerError( "missing modules %r" % missing )
	print '=================================================='
	print 'Loading modules:'
	for m in mf.modules.itervalues():
		print '-> %s\n : %s' % ( m.__name__, m.__file__ )
	result = [ mf.modules[ '__main__' ] ]
	for m in mf.modules.itervalues():
		if ( not m.__file__ or m.__name__ == '__main__' or m.__name__ in _flags[ 'NONLOCAL' ] ): continue
		if m.__file__.startswith( _flags[ 'SEARCH_PATH' ] ):
			if not m.__code__: raise FreezerError( "can not freeze binary module '%s' in '%s'" % ( m.__name__, m.__file__ ) )
			result.append( m )
	print '=================================================='
	print 'Selecting modules for freezing:'
	for m in result:
		print '-> %s\n : %s' % ( m.__name__, m.__file__ )
	return result

# Creates complex project with a protection
def _create_proj():
	mods = {}
	f = open( _flags[ 'C_FILE' ], 'w' )
	print '=================================================='
	for m in _get_mods():
		print "Dumping '%s'" % m.__name__
		mods[ zlib.compress( m.__name__, 9 ) ] = _encrypt_str( _pack_code( _dump_code( m.__code__ ) ), _flags[ 'PROTECTION_KEY' ] )
	ordered_mods = [zlib.compress( m_name.strip(), 9 ) for m_name in  _flags[ 'INIT_ORDER' ]]
	if _flags[ 'PROTECTION_KEY' ] != _DEFAULT_PROT_KEY:
		sys_letter = _flags[ 'PROTECTION_KEY' ][-17]
		if sys_letter == 'L':
			_KEY_PROTECTION_CHUNK = _PROTECTION_CHUNK_1_L
		elif sys_letter == 'D':
			_KEY_PROTECTION_CHUNK = _PROTECTION_CHUNK_1_D
		else:
			raise SystemError('Unknown system id: %s' % sys_letter)
	else:
		_KEY_PROTECTION_CHUNK = _PROTECTION_CHUNK_2
	#_KEY_PROTECTION_CHUNK = _PROTECTION_CHUNK_1 if _flags[ 'PROTECTION_KEY' ] != _DEFAULT_PROT_KEY else _PROTECTION_CHUNK_2
	compile_str = '_0_ = ' + `mods` + '\n' + '_0om_ = ' + `ordered_mods` + '\n' + _PROTECTION_CHUNK_0 + _KEY_PROTECTION_CHUNK + _PROTECTION_CHUNK_3
	print compile_str
	protbc = _encrypt_str( _dump_code( compile(compile_str, '', 'exec') ) )
	_write2file( f, protbc, '__prot__' );
	f.write( _CODE_CHUNK_0 )
	f.write( '\t{ "__main__", __prot__, %d },\n' % len( protbc ) )
	f.write( _CODE_CHUNK_1 )
	f.close()

# Copies required modules to a local directory 'modules'
def _copy_mods():
	def get_files_names( mod ):
		ext = os.path.splitext( mod.__file__ )[ 1 ] # extension
		if '__init__' in os.path.basename( mod.__file__ ): rest = os.path.sep + '__init__' + ext
		else: rest = ext
		return ( 
			mod.__name__.replace( '.', os.path.sep ) + rest,
			mod.__file__
		)
	namepairs = []
	pydirs = sys.path[ 1 : ]
	mf = modulefinder.ModuleFinder( [ _flags[ 'SEARCH_PATH' ] ] + pydirs )
	missing = []
	for modname, filename in _flags[ 'ADDITIONAL_MODULES' ].iteritems():
		if not filename: missing.append( modname )
		elif not filename.endswith( '.so' ):
			mf.run_script( filename )
			m = mf.modules[ '__main__' ]
			m.__name__ = modname
			mf.modules[ modname ] = m
			del mf.modules[ '__main__' ]
		else: mf.modules[ modname ] = modulefinder.Module( modname, filename )
	#for modname in _flags[ 'NONLOCAL' ]:
	#	missing.append( modname )
	mf.run_script( _flags[ 'PY_FILE' ] )
	missing.extend( mf.any_missing() )
	_WRITE2LOG( '- missing modules after compiling %r' % missing )
	_find_mods( missing, mf.modules )
	if missing:
		if _flags[ 'IGNORE_MISSING' ]:
			print >> sys.stderr, 'WARNING: missing modules %r' % missing
		else:
			raise ImportError( 'missing modules %r' % missing )
	print '=================================================='
	print 'Detecting required modules:'
	for m in mf.modules.itervalues():
		print '-> %s\n : %s' % ( m.__name__, m.__file__ )
		# excluding main and built-in modules
		if ( m.__name__ == '__main__' or ( not m.__code__ and not m.__file__ ) ): continue
		if m.__file__.startswith( _flags[ 'SEARCH_PATH' ] ):
			if m.__name__ in _flags[ 'NONLOCAL' ]:
				namepairs.append( get_files_names( m ) )
			continue
		loc = ''
		for d in pydirs:
			if d in m.__file__ and len( d ) > len( loc ): loc = d # finding the longest prefix (directory name)
		if loc: namepairs.append( ( m.__file__.replace( loc + os.path.sep, '' ), m.__file__ ) )
		else: namepairs.append( get_files_names( m ) )
	del mf
	outdir = os.path.dirname( _flags[ 'C_FILE' ] )
	moddir = os.path.join( outdir, 'modules' ) # target directory
	print '=================================================='
	for p in namepairs:
		destdir = os.path.join( moddir, os.path.dirname( p[ 0 ] ) )
		if not os.path.exists( destdir ): os.makedirs( destdir )
		destfile = os.path.join( moddir, p[ 0 ] )
		if (
			( not destfile.endswith( '.py' ) and not os.path.exists( destfile ) ) or
			( destfile.endswith( '.py' ) and not os.path.exists( destfile + 'c' ) )
		): # if module is not copied and compiled yet
			print 'Copying %s\n     to %s' % ( p[ 1 ], destfile )
			if os.system( "cp \"%s\" \"%s\"" % ( p[ 1 ], destfile ) ): raise OSError( 'can not copy the file' )
	pylib = 'libpython%s.so' % _PY_VER
	srcfile = '/usr/lib/' + pylib
	if not os.path.exists( srcfile ): srcfile = '/usr/local/lib/' + pylib
	destfile = os.path.join( outdir, pylib )
	cmd = 'cp %s "%s"' % ( srcfile, destfile )
	if not os.path.exists( destfile ):
		print( 'Copying: ' + cmd )
		if os.system( cmd ): raise OSError( 'can not copy the file' )
	print '=================================================='
	import compileall
	compileall.compile_dir( moddir )
	print '=================================================='
	print 'Cleaning up...'
	for p in namepairs:
		filename = os.path.join( moddir, p[ 0 ] )
		if filename.endswith( '.py' ) and os.path.exists( filename ): os.remove( filename )

# Analizes flags
def _analize_flags():
	if _flags[ 'SHOW_HELP' ]:
		print _USAGE
		sys.exit( 0 )
	if not _flags[ 'PY_FILE' ]: raise FreezerError( 'missing main module' )
	# fixing local path
	path = os.path.dirname( _flags[ 'PY_FILE' ] )
	if path: _flags[ 'SEARCH_PATH' ] = path
	else: _flags[ 'SEARCH_PATH' ] = '.' + os.path.sep
	del path
	# normalizing files names of files
	def norm_path( path ):
		d = os.path.dirname( path )
		# checking for reference to current directory
		if d.startswith('.') or d.startswith('..'):
			path = os.path.normpath( os.path.join( _flags[ 'LOCATION' ], path ) ) # converting to an absolute path relativelly to current dir
		else:
			if path[ 0 ] != '/': path = os.path.join( _flags[ 'SEARCH_PATH' ], path )
		return path
	if not _flags[ 'C_FILE' ]: _flags[ 'C_FILE' ] = _flags[ 'PY_FILE' ][ : -2 ] + 'c'
	_flags[ 'C_FILE' ] = norm_path( _flags[ 'C_FILE' ] )
	outdir = os.path.dirname( _flags[ 'C_FILE' ] )
	if not os.path.exists( outdir ): os.makedirs( outdir )
	mods = _flags[ 'ADDITIONAL_MODULES' ]
	for k, v in mods.iteritems():
		if v: mods[ k ] = norm_path( v )
	# cheking for protection flags
	_create_proj()
	_compile_proj()
	_copy_mods()
	print '=================================================='
	print 'Done!'

# Analizes given arguments
def _parse_args( args ):
	if 'pyfile' in args:
		_flags[ 'PY_FILE' ] = args[ 'pyfile' ]
	if 'cfile' in args:
		_flags[ 'C_FILE' ] = args[ 'cfile' ]
	if 'key' in args:
		_flags[ 'PROTECTION_KEY' ] = args[ 'key' ]
	if 'ignoremissing' in args:
		_flags[ 'IGNORE_MISSING' ] = args[ 'ignoremissing' ]
	if 'amods' in args:
		_flags[ 'ADDITIONAL_MODULES' ].update( **args[ 'amods' ] )
	if 'nonlocal' in args:
		_flags[ 'NONLOCAL' ].extend( args[ 'nonlocal' ] )

# Gets options from a command line
def _parse_cmd():
	import getopt
	opts, args = getopt.getopt(
		sys.argv[ 1 : ],
		'hk:i',
		[ 'help', 'key=', 'nloc=', 'amods=' , 'order=']
	)
	for o in opts:
		if   o[ 0 ] == '-h' or o[ 0 ] == '--help' :
			_flags[ 'SHOW_HELP' ] = True
		elif o[ 0 ] == '-k' or o[ 0 ] == '--key':
			_flags[ 'PROTECTION_KEY' ] = o[ 1 ]
		elif o[ 0 ] == '-i':
			_flags[ 'IGNORE_MISSING' ] = True
		elif o[ 0 ] == '--amods':
			for pair in o[ 1 ].split( ',' ):
				modname, filename = pair.split( ':' )
				if filename: _flags[ 'ADDITIONAL_MODULES' ][ modname ] = filename
				else: _flags[ 'ADDITIONAL_MODULES' ][ modname ] = None
		elif o[ 0 ] == '--nloc':
			_flags[ 'NONLOCAL' ].extend( o[ 1 ].split( ',' ) )
		elif o[ 0 ] == '--order':
			_flags[ 'INIT_ORDER' ].extend( o[ 1 ].split( ',' ) )
	if args:
		_flags[ 'PY_FILE' ] = args[ 0 ]
		if len( args ) == 2: _flags[ 'C_FILE' ] = args[ 1 ]

# Parses variables in 'Freezefile'
def _parse_vars():
	vars = _flags[ 'FREEZEFILE_VARS' ].keys()
	if 'PY_FILE' in vars:
		_flags[ 'PY_FILE' ] = _flags[ 'FREEZEFILE_VARS' ][ 'PY_FILE' ]
	if 'C_FILE' in vars:
		_flags[ 'C_FILE' ] = _flags[ 'FREEZEFILE_VARS' ][ 'C_FILE' ]
	if 'PROTECTION_KEY' in vars:
		_flags[ 'PROTECTION_KEY' ] = _flags[ 'FREEZEFILE_VARS' ][ 'PROTECTION_KEY' ]
	if 'IGNORE_MISSING' in vars:
		_flags[ 'IGNORE_MISSING' ] = _flags[ 'FREEZEFILE_VARS' ][ 'IGNORE_MISSING' ]
	if 'ADDITIONAL_MODULES' in vars:
		_flags[ 'ADDITIONAL_MODULES' ].update( **_flags[ 'FREEZEFILE_VARS' ][ 'ADDITIONAL_MODULES' ] )
	if 'NONLOCAL' in vars:
		_flags[ 'NONLOCAL' ].extend( _flags[ 'FREEZEFILE_VARS' ][ 'NONLOCAL' ] )

####################################################################################################

def freeze( **args ): # called from other module
	"""\
This function receives named arguments that
tells what modules should be frozen and in
which way.

Required arguments:
 pyfile        - full name of a main module (string)
Optional arguments:
 cfile         - full name of a generated .c file (string)
 key           - protection key (string)
 ignoremissing - ignore missing modules or do not (bool)
 amods         - dictionary containing pairs MODULE_NAME:MODULE_FILE
                 of additonal modules, that can not be detected by
                 introspection
 nonlocal      - list of names of modules that must be treated as
                 non-local and will not be frozen\
"""
	_reset_flags()
	_parse_args( args )
	_analize_flags()

def _main(): # called from a command line
	try:
		_reset_flags()
		if len( sys.argv ) == 1:
			filename = os.path.join( _flags[ 'LOCATION' ], 'Freezefile' )
			if os.path.exists( filename ):
				execfile( filename, _flags[ 'FREEZEFILE_VARS' ] )
				_parse_vars()
			else: raise FreezerError( "cannot stat 'Freezefile'" )
		else: _parse_cmd()
		_analize_flags()
		sys.exit( 0 )
	except Exception, err:
		sys.stderr.write( '%s: %s\n' % ( sys.argv[ 0 ], err ) )
		traceback.print_exc(file=sys.stderr)
		sys.exit( 1 )

if __name__ == '__main__': _main()
