import commands, md5, platform, os, os.path, sys

def get_linux_key():
    try:
        fsys_name = commands.getstatusoutput('/bin/df '+ os.getcwd())[1].split('\n')[1].split(' ')[0]
        id = filter(lambda x: os.path.realpath('/dev/disk/by-uuid/' + x) == fsys_name, os.listdir('/dev/disk/by-uuid'))
    except:
        print "error 66004"; sys.exit()
    if not id:
        print "error 11294"; sys.exit()
    else:
        id = id[0]
    if not id: print "error 11873"; sys.exit() #can't identify hardware
    try:
        check_id = filter(lambda x: os.path.realpath('/dev/disk/by-id/' + x) == fsys_name, os.listdir('/dev/disk/by-id'))
    except:
        print "error 66007"; sys.exit()
    if not check_id:
        print "error 11794"; sys.exit()
    else:
        check_id = check_id[0].lower()
    
    if (check_id.find('vmware') != -1) or (check_id.find('virtual') != -1):
        print "error 11669"; sys.exit()
        
    __3 = id    
    __6 = str.join('', __3)
    __6 = md5.new(__6).hexdigest()
    return __6.upper()[:-1] + 'L'

def get_bsd_key():
    try:
        fsys_name = commands.getstatusoutput('/bin/df '+ os.getcwd())[1].split('\n')[1].split(' ')[0].split('/')[2][:3]
        disk_type = fsys_name[:2]; disk_num = fsys_name[2]
        id = commands.getstatusoutput('/sbin/sysctl dev.' + disk_type + '.' + disk_num + '.%desc')
        if not id: print "error 77075"; sys.exit()
        if id.lower().find('virtual') != -1: print "error 77088"; sys.exit()
        id = id.split(': ')[1]
    except:
        print "error 77004"; sys.exit()
        
    __3 = id    
    __6 = str.join('', __3)
    __6 = md5.new(__6).hexdigest()
    return __6.upper()[:-1] + 'D'

if __name__ == '__main__':
    if platform.system() == 'Linux':
        key = get_linux_key()
    elif platform.system()[-3:] == 'BSD':
        key = get_bsd_key()
    else:
        print "error 00497"; sys.exit()
        
    print key
