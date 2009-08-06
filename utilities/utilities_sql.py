utilites_sql = {
    'get_sessions' : """SELECT session_id, nas_id, interrim_update FROM radius_activesession \
                      WHERE date_end IS NULL AND interrim_update <= %s;"""
            }