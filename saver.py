import os, sys, cPickle, glob, logging
    
def log_error_(lstr, level=logging.ERROR):
    log_adapt(lstr, level)
    
def log_adapt(lstr, level):
    print lstr



def graceful_saver(objlists, globals_, moduleName, saveDir):
    for objlist in objlists:
        if len(getattr(globals_,objlist[0])) > 0:
            if len(objlist) == 1:
                for objname in objlist:
                    if objname[-1] == '_': objname = objname[:-1]
                    f = open(saveDir + '/' + moduleName + objname + '.dmp', 'wb')
                    cPickle.dump(getattr(globals_, objname), f)
                    # pickled)
                    f.close()
            else:
                objnames_ = '_o_'.join(map(lambda x: x[:-1] if x[-1] == '_' else x, objlist))
                pickleobjets = []
                for objname in objlist:
                    pickleobjets.append(getattr(globals_, objname))
                
                f = open(saveDir + '/' + moduleName + objnames_ + '.dmp', 'wb')
                cPickle.dump(pickleobjets, f)
                # pickled)
                f.close()    
                    
                
def graceful_loader(objnames, globals_, moduleName, saveDir):
    fllist = glob.glob(saveDir + '/' + moduleName + '*' + '.dmp')
    dumpedObjs = []
    for objname in objnames:
        i = 0
        objname_ = objname if not isinstance(objname, list) else '_o_'.join(objname)
        for fname in fllist:
            if fname.find(objname_) != -1:
                f = open(fname, 'rb')
                try:
                    pickled = cPickle.load(f)
                    if not isinstance(objname, list):
                        setattr(globals_, objname, pickled)
                    else:
                        for z in xrange(len(objname)):
                            setattr(globals_, objname[z], pickled[z])
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
