CREATE OR REPLACE FUNCTION check_allowed_users_trg_fn()
  RETURNS trigger AS
$BODY$
DECLARE counted_num_ bigint;
  allowed_num_ bigint := 0;
BEGIN
  allowed_num_ := return_allowed();
  SELECT count(*) FROM billservice_account INTO counted_num_;
  IF counted_num_ + 1 > allowed_num_ THEN
  RAISE EXCEPTION 'Amount of users[% + 1] will exceed allowed[%] for the license file!', counted_num_, allowed_num_;
  ELSE
  RETURN NEW;
  END IF;
  END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION check_allowed_users_trg_fn() OWNER TO ebs;

