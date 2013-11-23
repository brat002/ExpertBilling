CREATE OR REPLACE FUNCTION get_free_ip_from_pool(ag_pool_id_ integer)
  RETURNS inet AS
$BODY$
BEGIN

RETURN (SELECT free_ip.ipaddress FROM 
(SELECT 
(SELECT start_ip FROM billservice_ippool WHERE id=ag_pool_id_) + ip_series.ip_inc 
FROM generate_series(0, (SELECT end_ip - start_ip FROM billservice_ippool WHERE id=ag_pool_id_))AS ip_series(ip_inc)) AS free_ip(ipaddress)
WHERE free_ip.ipaddress NOT IN (SELECT ip FROM billservice_ipinuse WHERE pool_id=ag_pool_id_ and ((dynamic=False and disabled is not null) or (ack=True and disabled is Null) or 
(disabled is NULL and ack=False and datetime>now()-(acct_interval*5 || ' seconds')::INTERVAL) or (disabled is not null and disabled>now()-interval '5 minutes'))) ORDER BY RANDOM() LIMIT 1);

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
  
CREATE OR REPLACE FUNCTION get_free_ip_from_pool(ag_pool_id_ integer, acct_interval integer)
  RETURNS inet AS
$BODY$
BEGIN

RETURN (SELECT free_ip.ipaddress FROM 
(SELECT 
(SELECT start_ip FROM billservice_ippool WHERE id=ag_pool_id_) + ip_series.ip_inc 
FROM generate_series(0, (SELECT end_ip - start_ip FROM billservice_ippool WHERE id=ag_pool_id_))AS ip_series(ip_inc)) AS free_ip(ipaddress)
WHERE free_ip.ipaddress NOT IN 
   (SELECT ip FROM billservice_ipinuse WHERE pool_id=ag_pool_id_ and ((dynamic=False and disabled is not null) or (disabled is NULL and ack=False and datetime>=now()-(acct_interval*5 || ' seconds')::INTERVAL) or (last_update is not null and last_update>now()-(acct_interval*10 || ' seconds')::INTERVAL))) ORDER BY RANDOM() LIMIT 1);

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;