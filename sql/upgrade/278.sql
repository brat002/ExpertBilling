ALTER TABLE billservice_periodicalservice ADD COLUMN delta_from_ballance boolean;
ALTER TABLE billservice_periodicalservice ALTER COLUMN delta_from_ballance SET DEFAULT true;
