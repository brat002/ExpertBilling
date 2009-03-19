import commands, md5, platform

if __name__ == '__main__':
    __1, __2 =  commands.getstatusoutput( 'ls /dev/disk/by-id' )
    if __1 or not __2: raise SystemError( "can't identify hardware" )
    __3 = []
    for __4 in __2.split( '\n' ):
	    __4 = __4.split( '_' )[ 1 ].split( '-' )[ 0 ]
	    if __4 and __4 not in __3: __3.append( __4 )
    __6 = str.join('', __3)
    __6 += platform.platform()
    __6 += open('license.lic').read()
    __6 = md5.new(__6).hexdigest()
    print __6.upper()
