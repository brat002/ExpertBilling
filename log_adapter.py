def log_info_(lstr, level=1):
    log_adapt(lstr, level)
    
def log_debug_(lstr, level=0):
    log_adapt(lstr, level)
    
def log_warning_(lstr, level=2):
    log_adapt(lstr, level)
    
def log_error_(lstr, level=3):
    log_adapt(lstr, level)
    
def log_adapt(lstr, level):
    print lstr