DELETE FROM billservice_accountprepaystrafic
WHERE id IN (SELECT id
              FROM (SELECT id,
                             row_number() over (partition BY account_tarif_id, prepaid_traffic_id, current ORDER BY id) AS rnum
                     FROM billservice_accountprepaystrafic) t
              WHERE t.rnum > 1);
              
              
ALTER TABLE billservice_accountprepaystrafic
  ADD CONSTRAINT billservice_accountprepaystrafic_uniq UNIQUE (account_tarif_id, prepaid_traffic_id, current);