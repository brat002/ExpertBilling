#!/usr/bin/env python2.5
####################################################################################################
"""
General:
--------
This module provides a functionality that allows you
to freeze one or several dependent Python modules in
a single binary executable file which is linked with
Python library, so it can be successfully ran later.

Technique of protection:
------------------------
All given units pass through three steps of freezing
process: marshaling, compressing and encryption with
specified key. After that their code can not be explored
by anyone. But at a startup the last step must be
reversed to allow program run. For this purpose one
additional module also froze into binary code. It is a
simple Python module that implements a function 'getKey'.
This can check whether it's a legal copy of software or
not by using high-level libraries (like WMI) and return
right (or not) string key for decryption.

Dependencies:
-------------
To compile a final file across different platforms the
freezer uses GCC (Dev-C++ under Windows). And it links
program with Python library and zlib. So be sure that
all these installed in your system.
"""
####################################################################################################
_CHUNK_0 = r"""
typedef struct
{
	char          *name;
	unsigned char *code;
	int           size;
} FrozenModule;

static FrozenModule _packed_modules[] = {
"""

_CHUNK_1 = r"""	{ 0 }
};

static FrozenModule _frozen_modules[] = {
"""

_CHUNK_2 = r"""	{ 0 }
};

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <zlib.h>

extern FrozenModule * __attribute__((dllimport)) PyImport_FrozenModules;
extern int __attribute__((dllimport)) Py_NoSiteFlag;
extern int __attribute__((dllimport)) Py_FrozenFlag;

int Py_SetProgramName( char * ) __attribute__((dllimport));
int PySys_SetArgv( int argc, char ** argv ) __attribute__((dllimport));
int PyImport_ImportFrozenModule( char * ) __attribute__((dllimport));
int Py_Initialize() __attribute__((dllimport));
int Py_Finalize() __attribute__((dllimport));
int PyErr_Print() __attribute__((dllimport));
"""

_CHUNK_3 = r"""
static
int
unpackModules()
{
	uLongf out_sz;

	for ( register int idx = 0; _packed_modules[ idx ].name; idx++ ) {
		out_sz = labs( _frozen_modules[ idx ].size );
		if ( !( _frozen_modules[ idx ].code = malloc( out_sz ) ) ) {
			fputs( "error: there is no enough memory\n", stderr );
			return 0;
		}
		if ( uncompress( _frozen_modules[ idx ].code, &out_sz, _packed_modules[ idx ].code, _packed_modules[ idx ].size ) != Z_OK ) {
			fputs( "error: could not unpack bytecode\n", stderr );
			return 0;
		}
	}
	return 1;
}
"""

_CHUNK_4 = r"""
typedef struct PyObject PyObject;

PyObject * PyImport_ExecCodeModule( char * name, PyObject * co ) __attribute__((dllimport));
PyObject * PyObject_CallFunction( PyObject * callable, char * format, ... ) __attribute__((dllimport));
PyObject * PyErr_Occurred() __attribute__((dllimport));
PyObject * PyMarshal_ReadObjectFromString( char * string, int len ) __attribute__((dllimport));
PyObject * PyModule_GetDict( PyObject * module ) __attribute__((dllimport));
PyObject * PyDict_GetItemString( PyObject * p, char * key ) __attribute__((dllimport));

const char * PyString_AsString( PyObject * string ) __attribute__((dllimport));
int PyString_Size( PyObject * string ) __attribute__((dllimport));

void Py_DecRef( PyObject * o ) __attribute__((dllimport));

static
void
decryptBuffer( register char * buf, register int count )
{
	for ( register int idx = 0; idx < count; idx++, buf++ ) {
		*buf = ~*buf;
		*buf = ( *buf & 0x80 ) | ( ( *buf >> 1 ) & 0x20 ) | ( ( *buf >> 2 ) & 0x08 ) | ( ( *buf >> 3 ) & 0x02 ) |
		       ( *buf & 0x01 ) | ( ( *buf << 1 ) & 0x04 ) | ( ( *buf << 2 ) & 0x10 ) | ( ( *buf << 3 ) & 0x40 );
	}
}

static
int
unpackModules()
{
	uLongf in_sz, out_sz;

	in_sz  = sizeof __prot__ - 1;
	out_sz = PROT_BYTECODE_SIZE;
	decryptBuffer( __prot__, in_sz );

	void *code_buf;

	if ( !( code_buf = malloc( PROT_BYTECODE_SIZE ) ) ) goto LBL_MEM_ERR;
	if ( uncompress( code_buf, &out_sz, __prot__, in_sz ) != Z_OK ) {
		fputs( "error: could not unpack bytecode\n", stderr );
		return 0;
	}

	PyObject
		*code = PyMarshal_ReadObjectFromString( code_buf, PROT_BYTECODE_SIZE ),
		*module = PyImport_ExecCodeModule( "__prot__", code ),
		*str  = PyObject_CallFunction( PyDict_GetItemString( PyModule_GetDict( module ), "getKey" ), NULL );

	Py_DecRef( code );
	Py_DecRef( module );
	free( code_buf );

	const char *key = PyString_AsString( str );
	int        key_len  = PyString_Size( str );

	if ( PyErr_Occurred() ) {
		PyErr_Print();
		return 0;
	}
	for ( register int idx = 0; _packed_modules[ idx ].name; idx++ ) {
		if ( ( in_sz = _packed_modules[ idx ].size ) % ( key_len + 1 ) ) {
			fputs( "error: invalid key length\n"
			       "This is illegal copy of program\n", stderr );
			return 0;
		}
		decryptBuffer( _packed_modules[ idx ].code, in_sz );
		{
			int
				count = _packed_modules[ idx ].size / ( key_len + 1 ),
				i = 1;
			register char
				*dest = _packed_modules[ idx ].code + key_len,
				*src  = dest + 1;

			while ( i < count ) {
				memcpy( dest, src, key_len );
				i++;
				dest += key_len;
				src += key_len + 1;
			}
		}
		for ( register int i = 0, j = 0; i < in_sz; i++, j++ ) {
			if ( j == key_len ) j = 0;
			_packed_modules[ idx ].code[ i ] ^= key[ j ];
		}
		out_sz = labs( _frozen_modules[ idx ].size );
		if ( !( _frozen_modules[ idx ].code = malloc( out_sz ) ) ) goto LBL_MEM_ERR;
		if ( uncompress( _frozen_modules[ idx ].code, &out_sz, _packed_modules[ idx ].code, in_sz ) != Z_OK ) {
			fputs( "error: could not unpack bytecode\n"
			       "File is damaged or you're using illegal copy of program\n", stderr );
			return 0;
		}
	}
	Py_DecRef( str );
	return 1;
LBL_MEM_ERR:
	fputs( "error: there is no enough memory\n", stderr );
	return 0;
}
"""

