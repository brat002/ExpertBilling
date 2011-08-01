DROP TABLE  IF EXISTS helpdesk_queue CASCADE;

CREATE TABLE "helpdesk_queue" (
    "id" serial NOT NULL PRIMARY KEY,
    "title" varchar(100) NOT NULL,
    "slug" varchar(50) NOT NULL,
    "email_address" varchar(75),
    "locale" varchar(10),
    "allow_public_submission" boolean NOT NULL,
    "allow_email_submission" boolean NOT NULL,
    "escalate_days" integer,
    "new_ticket_cc" varchar(75),
    "updated_ticket_cc" varchar(75),
    "email_box_type" varchar(5),
    "email_box_host" varchar(200),
    "email_box_port" integer,
    "email_box_ssl" boolean NOT NULL,
    "email_box_user" varchar(200),
    "email_box_pass" varchar(200),
    "email_box_imap_folder" varchar(100),
    "email_box_interval" integer,
    "email_box_last_check" timestamp with time zone
)
;
DROP TABLE IF EXISTS helpdesk_ticket CASCADE;

CREATE TABLE "helpdesk_ticket" (
    "id" serial NOT NULL PRIMARY KEY,
    "title" varchar(200) NOT NULL,
    "queue_id" integer NOT NULL REFERENCES "helpdesk_queue" ("id") DEFERRABLE INITIALLY DEFERRED,
    "submitter_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "created" timestamp with time zone NOT NULL,
    "modified" timestamp with time zone NOT NULL,
    "submitter_email" varchar(75),
    "assigned_to_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "status" integer NOT NULL,
    "on_hold" boolean NOT NULL,
    "description" text,
    "resolution" text,
    "priority" integer NOT NULL,
    "last_escalation" timestamp with time zone
)
;
DROP TABLE IF EXISTS helpdesk_followup CASCADE;
CREATE TABLE "helpdesk_followup" (
    "id" serial NOT NULL PRIMARY KEY,
    "ticket_id" integer NOT NULL REFERENCES "helpdesk_ticket" ("id") DEFERRABLE INITIALLY DEFERRED,
    "date" timestamp with time zone NOT NULL,
    "title" varchar(200),
    "comment" text,
    "public" boolean NOT NULL,
    "user_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "new_status" integer
)
;
DROP TABLE IF EXISTS helpdesk_ticketchange CASCADE;

