-- Your SQL goes here

create table user_(
    id serial primary key,
    username varchar(32) not null unique,
    email text unique not null,
    password_secured text not null,
    is_admin boolean default false not null,
    is_banned boolean default false not null,
    can_login boolean default true not null,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    deleted_at timestamp,
    email_verified_at timestamp,
    is_twofa_enabled boolean default false not null,
    twofa_codes json,
    twofa_secret text,
    twofa_setup_at timestamp,
    delete_after timestamp
);

create table user_profile (
    user_id serial references user_(id) ON DELETE CASCADE primary key,
    domain text,
    status text,
    name text,
    bio text,
    is_private boolean default false,
    is_artist boolean default false,
    website text,
    avatar_url text,
    header_url text,
    profile_layout varchar(40) default 'default',
    location varchar(256),
    is_recommendable boolean default true,
    is_remote boolean default false,
    private_key text,
    public_key text,
    unlisted boolean default true,
    followers_count integer default 0 not null,
    following_count integer default 0 not null,
    statuses_count integer default 0 not null,
    -- Activity pub things
    inbox_url text,
    outbox_url text,
    follower_url text,
    following_url text,
    shared_inbox text,
    webfinger text,
    -- Retrieval information
    url text not null
);