_CHUNK_5 = r"""
int main( int argc, char ** argv )
{
	int result = 0;

	Py_NoSiteFlag = Py_FrozenFlag = 1;
	Py_SetProgramName( argv[ 0 ] );
	Py_Initialize();
	PySys_SetArgv( argc, argv );

	if ( !unpackModules() ) {
		Py_Finalize();
		return 1;
	}
	PyImport_FrozenModules = _frozen_modules;
	switch ( PyImport_ImportFrozenModule( "__main__" ) )
	{
	case 0:
		fputs( "error: module '__main__' isn't frozen\n", stderr );
		result = 1;
		break;
	case -1:
		PyErr_Print();
		result = 1;
	}
	Py_Finalize();
	perror( 0 );
	return result;
}
"""

####################################################################################################

import sys, os, os.path, modulefinder

ver = float( sys.version[ : 3 ] )
if ver < 2.5 or ver >= 3.0: raise RuntimeError( 'Python of version 2.x (>=2.5) required' )
del ver

def _resetFlags():
	global _flags
	_flags = {
		'SHOW_HELP': False,        # show help and quit
		'PY_FILE': None,           # name of a .py file for freezing
		'C_FILE': None,            # name of a generated .c file
		'PROTECTION_MODULE': None, # name of a protection file with function 'getKey()'
		'PROTECTION_KEY': None,       # protection key for encryption
		'IGNORE_MISSING': False,      # ignore missing modules
		'FREEZE_LOCAL': False,        # freeze local modules used by main
		'SEARCH_PATH': None,          # path to search local modules
		'ADDITIONAL_MODULES': {},     # additional modules that will be freezed
		'NONLOCAL': [],               # treat listed modules/packages as non-local, even if they are in the (sub)directory of a main unit
		'LOCATION': os.getcwd() + os.sep, # current working directory
		'COMPILE': True,                  # compile result
		'DEV_CPP_DIR': 'C:\\Dev-Cpp\\',   # path to Dev-C++ (Windows only)
		'STAND_ALONE': False,      # make program independent (copy required Python modules)
		'SCRIPT_DIR': os.path.dirname( sys.modules[ __name__ ].__file__ ), # location of this script
		'FREEZEFILE_VARS': {},     # variables in Freezefile
	}

