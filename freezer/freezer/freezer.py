#!/usr/bin/env python
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
#include <malloc.h>
#include <zlib.h>

#if defined UNDER_MUSTDIE
# define DLL_IMPORT     __declspec(dllimport)
#else
# define DLL_IMPORT
#endif
"""

_CHUNK_3 = r"""
DLL_IMPORT FrozenModule *PyImport_FrozenModules;

DLL_IMPORT int Py_SetProgramName( char * );
DLL_IMPORT int PySys_SetArgv( int argc, char ** argv );
DLL_IMPORT int PyImport_ImportFrozenModule( char * );
DLL_IMPORT int Py_Initialize();
DLL_IMPORT int Py_Finalize();
DLL_IMPORT int PyErr_Print();

DLL_IMPORT int Py_FrozenFlag;
DLL_IMPORT int Py_NoSiteFlag;
DLL_IMPORT int Py_IgnoreEnvironmentFlag;
DLL_IMPORT int Py_OptimizeFlag;

static
int
unpackBytecode()
{
	uLongf out_sz;
	register idx = 0;

	for ( ; _packed_modules[ idx ].name; idx++ ) {
		out_sz = _frozen_modules[ idx ].size;
		if ( !( _frozen_modules[ idx ].code = malloc( out_sz ) ) ) {
			fputs( "error: there is no enough memory\n", stderr );
			return 0;
		}
		if ( uncompress( _frozen_modules[ idx ].code, &out_sz, _packed_modules[ idx ].code, _packed_modules[ idx ].size ) != Z_OK ) {
			fputs( "error: could not unpack bytecode\n", stderr );
			return 0;
		}
	}
	PyImport_FrozenModules = _frozen_modules;
	return 1;
}

int main( int argc, char ** argv )
{
	int result = 0;

	Py_NoSiteFlag = 1;
	Py_FrozenFlag = 1;
	Py_IgnoreEnvironmentFlag = 1;
	Py_OptimizeFlag = 1;
	Py_SetProgramName( argv[ 0 ] );
	Py_Initialize();
	PySys_SetArgv( argc, argv );

	if ( !unpackBytecode() ) {
		Py_Finalize();
		return 1;
	}
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
	return result;
}
"""

_CHUNK_4 = r"""
typedef struct PyObject PyObject;

DLL_IMPORT FrozenModule *PyImport_FrozenModules;

DLL_IMPORT int Py_SetProgramName( char * );
DLL_IMPORT int PySys_SetArgv( int argc, char ** argv );

DLL_IMPORT int PyImport_ImportFrozenModule( char * );
DLL_IMPORT PyObject * PyImport_ExecCodeModuleEx( char * name, PyObject * co, char * pathname );

DLL_IMPORT int PyErr_Print();
DLL_IMPORT int Py_Initialize();
DLL_IMPORT int Py_Finalize();

DLL_IMPORT int Py_FrozenFlag;
DLL_IMPORT int Py_NoSiteFlag;
DLL_IMPORT int Py_IgnoreEnvironmentFlag;
DLL_IMPORT int Py_OptimizeFlag;

DLL_IMPORT PyObject * PyObject_CallFunction( PyObject * callable, char * format, ... );
DLL_IMPORT PyObject * PyErr_Occurred();

DLL_IMPORT PyObject * PyMarshal_ReadObjectFromString( char * string, int len );
DLL_IMPORT PyObject * PyModule_GetDict( PyObject * module );
DLL_IMPORT PyObject * PyDict_GetItemString( PyObject * p, char * key );

DLL_IMPORT const char * PyString_AsString( PyObject * string );
DLL_IMPORT int PyString_Size( PyObject * string );

DLL_IMPORT void Py_DecRef( PyObject * o );

static
void
decryptBuffer( register char * buf, register int count )
{
	register idx;

	for ( idx = 0; idx < count; idx++, buf++ ) {
		*buf = ~*buf;
		*buf = ( *buf & 0x80 ) | ( ( *buf >> 1 ) & 0x20 ) | ( ( *buf >> 2 ) & 0x08 ) | ( ( *buf >> 3 ) & 0x02 ) |
		       ( *buf & 0x01 ) | ( ( *buf << 1 ) & 0x04 ) | ( ( *buf << 2 ) & 0x10 ) | ( ( *buf << 3 ) & 0x40 );
	}
}

