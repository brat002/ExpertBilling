CREATE INDEX CONCURRENTLY billservice_ipinuse_id_ack_idx
   ON billservice_ipinuse (id ASC NULLS LAST, ack ASC NULLS LAST);
   