CREATE TABLE "helpdesk_ticketchange" (
    "id" serial NOT NULL PRIMARY KEY,
    "followup_id" integer NOT NULL REFERENCES "helpdesk_followup" ("id") DEFERRABLE INITIALLY DEFERRED,
    "field" varchar(100) NOT NULL,
    "old_value" text,
    "new_value" text
)
;
DROP TABLE IF EXISTS helpdesk_attachment CASCADE;
CREATE TABLE "helpdesk_attachment" (
    "id" serial NOT NULL PRIMARY KEY,
    "followup_id" integer NOT NULL REFERENCES "helpdesk_followup" ("id") DEFERRABLE INITIALLY DEFERRED,
    "file" varchar(100) NOT NULL,
    "filename" varchar(100) NOT NULL,
    "mime_type" varchar(30) NOT NULL,
    "size" integer NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_presetreply CASCADE;
CREATE TABLE "helpdesk_presetreply" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "body" text NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_escalationexclusion CASCADE;
CREATE TABLE "helpdesk_escalationexclusion" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "date" date NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_emailtemplate CASCADE;
CREATE TABLE "helpdesk_emailtemplate" (
    "id" serial NOT NULL PRIMARY KEY,
    "template_name" varchar(100) NOT NULL UNIQUE,
    "subject" varchar(100) NOT NULL,
    "heading" varchar(100) NOT NULL,
    "plain_text" text NOT NULL,
    "html" text NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_kbcategory CASCADE;
CREATE TABLE "helpdesk_kbcategory" (
    "id" serial NOT NULL PRIMARY KEY,
    "title" varchar(100) NOT NULL,
    "slug" varchar(50) NOT NULL,
    "description" text NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_kbitem CASCADE;
CREATE TABLE "helpdesk_kbitem" (
    "id" serial NOT NULL PRIMARY KEY,
    "category_id" integer NOT NULL REFERENCES "helpdesk_kbcategory" ("id") DEFERRABLE INITIALLY DEFERRED,
    "title" varchar(100) NOT NULL,
    "question" text NOT NULL,
    "answer" text NOT NULL,
    "votes" integer NOT NULL,
    "recommendations" integer NOT NULL,
    "last_updated" timestamp with time zone NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_savedsearch CASCADE;
CREATE TABLE "helpdesk_savedsearch" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "title" varchar(100) NOT NULL,
    "shared" boolean NOT NULL,
    "query" text NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_usersettings CASCADE;
CREATE TABLE "helpdesk_usersettings" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "settings_pickled" text
)
;
DROP TABLE IF EXISTS helpdesk_ignoreemail CASCADE;
CREATE TABLE "helpdesk_ignoreemail" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "date" date NOT NULL,
    "email_address" varchar(150) NOT NULL,
    "keep_in_mailbox" boolean NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_ticketcc CASCADE;
CREATE TABLE "helpdesk_ticketcc" (
    "id" serial NOT NULL PRIMARY KEY,
    "ticket_id" integer NOT NULL REFERENCES "helpdesk_ticket" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "email" varchar(75),
    "can_view" boolean NOT NULL,
    "can_update" boolean NOT NULL
)
;
DROP TABLE IF EXISTS helpdesk_presetreply_queues CASCADE;
CREATE TABLE "helpdesk_presetreply_queues" (
    "id" serial NOT NULL PRIMARY KEY,
    "presetreply_id" integer NOT NULL REFERENCES "helpdesk_presetreply" ("id") DEFERRABLE INITIALLY DEFERRED,
    "queue_id" integer NOT NULL REFERENCES "helpdesk_queue" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("presetreply_id", "queue_id")
)
;
DROP TABLE IF EXISTS helpdesk_escalationexclusion_queues CASCADE;
CREATE TABLE "helpdesk_escalationexclusion_queues" (
    "id" serial NOT NULL PRIMARY KEY,
    "escalationexclusion_id" integer NOT NULL REFERENCES "helpdesk_escalationexclusion" ("id") DEFERRABLE INITIALLY DEFERRED,
    "queue_id" integer NOT NULL REFERENCES "helpdesk_queue" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("escalationexclusion_id", "queue_id")
)
;
DROP TABLE IF EXISTS helpdesk_ignoreemail_queues CASCADE;
CREATE TABLE "helpdesk_ignoreemail_queues" (
    "id" serial NOT NULL PRIMARY KEY,
    "ignoreemail_id" integer NOT NULL REFERENCES "helpdesk_ignoreemail" ("id") DEFERRABLE INITIALLY DEFERRED,
    "queue_id" integer NOT NULL REFERENCES "helpdesk_queue" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("ignoreemail_id", "queue_id")
)
;


CREATE INDEX "helpdesk_queue_slug" ON "helpdesk_queue" ("slug");
CREATE INDEX "helpdesk_queue_slug_like" ON "helpdesk_queue" ("slug" varchar_pattern_ops);
CREATE INDEX "helpdesk_ticket_queue_id" ON "helpdesk_ticket" ("queue_id");
CREATE INDEX "helpdesk_ticket_submitter_id" ON "helpdesk_ticket" ("submitter_id");
CREATE INDEX "helpdesk_ticket_assigned_to_id" ON "helpdesk_ticket" ("assigned_to_id");
CREATE INDEX "helpdesk_followup_ticket_id" ON "helpdesk_followup" ("ticket_id");
CREATE INDEX "helpdesk_followup_user_id" ON "helpdesk_followup" ("user_id");
CREATE INDEX "helpdesk_ticketchange_followup_id" ON "helpdesk_ticketchange" ("followup_id");
CREATE INDEX "helpdesk_attachment_followup_id" ON "helpdesk_attachment" ("followup_id");
CREATE INDEX "helpdesk_kbcategory_slug" ON "helpdesk_kbcategory" ("slug");
CREATE INDEX "helpdesk_kbcategory_slug_like" ON "helpdesk_kbcategory" ("slug" varchar_pattern_ops);
CREATE INDEX "helpdesk_kbitem_category_id" ON "helpdesk_kbitem" ("category_id");
CREATE INDEX "helpdesk_savedsearch_user_id" ON "helpdesk_savedsearch" ("user_id");
CREATE INDEX "helpdesk_ticketcc_ticket_id" ON "helpdesk_ticketcc" ("ticket_id");
CREATE INDEX "helpdesk_ticketcc_user_id" ON "helpdesk_ticketcc" ("user_id");