_USAGE = r"""
Usage: freezer [options] [PY_FILE [C_FILE ]]
 Freezes Python module and creates binary
 executable with optional anti-copy protection.
Options:
  -h,     --help         show this message and quit
  -k KEY, --pkey=KEY     use protection KEY for encryption
  -m MOD, --pmod=MOD     use module MOD as protection unit.
                         This file must implement function
                         'getKey' which returns a string
  -l                     freeze local program modules
  --amods=MODS           include additional modules MODS that
                         cannot be found by introspection.
                         MODS are separated by commas pairs
                         MODNAME:FILENAME (for example
                         --amods='pkg.io:io.py,data:data.py')
  -g                     generate .c file only - do not compile
  -d DIR                 specify a directory where Dev-C++ is
                         installed (Windows only; by default
                         is 'C:\Dev-Cpp\')
  -a                     make a stand-alone program, i.e. copy all
                         required modules to local directory 'modules'
  -i                     ignore missing modules
 Without any arguments freezer attempts to locate and
 execute file 'Freezefile' in the current directory.
Freezefile variables:
  PY_FILE            - name of a main module (str)
  C_FILE             - name of generated .c file (str)
  PROTECTION_KEY     - key for encryption (str)
  PROTECTION_MODULE  - name of a protection module (str)
  IGNORE_MISSING     - ignore missing modules (bool)
  FREEZE_LOCAL       - include local modules to the freezing (bool)
  NONLOCAL           - treat listed modules/packages as non-local even
                       if they are in the (sub)directory of a main unit
  ADDITIONAL_MODULES - modules that also must be froze (dict)
  COMPILE            - compile program at last or not (bool)
  STAND_ALONE        - copy shared modules into local directory
                       or not (bool)
Note:
 Never place modules used by a protection module in the directory
 (or subdirectory) where a main module locates! If you are building
 a program with an option '-l' - they will be encrypted yet at a time
 when the protection unit executed - you will get a segmentation fault.
"""

####################################################################################################

class FreezerError( RuntimeError ): pass

# Compiles a file 'filename' and returns bytecode
def _dumpCode( code ):
	import marshal
	return marshal.dumps( code )

# Compresses given 'bytecode' with zlib
def _packBytecode( bytecode ):
	import zlib
	result = zlib.compress( bytecode, zlib.Z_BEST_COMPRESSION )
	print( 'Compressing bytecode %d -> %d' % ( len( bytecode ), len( result ) ) )
	return result

# Returns a list containing segments of 'string' -
# each has length 'seg_len'
def _splitString( string, seg_len ):
	result = []
	import math
	si, di = 0, seg_len
	for i in xrange( int( math.ceil( float( len( string ) ) / seg_len ) ) ):
		result.append( string[ si : di ] )
		si += seg_len
		di += seg_len
	return result

# Returns encrypted version of 'string'
# Bit-encryption algorithm: 76543210 -> ~(75316420)
# If 'key' is specified - it will be used for
# first-rate encryption of given string
def _encryptString( string, key = None ):
	if key:
		tmp = string
		string = ''
		# encrypting each character in chunk with corresponding character from key
		for s in _splitString( tmp, len( key ) ):
			#print( _representString( s ) )
			for ch, mask in zip( s, key ):
				string += chr( 0xff & ( ord( ch ) ^ ord( mask ) ) ) # simple, but effective encoding
	result = ''
	for ch in string:
		ch = ord( ch )
		result += chr( 0xff & ~(
			( ch & 0x80 ) | ( ( ch << 1 ) & 0x40 ) | ( ( ch << 2 ) & 0x20 ) | ( ( ch << 3 ) & 0x10 ) | \
			( ch & 0x01 ) | ( ( ch >> 1 ) & 0x02 ) | ( ( ch >> 2 ) & 0x04 ) | ( ( ch >> 3 ) & 0x08 )
		))
	return result

# Writes frozen in 'string' module to file 'f'
def _writeToFile( file, string, arr_name ):
	def representString( string ):
		result = '"'
		for ch in string: result += '\\x%02X' % ord( ch )
		return result + '"'
	file.write( '\nstatic char %s[] =\n' % arr_name )
	for s in _splitString( string, 16 ):
		file.write( '\t%s\n' % representString( s ) )
	file.write( ';\n' )

# Compiles .c file to executable
def _makeBinary():
	inc_dir = os.path.join( _flags[ 'SCRIPT_DIR' ], 'include' )
	import distutils.sysconfig
	extra_opts = distutils.sysconfig.get_config_var( 'LINKFORSHARED' )
	extra_opts = extra_opts if extra_opts else ''
	args = {
		'CC': os.path.join( _flags[ 'DEV_CPP_DIR' ], 'bin\\gcc.exe' ),
		'CFLAGS': '-std=gnu99 -O3 -I"%s" -I"%s"' % (
			os.path.join( _flags[ 'DEV_CPP_DIR' ], 'include' ),
			inc_dir
		),
		'SRC': _flags[ 'C_FILE' ],
		'LFLAGS': '-L"%s" -L"%s" -L"%s" -lpython%s -lzlib1 %s' % (
			os.path.join( _flags[ 'DEV_CPP_DIR' ], 'lib' ),
			os.path.join( _flags[ 'SCRIPT_DIR' ], 'lib' ),
			os.path.join( os.getenv( 'windir' ), 'system32' ),
			sys.version[ : 3 ].replace( '.', '' ),
			extra_opts
		),
		'TARGET': _flags[ 'C_FILE' ][ : -1 ] + 'exe',
	} if sys.platform == 'win32' else {
		'CC': 'gcc',
		'CFLAGS': '-std=gnu99 -O3 -I"%s"' % inc_dir,
		'SRC': _flags[ 'C_FILE' ],
		'LFLAGS': '-lpython%s -lz -Wl,-rpath=./ %s' % (
			sys.version[ : 3 ],
			extra_opts
		),
		'TARGET': _flags[ 'C_FILE' ][ : -2 ],
	}
	cmd = '%(CC)s %(CFLAGS)s %(SRC)s %(LFLAGS)s -o %(TARGET)s' % args
	print( '==================================================' )
	print( 'Compiling: ' + cmd )
	if os.system( cmd ): raise OSError( 'can not compile program' )
	if sys.platform != 'win32':
		cmd = 'strip %(TARGET)s' % args
		print( '==================================================' )
		print( 'Stripping: ' + cmd )
		if os.system( cmd ): raise OSError( 'can not strip program' )

