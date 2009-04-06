import commands, md5, platform, os, os.path, sys

if __name__ == '__main__':
    fsys_name = commands.getstatusoutput('df '+ os.getcwd())[1].split('\n')[1].split(' ')[0]
    id = filter(lambda x: os.path.realpath('/dev/disk/by-uuid/' + x) == fsys_name, os.listdir('/dev/disk/by-uuid'))
    if not id:
        print "error 11294"; sys.exit()
    else:
        id = id[0]
    check_id = filter(lambda x: os.path.realpath('/dev/disk/by-id/' + x) == fsys_name, os.listdir('/dev/disk/by-id'))
    if not check_id:
        print "error 11794"; sys.exit()
    else:
        check_id = check_id[0].lower()
    
    if (check_id.find('vmware') != -1) or (check_id.find('virtual') != -1):
        print "error 11669"; sys.exit()
    #__1, __2 =  commands.getstatusoutput( 'dmidecode -s system-uuid' )
    #if __1 or not __2: raise SystemError( "can't identify hardware" )
    #__3 = [ids for ids in os.listdir('/dev/disk/by-uuid') if ( not 'part' in ids)]
    __3 = id
    if  not __3: print "error 11873"; sys.exit() #can't identify hardware
    '''
    for __4 in __2.split( '\n' ):
	    __4 = __4.split( '_' )[ 1 ].split( '-' )[ 0 ]
	    if __4 and __4 not in __3: __3.append( __4 )'''
    __6 = str.join('', __3)
    __6 = md5.new(__6).hexdigest()
    #__6 += open('license.lic').read()
    print __6.upper()
