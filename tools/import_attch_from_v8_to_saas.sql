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

DROP FUNCTION IF EXISTS create_attachment();
CREATE OR REPLACE FUNCTION create_attachment()
RETURNS void AS $$
    DECLARE
        att record;
        data_name varchar;
        cmodel varchar;
        new_id integer;
        att_id integer;
        uid_write integer;
        rec_id integer;
        uid_create integer;
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
             WHERE name ilike 'attchament_imported_vx80_%') AS ir_data;
        FOR att IN SELECT * FROM dblink('con',
                   'SELECT id, datas_fname, url, name, mimetype, store_fname, type, index_content, res_id, '||
                   'company_id, create_uid, file_size, db_datas, res_name, write_uid, res_model, write_date, create_date'||
                    ' FROM ir_attachment WHERE '||
                    'res_model IN ('||quote_literal('product.product')||','||
                                  quote_literal('product.template')||','||
                                  quote_literal('project.project')||','||
                                  quote_literal('project.issue')||','||
                                  quote_literal('sale.order')||','||
                                  quote_literal('crm.lead')||','||
                                  quote_literal('project.task')  || ')') AS
                    t1 (id integer, datas_fname varchar, url varchar, name varchar, mimetype varchar,
                        store_fname varchar, type varchar, index_content text, res_id integer, company_id integer,
                        create_uid integer, file_size integer, db_datas bytea, res_name varchar, write_uid integer,
                        res_model varchar, write_date timestamp(3), create_date timestamp(3)) LOOP

            str_id := 'attchament_imported_vx80_'||att.id;
            IF (data_from_ir->str_id) IS NOT NULL THEN
                CONTINUE;
            END IF;

            IF (users->att.write_uid) IS NULL THEN
                SELECT get_new_id('res.users', att.write_uid) INTO uid_write;
                users := users || jsonb_build_object(att.write_uid, uid_write);
            ELSE
                uid_write := (SELECT value FROM jsonb_each_text(users) WHERE key=att.write_uid);
            END IF;

            IF (users->att.create_uid) IS NULL THEN
                SELECT get_new_id('res.users', att.create_uid) INTO uid_create;
                users := users || jsonb_build_object(att.create_uid, uid_create);
            ELSE
                uid_create := (SELECT value FROM jsonb_each_text(users) WHERE key=att.create_uid);
            END IF;


            IF (models->att.res_model) IS NULL THEN
                cmodel := att.res_model;
            ELSE
                cmodel := (SELECT value FROM jsonb_each_text(models) WHERE key=att.res_model);
            END IF;

            new_key := att.res_model||'-'||att.res_id;
            IF (records->new_key) IS NULL THEN
                SELECT
                    ir_data_name INTO data_name
                FROM
                    dblink('con',
                           'SELECT name FROM ir_model_data WHERE model='||
                            quote_literal(att.res_model)||' AND res_id='|| att.res_id) AS
                    t1 (ir_data_name varchar);
                records := records || jsonb_build_object(new_key, data_name);
            ELSE
                data_name := (SELECT value FROM jsonb_each_text(records) WHERE key=new_key);
            END IF;
            SELECT res_id INTO new_id FROM ir_model_data WHERE model=cmodel AND name=data_name LIMIT 1;

            INSERT INTO ir_attachment(datas_fname, url, name, mimetype,
                store_fname, type, index_content, res_id, company_id,
                create_uid, file_size, db_datas, res_name, write_uid,
                res_model, write_date, create_date) VALUES
            (att.datas_fname, att.url, att.name, att.mimetype,
                att.store_fname, att.type, att.index_content, new_id, 1,
                uid_create, att.file_size, att.db_datas, att.res_name, uid_write,
                cmodel, att.write_date, att.create_date) RETURNING id INTO rec_id;
            INSERT INTO ir_model_data (name, noupdate, date_init, date_update, module, model, res_id) VALUES
            ('attchament_imported_vx80_'||att.id, true, NOW(), NOW(), '', 'ir.attachment', rec_id);
            data_from_ir := data_from_ir || jsonb_build_object('attchament_imported_vx80_'||att.id, rec_id);
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS link_attachment();
CREATE OR REPLACE FUNCTION link_attachment()
RETURNS integer AS $$
    DECLARE
        data_name varchar;
        new_id integer;
        att record;
        att_id integer;
        msg_id integer;
        data_from_ir_att jsonb;
        data_from_ir_msg jsonb;

    BEGIN
        SELECT
            jsonb_object_agg(name, res_id) INTO data_from_ir_att
        FROM
            (SELECT
                name,
                res_id
             FROM
                ir_model_data AS ir_data
             WHERE name ILIKE 'attchament_imported_vx80_%') AS ir_data;
        SELECT
            jsonb_object_agg(name, res_id) INTO data_from_ir_msg
        FROM
            (SELECT
                name,
                res_id
             FROM
                ir_model_data AS ir_data
             WHERE name ILIKE 'mail_message_imported_vx80_%') AS ir_data;
        FOR att IN SELECT * FROM dblink('con',
                   'SELECT message_id, attachment_id FROM message_attachment_rel') AS
                    t1 (message_id integer, attachment_id integer) LOOP

            SELECT value INTO att_id FROM jsonb_each_text(data_from_ir_att) WHERE key='attchament_imported_vx80_'||att.attachment_id;
            SELECT value INTO msg_id FROM jsonb_each_text(data_from_ir_msg) WHERE key='mail_message_imported_vx80_'||att.message_id;
            IF att_id IS NOT NULL AND msg_id IS NOT NULL AND NOT EXISTS(SELECT message_id FROM message_attachment_rel WHERE attachment_id=att_id AND message_id=msg_id) THEN
                INSERT INTO message_attachment_rel(message_id, attachment_id) VALUES (msg_id, att_id);
            END IF;
        END LOOP;
    RETURN new_id; END;
    $$ LANGUAGE plpgsql;
SELECT create_attachment();
SELECT link_attachment();