# Reads and compiles a content of a file
def _compileFile( filename ):
	f = open( filename )
	text = f.read()
	f.close()
	return compile( text, '', 'exec' )

# Tries to find modules that modulefinder did not
def _findModules( mods_names, modules ):
	print( '==================================================' )
	print( 'Looking for modules:' )
	def getDependencies( mod_name, file_name ):
		mf = modulefinder.ModuleFinder()
		mf.run_script( file_name )
		m = mf.modules[ '__main__' ]
		m.__name__ = mod_name
		mf.modules[ mod_name ] = m
		del mf.modules[ '__main__' ]
		modules.update( mf.modules )
	def findOne( mod_name, search_path = None ):
		print( "-> %s" % mod_name )
		base_name = mod_name.replace( '.', os.path.sep )
		EXTENSIONS = ( '.py', '.pyc', '.pyd' if sys.platform == 'win32' else '.so' )
		for path in ( ( sys.path + [ os.path.abspath( _flags[ 'SEARCH_PATH' ] ) ] ) if not search_path else ( search_path, ) ):
			for rest in ( '__init__.py', '__init__.pyc' ):
				file_name = os.path.join( path, base_name, rest )
				if os.path.exists( file_name ):
					search_path = path
					break
			else:
				for ext in EXTENSIONS:
					file_name = os.path.join( path, base_name + ext )
					if os.path.exists( file_name ):
						search_path = path
						break
				else: continue
			break
		else: return False
		if '.' in mod_name: # compoud package - looking for parent
			if not findOne( mod_name[ : mod_name.rindex( '.' ) ], search_path ): return False
		print( ' : ' + file_name )
		if file_name.endswith( EXTENSIONS[ 2 ] ): modules[ mod_name ] = modulefinder.Module( mod_name, file_name )
		else: getDependencies( mod_name, file_name )
		return True
	for mod_name in mods_names:
		if findOne( mod_name ): del mods_names[ mods_names.index( mod_name ) ]

# Returns loaded modules
def _getModules():
	mf = modulefinder.ModuleFinder( [ _flags[ 'SEARCH_PATH' ] ], False, sys.path + [ _flags[ 'SEARCH_PATH' ] ] )
	missing = []
	for mod_name, file_name in _flags[ 'ADDITIONAL_MODULES' ].iteritems():
		if not file_name: missing.append( mod_name )
		elif not file_name.endswith( '.so' ) and not file_name.endswith( '.pyd' ):
			mf.run_script( file_name )
			m = mf.modules[ '__main__' ]
			m.__name__ = mod_name
			mf.modules[ mod_name ] = m
			del mf.modules[ '__main__' ]
	mf.run_script( _flags[ 'PY_FILE' ] )
	missing.extend( mf.any_missing() )
	_findModules( missing, mf.modules )
	if missing:
		if _flags[ 'IGNORE_MISSING' ]:
			print( '==================================================' )
			print( 'WARNING: missing modules %r' % missing )
		else: raise FreezerError( "missing modules %r" % missing )
	print( '==================================================' )
	print( 'Loading modules:' )
	for m in mf.modules.itervalues():
		print( '-> %s\n : %s' % ( m.__name__, m.__file__ ) )
	result = [ mf.modules[ '__main__' ] ]
	if _flags[ 'FREEZE_LOCAL' ]:
		for m in mf.modules.itervalues():
			if ( not m.__file__ or m.__name__ == '__main__' ): continue
			if m.__file__.startswith( _flags[ 'SEARCH_PATH' ] ) and m.__name__.split( '.' )[ 0 ] not in _flags[ 'NONLOCAL' ]:
				if not m.__code__: raise FreezerError( "can not freeze binary module '%s' in '%s'" % ( m.__name__, m.__file__ ) )
				result.append( m )
	print( '==================================================' )
	print( 'Selecting modules for freezing:' )
	for m in result:
		print( '-> %s\n : %s' % ( m.__name__, m.__file__ ) )
	return result

