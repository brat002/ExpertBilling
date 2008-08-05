#-*-encoding:utf-8-*-

import psycopg2


class bpplotAdapter(object): 
    '''Adapter class for DB connection'''
    
    rCursor = 0
    
    @staticmethod
    def getdata(selstr):
        '''Connects to the database using #cstr# and executes 
        @selstr - query (SELECT) string, returns selected data'''
        '''try: 
            conn = psycopg2.connect(cstr)        
        except psycopg2.OperationalError, oerr:
            raise oerr
        #conn.set_client_encoding('UTF8')        
        curs = conn.cursor()'''
        
        curs = bpplotAdapter.rCursor
        try:
            curs.execute(selstr)
        except psycopg2.ProgrammingError, perr:
            raise perr        
        
        return curs.fetchall()
    
