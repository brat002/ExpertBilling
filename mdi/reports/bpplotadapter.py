#-*-encoding:utf-8-*-

import psycopg2

#database connect string
cstr = "dbname=mikrobill user=mikrobill password=1234 host=10.10.1.1"



class bpplotAdapter(object): 
    '''Adapter class for DB connection'''

    @staticmethod
    def getdata(selstr):
        '''Connects to the database using #cstr# and executes 
        @selstr - query (SELECT) string, returns selected data'''
        try: 
            conn = psycopg2.connect(cstr)        
        except psycopg2.OperationalError, oerr:
            raise oerr
        #conn.set_client_encoding('UTF8')        
        curs = conn.cursor()
        
        try:
            curs.execute(selstr)
        except psycopg2.ProgrammingError, perr:
            raise perr        
        
        return curs.fetchall()
    
