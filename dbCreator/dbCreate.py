import psycopg2
import ConfigParser

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.readfp(open('db.conf'))
    dbopts = config.items("db")
    cstr = "dbname=ebs8 user=mikrobill password=1234 host=localhost"
    f = open('ebs_test3.sql', 'rb')
    #selstr = f.read()
    try: 
        conn = psycopg2.connect(cstr)        
    except psycopg2.OperationalError, oerr:
        raise oerr
    #conn.set_client_encoding('UTF8')        
    curs = conn.cursor()
    try:
        #for selstr in f:
        #allstr = f.read()
        #selstrs = allste.split(';')
        '''while selstr:
            curs.execute(selstr + '\\')
            selstr = f.read(50)'''
        qstr = r''
        cfcmt = True
        #cfcmt = lambda: curs.commit()
        for line in f:
            selstr = line.strip('\n')
            qstr += selstr
            if selstr[-1] != ';':                
                continue         
            if (qstr.find('$$') != -1) and (selstr.find('$$') == -1):
                continue
            if (qstr.find('CREATE FUNCTION') != -1):
                cfcmt()
                cfcmt = lambda: False
            curs.execute(qstr)
            qstr = r''
    except psycopg2.ProgrammingError, perr:
        raise perr