CREATE INDEX CONCURRENTLY billservice_accountprepaystrafic_size_current
   ON billservice_accountprepaystrafic (size ASC NULLS LAST, current ASC NULLS LAST, account_tarif_id ASC NULLS LAST);

   