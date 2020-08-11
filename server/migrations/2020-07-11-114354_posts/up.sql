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
    status_type varchar(128) default 'status' not null,
    in_reply_to_id serial references post(id),
    reblog_of_id serial references post(id),
    is_nsfw boolean default false not null,
    visibility varchar(256) default 'public' not null,
    replies_count integer default 0 not null,
    likes_count integer default 0 not null,
    reblogs_count integer default 0 not null,
    views_count integer default 0 not null,
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
    thumbnail_path text not null,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    mimetype varchar(256),
    size smallint,
    orientation varchar(32) default 'portrait' not null,
    metadata json,
    procesed boolean default false not null,
    license text,
    unique(media_path)
);