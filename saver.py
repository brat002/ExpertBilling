import os, sys, cPickle, glob
    
def log_error_(lstr, level=3):
    log_adapt(lstr, level)
    
def log_adapt(lstr, level):
    print lstr

def setAllowedUsers(dbconnection, filepath):
    def transformByte(lbytes):
        indef = lambda x: x == 'FFFF'
        if indef(lbytes): return (1 << 63) - 1
        else: return int(lbytes, 16)
    #global allowedUsers
    allowedUsers = lambda: 0
    try:
        lfile = open(filepath, 'rb')
    except Exception,e:
        log_error_(repr(e))
        log_error_("License not found")
        print "License not found"
        sys.exit()
      
    try:
        lfile.seek(0,0)
        fhf = lfile.read(2)        
        lfile.seek(-2, 2)
        shf = lfile.read(2) 
        allowed = str(transformByte(fhf + shf))
        allowedUsers = lambda: int(allowed)
        lfile.close()
    except Exception, ex:
        log_error_("License file format error!")
        print "License file format error!"
        sys.exit()
    #print allowed
    cur = dbconnection.cursor()
    cur.callproc('crt_allowed_checker', (allowedUsers(),))
    dbconnection.commit()
    cur.close()
    dbconnection.close()
    return allowedUsers

def allowedUsersChecker(allowed, current):
    if current() > allowed():
        log_error_("SHUTTING DOWN: current amount of users[%s] exceeds allowed[%s] for the license file" % (str(current()), str(allowed())))
        print stderr >> sys.stderr, "SHUTTING DOWN: current amount of users[%s] exceeds allowed[%s] for the license file" % (str(current()), str(allowed()))
        sys.exit()

def graceful_saver(objlists, globals_, moduleName, saveDir):
    for objlist in objlists:
        if len(globals_[objlist[0]]) > 0:
            for objname in objlist:
                if objname[-1] == '_': objname = objname[:-1]
                f = open(saveDir + '/' + moduleName + objname + '.dmp', 'wb')
                cPickle.dump(globals_[objname], f)
                f.close()
                
def graceful_loader(objnames, globals_, moduleName, saveDir):
    fllist = glob.glob(saveDir + '/' + moduleName + '*' + '.dmp')
    dumpedObjs = []
    for objname in objnames:
        i = 0
        for fname in fllist:
            if fname.find(objname) != -1:
                f = open(fname, 'rb')
                try:
                    globals_[objname] = cPickle.load(f)
                except Exception, ex:
                    log_error_('Problems with unpickling file %s: %s' % (fname, repr(ex)))
                    print >> sys.stderr, 'Problems with unpickling file %s: %s' % (fname, repr(ex))
                finally:
                    f.close()
                    os.unlink(fname)
                break
            i += 1
        if i < len(fllist):
            fllist.pop(i)