static
int
unpackBytecode()
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
		*module = PyImport_ExecCodeModuleEx( "prot", code, "" ),
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

	register idx;

	for ( idx = 0; _packed_modules[ idx ].name; idx++ ) {
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

		register i, j;

		for ( i = 0, j = 0; i < in_sz; i++, j++ ) {
			if ( j == key_len ) j = 0;
			_packed_modules[ idx ].code[ i ] ^= key[ j ];
		}
		out_sz = _frozen_modules[ idx ].size;
		if ( !( _frozen_modules[ idx ].code = malloc( out_sz ) ) ) goto LBL_MEM_ERR;
		if ( uncompress( _frozen_modules[ idx ].code, &out_sz, _packed_modules[ idx ].code, in_sz ) != Z_OK ) {
			fputs( "error: could not unpack bytecode\n"
			       "File is damaged or you're using illegal copy of program\n", stderr );
			return 0;
		}
	}
	Py_DecRef( str );
	PyImport_FrozenModules = _frozen_modules;
	return 1;
LBL_MEM_ERR:
	fputs( "error: there is no enough memory\n", stderr );
	return 0;
}

int main( int argc, char ** argv )
{
	int result = 0;

	Py_NoSiteFlag = 1;
	Py_FrozenFlag = 1;
	Py_IgnoreEnvironmentFlag = 1;
	Py_OptimizeFlag = 1;
	Py_SetProgramName( argv[ 0 ] );
	Py_Initialize();
	PySys_SetArgv( argc, argv );

	if ( !unpackBytecode() ) {
		Py_Finalize();
		return 1;
	}
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
	return result;
}
"""

####################################################################################################

import sys, os, os.path

_flags = {
	'SHOW_HELP': False,           # show help and quit
	'PY_FILE': None,              # name of a .py file for freezing
	'C_FILE': None,               # name of a generated .c file
	'PROTECTION_MODULE': None,    # name of a protection file with function 'getKey()'
	'PROTECTION_KEY': None,       # protection key for encryption
	'FREEZE_LOCAL': False,        # freeze local modules used by main
	'SEARCH_PATH': None,          # path to search local modules
	'ADDITIONAL_MODULES': {},     # additional modules that will be freezed
	'LOCATION': None,             # path where Freezefile is located
	'COMPILE': True,              # compile result
	'DEV_CPP_DIR': 'C:/Dev-Cpp/', # path to Dev-C++ (Windows only)
}

_USAGE = r"""
Usage: freezer [options] [PY_FILE]
 Freezes Python module and creates binary
 executable with optional anti-copy protection.
Options:
 -h,     --help         show this message and quit
 -k KEY, --pkey=KEY     use protection KEY for encryption
 -m MOD, --pmod=MOD     use module MOD as protection unit.
                        This file must implement function
                        'getKey' which returns a string
 -l,     --local        freeze local (not in sys.path) modules
                        that imported from main (and so on)
 --amods=MODS           freeze additional modules MODS that
                        cannot be found by introspection.
                        MODS are separated by commas pairs
                        MODNAME:FILENAME (for example
                        --amods=pkg.io:io.py,data:data.py)
 -o FILENAME            name of generated .c file
 -g                     generate .c file only - do not compile
 -d DIR                 specify a directory where Dev-C++ is
                        installed (Windows only; by default
                        is 'C:/Dev-Cpp/')
