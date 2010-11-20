def get_db_data(cur, sql, options=[]):
    if options:
        cur.execute(sql, options)
    else:
        cur.execute(sql)
        
    ret_data = cur.fetchall()
    cur.connection.commit()
    return ret_data

def simple_list_index(data_list, key_idxs=[0], value_idxs=[1]):
    if len(key_idxs) == 1:
        get_keys = lambda d_field: d_field[key_idxs[0]]
    else:
        get_keys = lambda d_field: tuple([d_field[i] for i in key_idxs])
    
    return [(get_keys(data_field), [data_field[j] for j in value_idxs]) for data_field in data_list]
    