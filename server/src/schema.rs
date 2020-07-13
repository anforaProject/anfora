table! {
    media (id) {
        id -> Int4,
        status_id -> Int4,
        profile_id -> Int4,
        media_path -> Text,
        reference -> Nullable<Text>,
        thumbnail_path -> Nullable<Text>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        mimetype -> Nullable<Varchar>,
        size -> Nullable<Int2>,
        orientation -> Nullable<Varchar>,
        metadata -> Nullable<Json>,
        procesed -> Nullable<Bool>,
        license -> Nullable<Text>,
    }
}

table! {
    place (id) {
        id -> Int4,
        identification -> Nullable<Varchar>,
        country -> Nullable<Varchar>,
        lat -> Nullable<Numeric>,
        lon -> Nullable<Numeric>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
    }
}

table! {
    post (id) {
        id -> Int4,
        uri -> Nullable<Text>,
        caption -> Nullable<Varchar>,
        profile_id -> Int4,
        status_type -> Nullable<Varchar>,
        in_reply_to_id -> Int4,
        reblog_of_id -> Int4,
        is_nsfw -> Nullable<Bool>,
        visibility -> Nullable<Varchar>,
        replies_count -> Nullable<Int4>,
        likes_count -> Nullable<Int4>,
        reblogs_count -> Nullable<Int4>,
        lang -> Nullable<Varchar>,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        delete_at -> Nullable<Timestamp>,
        location_id -> Int4,
    }
}

table! {
    user_ (id) {
        id -> Int4,
        username -> Varchar,
        email -> Text,
        password_secured -> Text,
        is_admin -> Bool,
        is_banned -> Bool,
        can_login -> Bool,
        created_at -> Timestamp,
        updated_at -> Timestamp,
        deleted_at -> Nullable<Timestamp>,
        email_verified_at -> Nullable<Timestamp>,
        is_twofa_enabled -> Bool,
        twofa_codes -> Nullable<Json>,
        twofa_secret -> Nullable<Text>,
        twofa_setup_at -> Nullable<Timestamp>,
        delete_after -> Nullable<Timestamp>,
    }
}

table! {
    user_profile (user_id) {
        user_id -> Int4,
        domain -> Nullable<Text>,
        status -> Nullable<Text>,
        name -> Nullable<Text>,
        bio -> Nullable<Text>,
        is_private -> Nullable<Bool>,
        is_artist -> Nullable<Bool>,
        website -> Nullable<Text>,
        avatar_url -> Nullable<Text>,
        header_url -> Nullable<Text>,
        profile_layout -> Nullable<Varchar>,
        location -> Nullable<Varchar>,
        is_recommendable -> Nullable<Bool>,
        is_remote -> Nullable<Bool>,
        private_key -> Nullable<Text>,
        public_key -> Nullable<Text>,
        unlisted -> Nullable<Bool>,
        followers_count -> Int4,
        following_count -> Int4,
        statuses_count -> Int4,
        inbox_url -> Nullable<Text>,
        outbox_url -> Nullable<Text>,
        follower_url -> Nullable<Text>,
        following_url -> Nullable<Text>,
        shared_inbox -> Nullable<Text>,
        webfinger -> Nullable<Text>,
        url -> Text,
    }
}

joinable!(media -> post (status_id));
joinable!(media -> user_profile (profile_id));
joinable!(post -> place (location_id));
joinable!(post -> user_profile (profile_id));
joinable!(user_profile -> user_ (user_id));

allow_tables_to_appear_in_same_query!(
    media,
    place,
    post,
    user_,
    user_profile,
);
