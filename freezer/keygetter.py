import commands, platform, os, os.path, sys
from hashlib import md5

def get_linux_key(allow_virtual=False):
    try:
        fsys_name = commands.getstatusoutput('/bin/df '+ os.getcwd())[1].split('\n')[1].split(' ')[0]
        id = filter(lambda x: os.path.realpath('/dev/disk/by-uuid/' + x) == fsys_name, os.listdir('/dev/disk/by-uuid'))
    except:
        print "error 66004"; sys.exit()
    check_id = ''    
    try:
        check_id = filter(lambda x: os.path.realpath('/dev/disk/by-id/' + x) == fsys_name, os.listdir('/dev/disk/by-id'))
    except:
        if not allow_virtual:
            print "error 66007"
            sys.exit()
    if not check_id and not allow_virtual:
        print "error 11794"; sys.exit()
    elif check_id:
        check_id = check_id[0].lower()        

    if not id:
        id = check_id
    else:
        id = id[0]
    if not id: print "error 11873"; sys.exit() #can't identify hardware
    
    if not allow_virtual:
        if (check_id.find('vmware') != -1) or (check_id.find('virtual') != -1):
            print "error 11669"; sys.exit()
        
    __3 = id    
    __6 = str.join('', __3)
    __6 = md5(__6).hexdigest()
    return __6.upper()[:-1] + 'L'

def get_bsd_key(allow_virtual=False):
    try:
        fsys_name = commands.getstatusoutput('/bin/df '+ os.getcwd())[1].split('\n')[1].split(' ')[0].split('/')[2][:3]
        disk_type = fsys_name[:2]; disk_num = fsys_name[2]
        id = commands.getstatusoutput('/sbin/sysctl dev.' + disk_type + '.' + disk_num + '.%desc')
        if not id: print "error 77075"; sys.exit()
        if not allow_virtual:
            if id.lower().find('virtual') != -1: print "error 77088"; sys.exit()
        id = id.split(': ')[1]
    except:
        print "error 77004"; sys.exit()
        
    __3 = id    
    __6 = str.join('', __3)
    __6 = md5(__6).hexdigest()
    return __6.upper()[:-1] + 'D'

if __name__ == '__main__':
    allow_virtual = False
    if '-a' in sys.argv:
        allow_virtual = True
    if platform.system() == 'Linux':
        key = get_linux_key(allow_virtual)
    elif platform.system()[-3:] == 'BSD':
        key = get_bsd_key(allow_virtual)
    else:
        print "error 00497"; sys.exit()
        
    print key
    
#008F39C777CDF7FB4FAB233AFE156DDL
