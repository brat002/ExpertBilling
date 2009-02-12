#-*-encoding:utf-8-*-

import psycopg2


class bpplotAdapter(object): 
    '''Adapter class for DB connection'''
    
    rCursor = None
    
    @staticmethod
    def getdata(selstr):
        '''Connects to the database using #cstr# and executes 
        @selstr - query (SELECT) string, returns selected data'''
        #print "query: " + selstr 
        curs = bpplotAdapter.rCursor
        try:
            curs.execute(selstr)
        except psycopg2.ProgrammingError, perr:
            raise perr 
        retval = curs.fetchall()
        curs.connection.commit()
        return retval
    
