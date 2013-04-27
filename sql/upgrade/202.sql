CREATE TABLE "billservice_notificationssettings" (
    "id" serial NOT NULL PRIMARY KEY,
    "payment_notifications" boolean NOT NULL,
    "payment_notifications_template" text NOT NULL,
    "tariff_cost_notifications" boolean NOT NULL,
    "tariff_cost_notifications_template" text NOT NULL,
    "balance_notifications" boolean NOT NULL,
    "balance_edge" double precision NOT NULL,
    "balance_notifications_each" integer NOT NULL,
    "balance_notifications_limit" integer NOT NULL,
    "balance_notifications_template" text NOT NULL,
    "send_email" boolean NOT NULL,
    "send_sms" boolean NOT NULL
)
;
