delete from billservice_ipinuse where pool_id not in (SELECT id FROM billservice_ippool);
