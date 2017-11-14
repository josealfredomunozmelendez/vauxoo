DROP FUNCTION IF EXISTS get_new_id(cmodel varchar, id_res integer);
CREATE OR REPLACE FUNCTION get_new_id(cmodel varchar, id_res integer)
RETURNS integer AS $$
    DECLARE
        data_name varchar;
        new_id integer;

    BEGIN
        SELECT
            ir_data_name INTO data_name
        FROM
            dblink('con',
                   'SELECT name FROM ir_model_data WHERE model='||
                    quote_literal(cmodel)||' AND res_id='|| id_res) AS
            t1 (ir_data_name varchar);
        SELECT res_id INTO new_id FROM ir_model_data WHERE model=cmodel AND name=data_name LIMIT 1;
    RETURN new_id; END;
    $$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS create_message();
CREATE OR REPLACE FUNCTION create_message()
RETURNS void AS $$
    DECLARE
        msg record;
        ir_data "ir_model_data";
        data_name varchar;
        cmodel varchar;
        new_id integer;
        msg_id integer;
        parent integer;
        uid_write integer;
        rec_id integer;
        uid_create integer;
        id_author integer;
        id_subtype integer;
        chr_subtype varchar;
        new_key varchar;
        models jsonb;
        users jsonb;
        partners jsonb;
        records jsonb;
        data_from_ir jsonb;
        str_id varchar;

    BEGIN
        PERFORM dblink_connect('con' ,
            'host= port= dbname= user= password=');
        SELECT jsonb_build_object('project.product', 'sale.order',
                                 'project.issue', 'helpdesk.ticket') INTO models;
        SELECT
            jsonb_object_agg(name, res_id) INTO data_from_ir
        FROM
            (SELECT
                name,
                res_id
             FROM
                ir_model_data AS ir_data
             WHERE name ilike 'mail_message_imported_vx80_%') AS ir_data;
        FOR msg IN SELECT * FROM dblink('con',
                   'SELECT id, create_date, create_uid, write_date, write_uid, body, model, record_name, '||
                          'date, subject, message_id, parent_id, res_id, subtype_id, author_id, email_from, '||
                          'mail_server_id, no_auto_thread, reply_to, website_published, path '||
                    'FROM mail_message WHERE '||
                    'model IN ('||quote_literal('product.product')||','||
                                  quote_literal('product.template')||','||
                                  quote_literal('project.project')||','||
                                  quote_literal('project.issue')||','||
                                  quote_literal('sale.order')||','||
                                  quote_literal('crm.lead')||','||
                                  quote_literal('project.task')  || ') ORDER BY date ASC') AS
                    t1 (id integer, create_date timestamp(3), create_uid integer, write_date timestamp(3), write_uid integer, body text,
                        model varchar, record_name varchar, date_val timestamp(3), subject varchar, message_id varchar,
                        parent_id integer, res_id integer, subtype_id integer, author_id integer,
                        email_from varchar,mail_server_id integer, no_auto_thread boolean, reply_to varchar,
                        website_published boolean, spath char ) LOOP

            str_id := 'mail_message_imported_vx80_'||msg.id;
            IF (data_from_ir->str_id) IS NOT NULL THEN
                CONTINUE;
            END IF;

            IF (users->msg.write_uid) IS NULL THEN
                SELECT get_new_id('res.users', msg.write_uid) INTO uid_write;
                users := users || jsonb_build_object(msg.write_uid, uid_write);
            ELSE
                uid_write := (SELECT value FROM jsonb_each_text(users) WHERE key=msg.write_uid);
            END IF;

            IF (users->msg.create_uid) IS NULL THEN
                SELECT get_new_id('res.users', msg.create_uid) INTO uid_create;
                users := users || jsonb_build_object(msg.create_uid, uid_create);
            ELSE
                uid_create := (SELECT value FROM jsonb_each_text(users) WHERE key=msg.create_uid);
            END IF;

            IF msg.author_id IS NOT NULL AND (partners->msg.author_id) IS NULL THEN
                SELECT get_new_id('res.partner', msg.author_id) INTO id_author;
                partners := partners || jsonb_build_object(msg.author_id, id_author);
            ELSIF msg.author_id IS NOT NULL AND (partners->msg.author_id) IS NOT NULL THEN
                id_author := (SELECT value FROM jsonb_each_text(partners) WHERE key=msg.author_id);
            END IF;

            IF (models->msg.model) IS NULL THEN
                cmodel := msg.model;
            ELSE
                cmodel := (SELECT value FROM jsonb_each_text(models) WHERE key=msg.model);
            END IF;

            IF msg.parent_id IS NOT NULL THEN
                SELECT value INTO parent FROM jsonb_each_text(data_from_ir) WHERE key='mail_message_imported_vx80_'||msg.parent_id;
            END IF;

            new_key := msg.model||'-'||msg.res_id;
            IF (records->new_key) IS NULL THEN
                SELECT
                    ir_data_name INTO data_name
                FROM
                    dblink('con',
                           'SELECT name FROM ir_model_data WHERE model='||
                            quote_literal(msg.model)||' AND res_id='|| msg.res_id) AS
                    t1 (ir_data_name varchar);
                records := records || jsonb_build_object(new_key, data_name);
            ELSE
                data_name := (SELECT value FROM jsonb_each_text(records) WHERE key=new_key);
            END IF;
            SELECT res_id INTO new_id FROM ir_model_data WHERE model=cmodel AND name=data_name LIMIT 1;

            INSERT INTO mail_message(create_date, create_uid, write_date,
                write_uid, body, model, record_name, date, subject, message_id,
                parent_id, res_id, subtype_id, author_id,
                email_from,mail_server_id, no_auto_thread, reply_to,
                website_published, path, message_type) VALUES
            (msg.create_date, uid_create, msg.write_date, uid_write,
                msg.body, cmodel, msg.record_name, msg.date_val, msg.subject,
                msg.message_id, parent, new_id, msg.subtype_id,
                id_author, msg.email_from, null,
                msg.no_auto_thread, msg.reply_to, msg.website_published,
                msg.spath, 'comment') RETURNING id INTO rec_id;
            INSERT INTO ir_model_data (name, noupdate, date_init, date_update, module, model, res_id) VALUES
            ('mail_message_imported_vx80_'||msg.id, true, NOW(), NOW(), '', 'mail.message', rec_id);
            data_from_ir := data_from_ir || jsonb_build_object('mail_message_imported_vx80_'||msg.id, rec_id);
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS import_followers();
CREATE OR REPLACE FUNCTION import_followers()
RETURNS void AS $$
    DECLARE
        follower record;
        new_id integer;
        cmodels jsonb;
        models jsonb;
        partners jsonb;
        records jsonb;
        partner integer;
        new_key varchar;
        data_name varchar;
        cmodel varchar;
        mname varchar;

    BEGIN
        SELECT jsonb_build_object('project.product', 'sale.order',
                                 'project.issue', 'helpdesk.ticket') INTO cmodels;
        FOR follower IN SELECT * FROM
            dblink('con',
                   'SELECT res_model, res_id, partner_id FROM mail_followers WHERE '||
                    'res_model IN ('||quote_literal('product.product')||','||
                                  quote_literal('product.template')||','||
                                  quote_literal('project.project')||','||
                                  quote_literal('project.issue')||','||
                                  quote_literal('sale.order')||','||
                                  quote_literal('crm.lead')||','||
                                  quote_literal('project.task')  || ')') AS
            t1 (res_model varchar, res_id integer, partner_id integer) LOOP

            IF (cmodels->follower.res_model) IS NULL THEN
                cmodel := follower.res_model;
            ELSE
                cmodel := (SELECT value FROM jsonb_each_text(cmodels) WHERE key=follower.res_model);
            END IF;

            IF (partners->follower.partner_id) IS NULL THEN
                SELECT get_new_id('res.partner', follower.partner_id) INTO partner;
                partners := partners || jsonb_build_object(follower.partner_id, partner);
            ELSE
                partner := (SELECT value FROM jsonb_each_text(partners) WHERE key=follower.partner_id);
            END IF;

            new_key := follower.res_model||'-'||follower.res_id;
            IF (records->new_key) IS NULL THEN
                SELECT
                    ir_data_name INTO data_name
                FROM
                    dblink('con',
                           'SELECT name FROM ir_model_data WHERE model='||
                            quote_literal(follower.res_model)||' AND res_id='|| follower.res_id) AS
                    t1 (ir_data_name varchar);
                records := records || jsonb_build_object(new_key, data_name);
            ELSE
                data_name := (SELECT value FROM jsonb_each_text(records) WHERE key=new_key);
            END IF;
            SELECT res_id INTO new_id FROM ir_model_data WHERE model=cmodel AND name=data_name LIMIT 1;

            IF new_id iS NOT NULL AND
                NOT EXISTS (SELECT res_id FROM mail_followers WHERE res_model=cmodel AND res_id=new_id AND partner_id=partner) AND
                partner IS NOT NULL THEN
                INSERT INTO mail_followers(res_model, res_id, partner_id) VALUES
                                    (cmodel, new_id, partner);
            END IF;

        END LOOP;
    END;
    $$ LANGUAGE plpgsql;

SELECT create_message();
SELECT import_followers();
