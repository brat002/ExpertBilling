import os, sys, cPickle, glob
from log_adapter import log_error_

def setAllowedUsers(dbconnection, filepath):
    def transformByte(lbyte):
        ldict = {'A': 50, 'B': 250, 'C': 500, 'D': 800, 'E': 1000, 'F': ((1 << 63) - 1)}
        return ldict.get(lbyte, 0)
    #global allowedUsers
    allowedUsers = lambda: 0
    try:
        lfile = open(filepath, 'rb')
    except Exception,e:
        log_error_(repr(e))
        log_error_("License not found")
        print "License not found"
        sys.exit()
        
    lfile.seek(-1, 2)
    allowed = str(transformByte(lfile.read(1)))
    allowedUsers = lambda: int(allowed)
    lfile.close()
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
                    log.error('Problems with unpickling file %s: %s' % (fname, repr(ex)))
                    print >> sys.stderr, 'Problems with unpickling file %s: %s' % (fname, repr(ex))
                finally:
                    f.close()
                    os.unlink(fname)
                break
            i += 1
        if i < len(fllist):
            fllist.pop(i)