# Creates plain project without any protection
def _createSimple():
	f = open( _flags[ 'C_FILE' ], 'w' )
	mods = _getModules()
	table = []
	print( '==================================================' )
	for m in mods:
		print( "Dumping '%s'" % m.__name__ )
		bytecode = _dumpCode( m.__code__ )
		if m.__name__ == '__main__':
			# we need a way to add a local path: ugly some, but it works
			bytecode = _dumpCode( compile(
"""
import sys, marshal
sys.path[ 0 ] += '%smodules'
exec marshal.loads( %r ) in globals()""" % ( os.path.sep, bytecode ),
				'',
				'exec'
			))
		bc_len = len( bytecode ) # actual size of a bytecode 
		item = [
			m.__name__, # internal name
			'__main__' if m.__name__ == '__main__' else '_mod_' + '$'.join( m.__name__.split( '.' ) ), # variable name
			-bc_len if os.path.basename( m.__file__ ).startswith( '__init__' ) else bc_len # negative size of a compoud package
		]
		bytecode = _packBytecode( bytecode )
		item.append( len( bytecode ) ) # size of packed bytecode
		_writeToFile( f, bytecode, item[ 1 ] )
		table.append( item )
	f.write( _CHUNK_0 )
	for item in table:
		f.write( '\t{ "%s", %s, %d },\n' % ( item[ 0 ], item[ 1 ], item[ 3 ] ) )
	f.write( _CHUNK_1 )
	for item in table:
		f.write( '\t{ "%s", 0, %d },\n' % ( item[ 0 ], item[ 2 ] ) )
	f.write( _CHUNK_2 )
	f.write( _CHUNK_3 )
	f.write( _CHUNK_5 )
	f.close()

# Creates complex project with a protection
def _createAdvanced():
	# adds to bytecode useless data
	def messBytecode( code ):
		ln = len( _flags[ 'PROTECTION_KEY' ] )
		chunks = _splitString( code, ln )
		ln += 1
		import random
		for idx in xrange( len( chunks ) ):
			while len( chunks[ idx ] ) != ln: chunks[ idx ] += chr( 0xff & int( random.random() * 1000 ) )
		result = ''
		for ch in chunks: result += ch
		return result
	#
	f = open( _flags[ 'C_FILE' ], 'w' )
	# packing protection module first
	print( 'Dumping protection module' )
	bytecode = _dumpCode( compile(
"""
import sys, marshal
sys.path[ 0 ] += '%smodules'
exec marshal.loads( %r ) in globals()""" % ( # we need a way to add a local path: ugly some, but it works
			os.path.sep,
			_dumpCode( _compileFile( _flags[ 'PROTECTION_MODULE' ] ) )
		),
		'',
		'exec'
	))
	f.write( '\n#define PROT_BYTECODE_SIZE     %s\n' % len( bytecode ) )
	_writeToFile( f, _encryptString( _packBytecode( bytecode ) ), '__prot__' )
	mods = _getModules()
	table = []
	print( '==================================================' )
	for m in mods:
		print( "Dumping '%s'" % m.__name__ )
		bytecode = _dumpCode( m.__code__ )
		bc_len = len( bytecode ) # actual size of a bytecode 
		item = [
			m.__name__, # internal name
			'__main__' if m.__name__ == '__main__' else '_mod_' + '$'.join( m.__name__.split( '.' ) ), # variable name
			-bc_len if '__init__' in m.__file__ else bc_len # negative size of a compoud package
		]
		bytecode = messBytecode( _encryptString( _packBytecode( bytecode ), _flags[ 'PROTECTION_KEY' ] ) )
		item.append( len( bytecode ) ) # size of packed bytecode
		_writeToFile( f, bytecode, item[ 1 ] )
		table.append( item )
	f.write( _CHUNK_0 )
	for item in table:
		f.write( '\t{ "%s", %s, %d },\n' % ( item[ 0 ], item[ 1 ], item[ 3 ] ) )
	f.write( _CHUNK_1 )
	for item in table:
		f.write( '\t{ "%s", 0, %d },\n' % ( item[ 0 ], item[ 2 ] ) )
	f.write( _CHUNK_2 )
	f.write( _CHUNK_4 )
	f.write( _CHUNK_5 )
	f.close()

