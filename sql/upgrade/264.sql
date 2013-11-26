CREATE FUNCTION ip2int(text) RETURNS bigint AS $$ 
SELECT split_part($1,'.',1)::bigint*16777216 + split_part($1,'.',2)::bigint*65536 +
 split_part($1,'.',3)::bigint*256 + split_part($1,'.',4)::bigint;
$$ LANGUAGE SQL  IMMUTABLE RETURNS NULL ON NULL INPUT;
