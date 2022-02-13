ALTER TABLE chats ALTER COLUMN type TYPE text USING type[1];
ALTER TABLE users ADD COLUMN is_bot BOOLEAN DEFAULT false;
ALTER TABLE users drop CONSTRAINT idx_16418_primary;
ALTER TABLE users ADD COLUMN id BIGSERIAL PRIMARY KEY;
ALTER TABLE users RENAME COLUMN user_id TO tg_id;

ALTER TABLE settings DROP CONSTRAINT settings_ibfk_1;
ALTER TABLE val_as_for_chat DROP CONSTRAINT val_as_for_chat_ibfk_1;
ALTER TABLE chats DROP CONSTRAINT idx_16399_primary;
ALTER TABLE chats ADD COLUMN id BIGSERIAL PRIMARY KEY;
ALTER TABLE chats RENAME COLUMN chat_id TO tg_id;
ALTER TABLE chats RENAME COLUMN type_ TO type;

CREATE TABLE alembic_version (
    version_num varchar
);
INSERT INTO alembic_version values ('898ec90733e2');