# Copies required modules to a local directory 'modules'
def _copyModules():
	def getFilesNames( mod ):
		ext = os.path.splitext( mod.__file__ )[ 1 ] # extension
		return ( 
			mod.__name__.replace( '.', os.path.sep ) + (
				( os.path.sep + '__init__' + ext ) if '__init__' in os.path.basename( mod.__file__ ) else ext
			),
			mod.__file__
		)
	name_pairs = []
	py_dirs = sys.path[ 1 : ]
	#print( sys.path )
	mf = modulefinder.ModuleFinder( [ _flags[ 'SEARCH_PATH' ] ] + py_dirs )
	missing = []
	for mod_name, file_name in _flags[ 'ADDITIONAL_MODULES' ].iteritems():
		if not file_name: missing.append( mod_name )
		elif not file_name.endswith( '.so' ) and not file_name.endswith( '.pyd' ):
			mf.run_script( file_name )
			m = mf.modules[ '__main__' ]
			m.__name__ = mod_name
			mf.modules[ mod_name ] = m
			del mf.modules[ '__main__' ]
		else: mf.modules[ mod_name ] = modulefinder.Module( mod_name, file_name )
	if _flags[ 'PROTECTION_MODULE' ]:
		mf.run_script( _flags[ 'PROTECTION_MODULE' ] )
		del mf.modules[ '__main__' ]
	mf.run_script( _flags[ 'PY_FILE' ] )
	if _flags[ 'PROTECTION_MODULE' ]:
		for m in mf.modules.itervalues():
			if m.__file__ == _flags[ 'PROTECTION_MODULE' ]: del mf.modules[ m.__name__ ]; break
	missing.extend( mf.any_missing() )
	_findModules( missing, mf.modules )
	if missing:
		if _flags[ 'IGNORE_MISSING' ]: print( 'WARNING: missing modules %r' % missing )
		else: raise ImportError( 'missing modules %r' % missing )
	print( '==================================================' )
	print( 'Detecting required modules:' )
	for m in mf.modules.itervalues():
		print( '-> %s\n : %s' % ( m.__name__, m.__file__ ) )
	for mod in mf.modules.itervalues():
		# excluding main and built-in modules
		if ( mod.__name__ == '__main__' or ( not mod.__code__ and not mod.__file__ ) ): continue
		if mod.__file__.startswith( _flags[ 'SEARCH_PATH' ] ): # local module
			if ( not _flags[ 'FREEZE_LOCAL' ] or mod.__name__.split( '.' )[ 0 ] in _flags[ 'NONLOCAL' ] ): name_pairs.append( getFilesNames( mod ) )
			continue
		loc = ''
		for d in py_dirs:
			if d in mod.__file__ and len( d ) > len( loc ): loc = d # finding the longest prefix (directory name)
		if loc: name_pairs.append( ( mod.__file__.replace( loc + os.path.sep, '' ), mod.__file__ ) )
		else: name_pairs.append( getFilesNames( mod ) )
	del mf
	out_dir = os.path.dirname( _flags[ 'C_FILE' ] )
	mod_dir = os.path.join( out_dir, 'modules' ) # target directory
	command = 'copy /Y' if sys.platform == 'win32' else 'cp'
	print( '==================================================' )
	for p in name_pairs:
		dest_dir = os.path.join( mod_dir, os.path.dirname( p[ 0 ] ) )
		if not os.path.exists( dest_dir ): os.makedirs( dest_dir )
		dest_file = os.path.join( mod_dir, p[ 0 ] )
		if (
			( not dest_file.endswith( '.py' ) and not os.path.exists( dest_file ) ) or
			( dest_file.endswith( '.py' ) and not os.path.exists( dest_file + 'c' ) )
		): # if module is not copied and compiled yet
			print( 'Copying %s\n     to %s' % ( p[ 1 ], dest_file ) )
			if os.system( "%s \"%s\" \"%s\"" % ( command, p[ 1 ], dest_file ) ): raise OSError( 'can not copy file' )
	def copy( cmd, dest_file ):
		if not os.path.exists( dest_file ):
			print( 'Copying: ' + cmd )
			if os.system( cmd ): raise OSError( 'can not copy file' )
	if sys.platform == 'win32':
		dest_file = os.path.join( out_dir, "zlib1.dll" )
		copy( 'copy /Y "%s" "%s"' % (
			os.path.join( _flags[ 'SCRIPT_DIR' ], "lib", "zlib1.dll" ),
			dest_file
		), dest_file )
		py_lib = 'python%s.dll' % sys.version[ : 3 ].replace( '.', '' )
		dest_file = os.path.join( out_dir, py_lib )
		copy( 'copy /Y "%s" "%s"' % (
			os.path.join( os.getenv( 'windir' ), "system32", py_lib ),
			dest_file
		), dest_file )
	else:
		dest_file = os.path.join( out_dir, "libz.so" )
		src_file = '/usr/lib/libz.so'
		if not os.path.exists( src_file ): src_file = '/usr/local/lib/libz.so'
		copy( 'cp %s "%s"' % ( src_file, dest_file ), dest_file )
		py_lib = 'libpython%s.so' % sys.version[ : 3 ]
		src_file = '/usr/lib/' + py_lib
		if not os.path.exists( src_file ): src_file = '/usr/local/lib/' + py_lib
		dest_file = os.path.join( out_dir, py_lib )
		copy( 'cp %s "%s"' % ( src_file, dest_file ), dest_file )
	print( '==================================================' )
	import compileall
	compileall.compile_dir( mod_dir )
	print( '==================================================' )
	print( 'Cleaning up...' )
	for p in name_pairs:
		file_name = os.path.join( mod_dir, p[ 0 ] )
		if file_name.endswith( '.py' ) and os.path.exists( file_name ): os.remove( file_name )