Without any arguments freezer attempts to locate and
execute file 'Freezefile' in current directory."""

class FreezerError( RuntimeError ): pass

# Compiles a file 'filename' and returns bytecode
def _dumpCode( code ):
	import marshal
	return marshal.dumps( code )

# Compresses given 'bytecode' with zlib
def _packBytecode( bytecode ):
	import zlib
	result = zlib.compress( bytecode, zlib.Z_BEST_COMPRESSION )
	print( 'Compressing bytecode:\n\t%d -> %d' % ( len( bytecode ), len( result ) ) )
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
		) )
	return result

# Returns a C-string enclosed in "", where every
# original character present in hex mode '\x<hexcode>'
def _representString( string ):
	result = '"'
	for ch in string: result += '\\x%02X' % ord( ch )
	return result + '"'

# Writes frozen in 'string' module to file 'f'
def _writeToFile( f, string, arr_name ):
	f.write( '\nstatic char %s[] =\n' % arr_name )
	for s in _splitString( string, 16 ):
		f.write( '\t%s\n' % _representString( s ) )
	f.write( ';\n' )

# Compiles file 'filename' to executable
def _makeBinary():
	if sys.platform == 'win32':
		flags = {
			'CC': _flags[ 'DEV_CPP_DIR' ] + 'bin/gcc.exe',
			'CFLAGS': '-DUNDER_MUSTDIE -I"%s"' % ( _flags[ 'DEV_CPP_DIR' ] + 'include' ),
			'SRC': _flags[ 'C_FILE' ],
			'LFLAGS': '-L"%s" -lpython%s -lzlib' % ( _flags[ 'DEV_CPP_DIR' ] + 'lib', sys.version[ : 3 ] ),
			'TARGET': _flags[ 'C_FILE' ][ : -1 ] + 'exe',
		}
	else:
		flags = {
			'CC': 'gcc',
			'CFLAGS': '',
			'SRC': _flags[ 'C_FILE' ],
			'LFLAGS': '-lpython%s -lz' % sys.version[ : 3 ],
			'TARGET': _flags[ 'C_FILE' ][ : -2 ]
		}
	cmd = '%(CC)s %(CFLAGS)s %(SRC)s %(LFLAGS)s -o %(TARGET)s' % flags
	print( 'Compiling:\n\t' + cmd )
	os.system( cmd )

def _readFile( filename ):
	f = open( filename )
	result = f.read()
	f.close()
	return result

# Returns loaded modules
def _getModules():
	import modulefinder
	mf = modulefinder.ModuleFinder( _flags[ 'SEARCH_PATH' ], False, sys.path )
	mf.run_script( _flags[ 'PY_FILE' ] )
	result = mf.modules
	del mf
	if not _flags[ 'FREEZE_LOCAL' ]: result = { '__main__' : result[ '__main__' ] }
	for modname, filename in _flags[ 'ADDITIONAL_MODULES' ].iteritems():
		m = modulefinder.Module( modname, filename )
		m.__code__ = compile( _readFile( filename ), '', 'exec' )
		result[ modname ] = m
	return result

def _createSimple():
	f = open( _flags[ 'C_FILE' ], 'w' )
	mods = _getModules()
	table = []
	for name in reversed( mods.keys() ):
		m = mods[ name ]
		if m.__code__: # preventing dumping of built-in modules
			print( "Dumping '%s'" % name )
			bytecode = _dumpCode( m.__code__ )
			item = [
				name, # internal name
				'__main__' if name == '__main__' else '_mod_' + '__'.join( name.split( '.' ) ), # variable name
				len( bytecode ) # actual size of a bytecode
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
	f.close()
	if _flags[ 'COMPILE' ]: _makeBinary()

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

	f = open( _flags[ 'C_FILE' ], 'w' )
	# packing protection module first
	print( 'Dumping protection module' )
	bytecode = _dumpCode( compile( _readFile( _flags[ 'PROTECTION_MODULE' ] ), '', 'exec' ) )
	f.write( '\n#define PROT_BYTECODE_SIZE     %s\n' % len( bytecode ) )
	_writeToFile( f, _encryptString( _packBytecode( bytecode ) ), '__prot__' )
	mods = _getModules()
	table = []
	for name in reversed( mods.keys() ):
		m = mods[ name ]
		if m.__code__: # preventing dumping of built-in modules
			print( "Dumping '%s'" % name )
			bytecode = _dumpCode( m.__code__ )
			item = [
				name, # internal name
				'__main__' if name == '__main__' else '_mod_' + '__'.join( name.split( '.' ) ), # variable name
				len( bytecode ) # actual size of a bytecode
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
	f.close()
	if _flags[ 'COMPILE' ]: _makeBinary()

# Analizes flags
def _analizeFlags():
	if _flags[ 'SHOW_HELP' ]:
		print( _USAGE )
		sys.exit( 0 )
	if _flags[ 'FREEZE_LOCAL' ]:
		path = os.path.dirname( _flags[ 'PY_FILE' ] )
		if path: _flags[ 'SEARCH_PATH' ] = [ path ]
		else:    _flags[ 'SEARCH_PATH' ] = '.'
	if not _flags[ 'PY_FILE' ]:
		raise FreezerError, 'missing main module'
	if not _flags[ 'PROTECTION_KEY' ] and not _flags[ 'PROTECTION_MODULE' ]:
		_createSimple()
	elif _flags[ 'PROTECTION_KEY' ] and _flags[ 'PROTECTION_MODULE' ]:
		_createAdvanced()
	elif not _flags[ 'PROTECTION_KEY' ]:
		raise FreezerError, 'missing protection key'
	else:
		raise FreezerError, 'missing protection module'
	if _flags[ 'DEV_CPP_DIR' ][ -1 ] != '/': _flags[ 'DEV_CPP_DIR' ] += '/'

# Analizes given arguments
def _parseArguments( args ):
	if 'py_file' in args.keys():
		_flags[ 'PY_FILE' ] = args[ 'py_file' ]
	if 'c_file' not in args.keys():
		_flags[ 'C_FILE' ] = args[ 'py_file' ][ : -2 ] + 'c'
	else:
		_flags[ 'C_FILE' ] = args[ 'c_file' ]
	if 'pkey' in args.keys():
		_flags[ 'PROTECTION_KEY' ] = args[ 'pkey' ]
	if 'pmod' in args.keys():
		_flags[ 'PROTECTION_MODULE' ] = args[ 'pmod' ]
	if 'local' in args.keys():
		_flags[ 'FREEZE_LOCAL' ] = args[ 'local' ]
	if 'compile' in args.keys():
		_flags[ 'COMPILE' ] = args[ 'compile' ]
	if 'dev_cpp_dir' in args.keys():
		_flags[ 'DEV_CPP_DIR' ] = args[ 'dev_cpp_dir' ]

# Gets options from command line
def _parseCommandLine():
	try:
		import getopt
		opts, args = getopt.getopt(
			sys.argv[ 1 : ],
			'hk:m:lo:gd:',
			[ 'help', 'pkey=', 'pmod=', 'amods=' ]
		)
		for o in opts:
			if   o[ 0 ] == '-h' or o[ 0 ] == '--help' : _flags[ 'SHOW_HELP' ]         = True
			elif o[ 0 ] == '-k' or o[ 0 ] == '--pkey':  _flags[ 'PROTECTION_KEY' ]    = o[ 1 ]
			elif o[ 0 ] == '-m' or o[ 0 ] == '--pmod':  _flags[ 'PROTECTION_MODULE' ] = o[ 1 ]
			elif o[ 0 ] == '-l':                        _flags[ 'FREEZE_LOCAL' ]      = True
			elif o[ 0 ] == '-o':                        _flags[ 'C_FILE' ]            = o[ 1 ]
			elif o[ 0 ] == '-g':                        _flags[ 'COMPILE' ]           = False
			elif o[ 0 ] == '-d':                        _flags[ 'DEV_CPP_DIR' ]       = o[ 1 ]
			elif o[ 0 ] == '--amods':
				for pair in o[ 1 ].split( ',' ):
					modname, filename = pair.split( ':' )
					_flags[ 'ADDITIONAL_MODULES' ][ modname ] = filename					
		if args:
			_flags[ 'PY_FILE' ] = args[ 0 ]
			if not _flags[ 'C_FILE' ]: _flags[ 'C_FILE' ]  = args[ 0 ][ : -2 ] + 'c'
	except getopt.GetoptError, err:
		print( err )
		sys.exit( 1 )

# Parses variables in 'Freezefile'
def _parseVariables():
	def normalizePath( path ):
		if sys.platform == 'win32':
			if path[ 1 ] != ':': path = os.path.normpath( _flags[ 'LOCATION' ] + path )
		else:
			if path[ 0 ] != '/': path = os.path.normpath( _flags[ 'LOCATION' ] + path )
		return path
	#
	try:
		_flags[ 'PY_FILE' ] = normalizePath( PY_FILE )
		try: _flags[ 'C_FILE' ] = normalizePath( C_FILE )
		except NameError: _flags[ 'C_FILE' ] = _flags[ 'PY_FILE' ][ : -2 ] + 'c'
	except NameError: pass
	try: _flags[ 'PROTECTION_KEY' ] = PROTECTION_KEY
	except NameError: pass
	try: _flags[ 'PROTECTION_MODULE' ] = normalizePath( PROTECTION_MODULE )
	except NameError: pass
	try: _flags[ 'FREEZE_LOCAL' ] = FREEZE_LOCAL
	except NameError: pass
	try:
		for k, v in ADDITIONAL_MODULES.iteritems():
			ADDITIONAL_MODULES[ k ] = normalizePath( v )
		_flags[ 'ADDITIONAL_MODULES' ] = ADDITIONAL_MODULES
	except NameError: pass
	try: _flags[ 'COMPILE' ] = COMPILE
	except NameError: pass

####################################################################################################

def freeze( **args ): # called from other module
	"""
