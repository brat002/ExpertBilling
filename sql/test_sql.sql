                               
SELECT ba.id, bt.id, act.id, act.datetime, ARRAY(SELECT bgps.group_id, SUM(bgps.bytes) FROM billservice_groupstat AS bgps WHERE (bgps.group_id IN (SELECT bttn2.traffic_transmit_service_id FROM billservice_traffictransmitnodes as bttn2 WHERE bttn2.traffic_transmit_service_id = bt.traffic_transmit_service_id)) AND (bgps.datetime BETWEEN act.datetime AND %s) GROUP BY bgps.group_id ORDER BY bgps.group_id) AS gr_bytes 
           FROM billservice_tariff AS bt 
           JOIN billservice_accounttarif AS act ON 
               EXISTS (SELECT 1 FROM billservice_traffictransmitnodes as bttn1 WHERE bttn1.traffic_transmit_service_id = bt.traffic_transmit_service_id) 
               AND act.tarif_id=bt.id
               AND act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=act.account_id and att.datetime<%s ORDER BY datetime DESC LIMIT 1)               
           JOIN billservice_account as ba ON  
               ba.id = act.account_id
               
           ORDER BY bt.id, ba.id;
       
  


CREATE TYPE group_bytes AS (
    group_id_t int,
    bytes_t    numeric
);



SELECT ba.id AS account_id, bt.id AS tarif_id, act.id AS acct_id, act.datetime, ARRAY(SELECT ROW(bgps.group_id, SUM(bgps.bytes))::group_bytes FROM billservice_groupstat AS bgps WHERE (bgps.group_id IN (SELECT bttn2.traffic_transmit_service_id FROM billservice_traffictransmitnodes as bttn2 WHERE bttn2.traffic_transmit_service_id = bt.traffic_transmit_service_id)) AND (bgps.datetime BETWEEN act.datetime AND now()) GROUP BY bgps.group_id ORDER BY bgps.group_id) AS gr_bytes 
           FROM billservice_tariff AS bt 
           JOIN billservice_accounttarif AS act ON 
               EXISTS (SELECT 1 FROM billservice_traffictransmitnodes as bttn1 WHERE bttn1.traffic_transmit_service_id = bt.traffic_transmit_service_id) 
               AND act.tarif_id=bt.id
               AND act.id=(SELECT id FROM billservice_accounttarif AS att WHERE att.account_id=act.account_id and att.datetime<now() ORDER BY datetime DESC LIMIT 1)               
           JOIN billservice_account as ba ON  
               ba.id = act.account_id               
           ORDER BY bt.id, ba.id;
           
  
CREATE TYPE group_nodes AS (
    group_id_t int,
    node_egde_t   int[]
);         
           
SELECT bt.id AS tarif_id,  ARRAY(SELECT ROW(bttn1.group_id, int_array_aggregate(bttn1.edge_value))::group_nodes FROM billservice_traffictransmitnodes as bttn1 WHERE bttn1.traffic_transmit_service_id = bt.traffic_transmit_service_id GROUP BY bttn1.group_id, bttn1.edge_value ORDER BY bttn1.group_id, bttn1.edge_value) AS gr_nodes 
           FROM billservice_tariff AS bt 
           WHERE EXISTS (SELECT 1 FROM billservice_traffictransmitnodes as bttn2 WHERE bttn2.traffic_transmit_service_id = bt.traffic_transmit_service_id AND bttn2.edge_value > 0)
           ORDER BY bt.id;
           
           
ALTER TABLE billservice_traffictransmitnodes ALTER edge_value TYPE int; 