# Analizes flags
def _analizeFlags():
	if _flags[ 'SHOW_HELP' ]:
		print( _USAGE )
		sys.exit( 0 )
	if not _flags[ 'PY_FILE' ]: raise FreezerError( 'missing main module' )
	_flags[ 'PY_FILE' ] = _flags[ 'PY_FILE' ].replace( '/', os.path.sep )
	# fixing local path
	path = os.path.dirname( _flags[ 'PY_FILE' ] )
	if path: _flags[ 'SEARCH_PATH' ] = path
	else: _flags[ 'SEARCH_PATH' ] = '.' + os.path.sep
	del path
	# normalizing files names of files
	def normalizePath( path ):
		path = path.replace( '/', os.path.sep )
		d = os.path.dirname( path )
		# checking for reference to current directory
		if d == '.' or d == '..':
			path = os.path.normpath( os.path.join( _flags[ 'LOCATION' ], path ) ) # converting to an absolute path relativelly to CWD
		elif sys.platform == 'win32':
 			if path[ 0 ] == '\\': raise ValueError( 'invalid path "%s": drive letter expected' % path )
			if not os.path.splitdrive( path )[ 0 ]: path = os.path.join( _flags[ 'SEARCH_PATH' ], path )
		else:
			if path[ 0 ] != '/': path = os.path.join( _flags[ 'SEARCH_PATH' ], path )
		return path
	if not _flags[ 'C_FILE' ]: _flags[ 'C_FILE' ] = _flags[ 'PY_FILE' ][ : -2 ] + 'c'
	_flags[ 'C_FILE' ] = normalizePath( _flags[ 'C_FILE' ] )
	if sys.platform == 'win32': _flags[ 'DEV_CPP_DIR' ] = normalizePath( _flags[ 'DEV_CPP_DIR' ] )
	out_dir = os.path.dirname( _flags[ 'C_FILE' ] )
	if not os.path.exists( out_dir ): os.makedirs( out_dir )
	mods = _flags[ 'ADDITIONAL_MODULES' ]
	for k, v in mods.iteritems():
		if v: mods[ k ] = normalizePath( v )
	if _flags[ 'PROTECTION_MODULE' ]: _flags[ 'PROTECTION_MODULE' ] = normalizePath( _flags[ 'PROTECTION_MODULE' ] )
	# cheking for protection flags
	if not _flags[ 'PROTECTION_KEY' ] and not _flags[ 'PROTECTION_MODULE' ]:
		_createSimple()
	elif _flags[ 'PROTECTION_KEY' ] and _flags[ 'PROTECTION_MODULE' ]:
		_createAdvanced()
	elif not _flags[ 'PROTECTION_KEY' ]:
		raise FreezerError( 'missing protection key' )
	else:
		raise FreezerError( 'missing protection module' )
	if _flags[ 'COMPILE' ]: _makeBinary()
	if _flags[ 'STAND_ALONE' ]: _copyModules()
	print( '==================================================' )
	print( 'Done!' )

# Analizes given arguments
def _parseArguments( args ):
	if 'py_file' in args:
		_flags[ 'PY_FILE' ] = args[ 'py_file' ]
	if 'c_file' in args:
		_flags[ 'C_FILE' ] = args[ 'c_file' ]
	if 'pkey' in args:
		_flags[ 'PROTECTION_KEY' ] = args[ 'pkey' ]
	if 'pmod' in args:
		_flags[ 'PROTECTION_MODULE' ] = args[ 'pmod' ]
	if 'ignore_missing' in args:
		_flags[ 'IGNORE_MISSING' ] = args[ 'ignore_missing' ]
	if 'local' in args:
		_flags[ 'FREEZE_LOCAL' ] = args[ 'local' ]
	if 'compile' in args:
		_flags[ 'COMPILE' ] = args[ 'compile' ]
	if 'dev_cpp_dir' in args:
		_flags[ 'DEV_CPP_DIR' ] = args[ 'dev_cpp_dir' ]
	if 'stand_alone' in args:
		_flags[ 'STAND_ALONE' ] = args[ 'stand_alone' ]

# Gets options from command line
def _parseCommandLine():
	import getopt
	opts, args = getopt.getopt(
		sys.argv[ 1 : ],
		'hk:m:ilo:gd:a',
		[ 'help', 'pkey=', 'pmod=', 'amods=' ]
	)
	for o in opts:
		if   o[ 0 ] == '-h' or o[ 0 ] == '--help' :
			_flags[ 'SHOW_HELP' ] = True
		elif o[ 0 ] == '-k' or o[ 0 ] == '--pkey':
			_flags[ 'PROTECTION_KEY' ] = o[ 1 ]
		elif o[ 0 ] == '-m' or o[ 0 ] == '--pmod':
			_flags[ 'PROTECTION_MODULE' ] = o[ 1 ]
		elif o[ 0 ] == '-i':
			_flags[ 'IGNORE_MISSING' ] = True
		elif o[ 0 ] == '-l':
			_flags[ 'FREEZE_LOCAL' ] = True
		elif o[ 0 ] == '-g':
			_flags[ 'COMPILE' ] = False
		elif o[ 0 ] == '-d':
			_flags[ 'DEV_CPP_DIR' ] = o[ 1 ]
		elif o[ 0 ] == '-a':
			_flags[ 'STAND_ALONE' ] = True
		elif o[ 0 ] == '--amods':
			for pair in o[ 1 ].split( ',' ):
				modname, filename = pair.split( ':' )
				_flags[ 'ADDITIONAL_MODULES' ][ modname ] = filename if filename else None
	if args:
		_flags[ 'PY_FILE' ] = args[ 0 ]
		if len( args ) == 2: _flags[ 'C_FILE' ] = args[ 1 ]

