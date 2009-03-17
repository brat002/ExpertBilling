
def log_info(lstr, level=1):
    log_adapt(lstr, level)
    
def log_debug(lstr, level=0):
    log_adapt(lstr, level)
    
def log_warning(lstr, level=2):
    log_adapt(lstr, level)
    
def log_error(lstr, level=3):
    log_adapt(lstr, level)
    
def log_adapt(lstr, level):
    print lstr