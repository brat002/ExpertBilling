ALTER TABLE billservice_settlementperiod
   ALTER COLUMN length DROP NOT NULL;

ALTER TABLE billservice_settlementperiod
   ALTER COLUMN length SET DEFAULT 0;
   
   