# Parses variables in 'Freezefile'
def _parseVariables():
	vars = _flags[ 'FREEZEFILE_VARS' ].keys()
	if 'PY_FILE' in vars:
		_flags[ 'PY_FILE' ] = _flags[ 'FREEZEFILE_VARS' ][ 'PY_FILE' ]
	if 'C_FILE' in vars:
		_flags[ 'C_FILE' ] = _flags[ 'FREEZEFILE_VARS' ][ 'C_FILE' ]
	if 'PROTECTION_KEY' in vars:
		_flags[ 'PROTECTION_KEY' ] = _flags[ 'FREEZEFILE_VARS' ][ 'PROTECTION_KEY' ]
	if 'PROTECTION_MODULE' in vars:
		_flags[ 'PROTECTION_MODULE' ] = _flags[ 'FREEZEFILE_VARS' ][ 'PROTECTION_MODULE' ]
	if 'IGNORE_MISSING' in vars:
		_flags[ 'IGNORE_MISSING' ] = _flags[ 'FREEZEFILE_VARS' ][ 'IGNORE_MISSING' ]
	if 'FREEZE_LOCAL' in vars:
		_flags[ 'FREEZE_LOCAL' ] = _flags[ 'FREEZEFILE_VARS' ][ 'FREEZE_LOCAL' ]
	if 'ADDITIONAL_MODULES' in vars:
		_flags[ 'ADDITIONAL_MODULES' ] = _flags[ 'FREEZEFILE_VARS' ][ 'ADDITIONAL_MODULES' ]
	if 'NONLOCAL' in vars:
		_flags[ 'NONLOCAL' ] = _flags[ 'FREEZEFILE_VARS' ][ 'NONLOCAL' ]
	if 'COMPILE' in vars:
		_flags[ 'COMPILE' ] = _flags[ 'FREEZEFILE_VARS' ][ 'COMPILE' ]
	if 'STAND_ALONE' in vars:
		_flags[ 'STAND_ALONE' ] = _flags[ 'FREEZEFILE_VARS' ][ 'STAND_ALONE' ]
	_flags[ 'FREEZEFILE_VARS' ] = {}

####################################################################################################

def freeze( **args ): # called from other module
	"""
This function receives named arguments that
tells what modules should be freezed and in
which way.

Required arguments:
 py_file        - full name of a main module (executed at startup)
Optional arguments:
 c_file         - full name of generated .c file (by default equals to
                  'py_file' name with replaced extension to .c. The base
                  name is used as a program name)
 pkey           - string value of protection key (must be coupled with 'pmod')
 pmod           - name of module that implements function 'getKey'
 ignore_missing - ignore missing modules (bool)
 local          - boolean value that enables/disables freezing of
                  dependent local modules ('False' by default)
 amods          - dictionary containing pairs MODULE_NAME:MODULE_FILE
                  of additonal modules, which cannot be detected by
                  introspection
 compile        - boolean value that enables/disables compilation of
                  generated file ('True' by default)
 stand_alone    - make program independent by copying required modules
                  from system directories to local 'modules' (defaults to 'False')
 dev_cpp_dir    - specify a directory where Dev-C++ is installed
                  (Windows only, defaults to 'C:\\Dev-Cpp\\')
Note:
 Never place modules used by a protection module in the directory
 (or subdirectory) where a main module locates! If you are building
 a program with 'local = True' - they will be encrypted yet at a time
 when the protection unit executed - you will get a segmentation fault.
"""
	_resetFlags()
	_parseArguments( args )
	_analizeFlags()

def _main(): # called from command line
	try:
		_resetFlags()
		if len( sys.argv ) == 1:
			filename = os.path.join( _flags[ 'LOCATION' ], 'Freezefile' )
			if os.path.exists( filename ):
				execfile( filename, _flags[ 'FREEZEFILE_VARS' ] )
				_parseVariables()
			else: raise FreezerError( "cannot stat 'Freezefile'" )
		else: _parseCommandLine()
		_analizeFlags()
		sys.exit( 0 )
	except Exception, err:
		print( sys.argv[ 0 ] + ': ' + str( err ) )
		sys.exit( 1 )

if __name__ == '__main__': _main()