This function receives named arguments that
tells what modules should be freezed and in
which way.

Required arguments:
 py_file - full name of a main module (executed at startup)
Optional arguments:
 c_file      - full name of generated .c file (by default equals to
               'py_file' name with replaced extension to .c. The base
               name is used as a program name)
 pkey        - string value of protection key (must be coupled with 'pmod')
 pmod        - name of module that implements function 'getKey'
 local       - boolean value that enables/disables freezing of
               dependent local modules ('False' by default)c
 amods       - dictionary containing pairs MODULE_NAME:MODULE_FILE
               of additonal modules, which cannot be detected by
               introspection but also must be froze into executable
 compile     - boolean value that enables/disables compilation of
               generated file ('True' by default)
 dev_cpp_dir - specify a directory where Dev-C++ is installed
               (Windows only; by default is 'C:/Dev-Cpp/')
"""
	_parseArguments( args )
	_analizeFlags()

def _main(): # called from command line
	try:
		if len( sys.argv ) == 1:
			_flags[ 'LOCATION' ] = os.getcwd() + os.sep
			filename = _flags[ 'LOCATION' ] + 'Freezefile'
			if os.path.exists( filename ):
				execfile( filename, globals() )
				_parseVariables()
			else: raise FreezerError, "cannot stat 'Freezefile'"
		else: _parseCommandLine()
		_analizeFlags()
		sys.exit( 0 )
	except FreezerError, err:
		print( sys.argv[ 0 ] + ': ' + str( err ) )
		sys.exit( 1 )

if __name__ == '__main__': _main()
