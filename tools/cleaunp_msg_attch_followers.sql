delete from mail_message;
delete from ir_attachment;
delete from mail_followers;
delete from ir_model_data where model = 'mail.message';
delete from ir_model_data where model = 'ir.attachment';
VACUUM FULL;
