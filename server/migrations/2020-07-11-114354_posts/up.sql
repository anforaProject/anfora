-- Your SQL goes here
create table place(
    id serial primary key,
    identification varchar(256),
    country varchar(64),
    lat decimal,
    lon decimal,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now()
);

create table post(
    id serial primary key,
    uri text,
    caption varchar(750),
    profile_id serial references user_profile(user_id) on delete cascade not null,
    status_type varchar(128) default 'status',
    in_reply_to_id serial,
    reblog_of_id serial,
    is_nsfw boolean,
    visibility varchar(256),
    replies_count integer,
    likes_count integer,
    reblogs_count integer,
    lang varchar(64),
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    delete_at timestamp,
    location_id serial references place(id)
);


create table media(
    id serial primary key,
    status_id serial references post(id),
    profile_id serial references user_profile(user_id) not null,
    media_path text not null,
    reference text, -- hash of the file
    thumbnail_path text,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    mimetype varchar(256),
    size smallint,
    orientation varchar(32) default 'portrait',
    metadata json,
    procesed boolean default false,
    license text,
    unique(media_path)
);