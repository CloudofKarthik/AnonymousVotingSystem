drop table if exists users;
drop table if exists polls cascade;
create table users(id serial primary key, name text, email text, password text);
create table polls(id serial primary key, owner int, poll_name text)


