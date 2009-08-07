utilites_sql = {
    'get_sessions' : """SELECT session_id, nas_int_id, interrim_update FROM radius_activesession \
                      WHERE date_end IS NULL AND interrim_update <= %s AND (session_status = 'ACTIVE' OR session_status = 'NACK');"""
            }