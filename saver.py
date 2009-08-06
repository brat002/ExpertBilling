import os, sys, cPickle, glob
    
def log_error_(lstr, level=3):
    log_adapt(lstr, level)
    
def log_adapt(lstr, level):
    print lstr

def setAllowedUsers(licstr, dbconnection = None):
    def transformByte(lbytes):
        indef = lambda x: x == 'FFFF'
        if indef(lbytes): return (1 << 63) - 1
        else: return int(lbytes, 16)
    #global allowedUsers
    allowedUsers = lambda: 0
    try:
        if not licstr == '':
            allowed = str(transformByte(licstr[:2] + licstr[-2:]))
        else:
            log_error_('Test version: only 32 users allowed!' % ())
            allowed = str(2**3*2**2)        
        allowedUsers = lambda: int(allowed)
    except Exception, ex:
        log_error_("License file format error!")
        print "License file format error!"
        sys.exit()
    #print allowed
    if dbconnection:
        cur = dbconnection.cursor()
        cur.callproc('crt_allowed_checker', (allowedUsers(),))
        dbconnection.commit()
        cur.close()
        dbconnection.close()
    return allowedUsers

def allowedUsersChecker(allowed, current):
    if current() > allowed():
        log_error_("SHUTTING DOWN: current amount of users[%s] exceeds allowed[%s] for the license file" % (str(current()), str(allowed())))
        print >> sys.stderr, "SHUTTING DOWN: current amount of users[%s] exceeds allowed[%s] for the license file" % (str(current()), str(allowed()))
        sys.exit()

def graceful_saver(objlists, globals_, moduleName, saveDir):
    for objlist in objlists:
        if len(getattr(globals_,objlist[0])) > 0:
            for objname in objlist:
                if objname[-1] == '_': objname = objname[:-1]
                f = open(saveDir + '/' + moduleName + objname + '.dmp', 'wb')
                cPickle.dump(getattr(globals_, objname), f)
                # pickled)
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
                    pickled = cPickle.load(f)
                    setattr(globals_, objname, pickled)
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