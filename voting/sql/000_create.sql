drop table if exists polls cascade;
drop table if exists users;

create table users(id serial primary key, name text, email text, password text);
create table polls(id serial primary key, owner int, poll_name text, no_of_options int, deadline date, constraint fk_poll foreign key(owner) REFERENCES users(id));


