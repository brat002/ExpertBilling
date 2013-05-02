CREATE OR REPLACE FUNCTION encrypt_pw(password text, key text)
  RETURNS text AS
$BODY$ 
BEGIN 

IF substring(password from 1 for 27) != '-----BEGIN PGP MESSAGE-----' THEN  
    return armor(encrypt(password::bytea, key::bytea, 'AES'))::text;
else 
    return password::text;
end if;

END; 
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION decrypt_pw(text, text)
  OWNER TO ebs;
