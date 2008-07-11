#-*-encoding:utf-8-*-

class BaseModel(object):
    def __init__(self):
        self.fields=[]
        self.table=''
    
    def create(self, *args, **kwargs):
                
        if len(kwargs)>0:
            sql="INSERT INTO %s (%s) VALUES('%s') RETURNING id;" % (self.table, "','".join([x for x in kwargs ]), "%s" % "','".join([kwargs[x] for x in kwargs ]))
        else:
            pass
            """
            Сделать форматирование для случая
            n=Nas()
            n.id=1
            n.name="123"
            n.create()
            """
        return sql, True


    def update(self, where='', *args, **kwargs):
        #Не работает
        if len(kwargs)>0:
            sql="UPDATE %s SET %s WHERE %s;" % (self.table, " , ".join(["%s='%s'" % (x, kwargs[x]) for x in kwargs ]), where)
            print sql
        else:
            pass
            """
            Сделать форматирование для случая
            n=Nas()
            n.id=1
            n.name="123"
            n.update()
            """
        return sql, False

    
    def get(self, where=''):
        sql="SELECT * FROM %s WHERE %s" % (self.table, where)
        return sql+";", True
    
    def all(self, limit=[], order=None):
        sql="SELECT "+ ",".join([x for x in self.fields ]) +" FROM %s" % self.table
        
        if order: sql+=" ORDER BY %s" % order
        
        if len(limit)>0:
            if limit[0]:
                sql+=" LIMIT %d" % limit[0]
                if limit[1]:
                    sql+=", %d" % limit[1]
        return sql+";", True
    
    def filter(self, limit=[], where='', order=None):
        sql="SELECT "+ ",".join([x for x in self.fields ]) +" FROM %s WHERE %s" % (self.table, where)
        if order: sql+=" ORDER BY %s" % order
        if len(limit)>0:
            if limit[0]:
                sql+=" LIMIT %d" % limit[0]
                if limit[1]:
                    sql+=", %d" % limit[1]
        return sql+";", True   
    
    def delete(self, where=None):
        """
        Если указан where - удаление по условию. Если не указан-удаление текущего объекта  
        """
        if where:
            sql="DELETE FROM %s WHERE %s" % (self.table, where)
        else:
            sql="DELETE FROM %s WHERE id='%s'" % (self.table, self.id)
        return sql, False
    
    def parse(self,result):
        print 'start_parse'
        objects_list=[]
        for res in result:
            objects_list.append(self.__class__(res))
            
        if len(objects_list)==1:
            return objects_list[0]
        return objects_list

    
class Nas(BaseModel):
    def __init__(self, obj=None):
        self.table = "nas_nas"
        
        self.fields=[
            "id",
            "type",
            "name",
            "ipaddress",
            "secret",
            "login",
            "password",
            "description",
            "allow_pptp",
            "allow_pppoe",
            "allow_ipn",
            "user_add_action",
            "user_enable_action",
            "user_disable_action",
            "user_delete_action",
            "support_pod",
            "support_coa",
            "configure_nas",
            "confstring"]
        
        i=0
        if obj:
            print obj
            for field in self.fields:
                setattr(self, field, obj[i])
                i+=1
        else:
            for field in self.fields:
                print field
                setattr(self, field, None)
                i+=1 

class Nas(BaseModel):
    def __init__(self, obj=None):
        self.table = "nas_nas"
        
        self.fields=[
            "id",
            "type",
            "name",
            "ipaddress",
            "secret",
            "login",
            "password",
            "description",
            "allow_pptp",
            "allow_pppoe",
            "allow_ipn",
            "user_add_action",
            "user_enable_action",
            "user_disable_action",
            "user_delete_action",
            "support_pod",
            "support_coa",
            "configure_nas",
            "confstring"]
        
        i=0
        if obj:
            print obj
            for field in self.fields:
                setattr(self, field, obj[i])
                i+=1
        else:
            for field in self.fields:
                print field
                setattr(self, field, None)
                i+=1 
                