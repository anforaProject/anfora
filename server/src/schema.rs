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
        inbox_url -> Nullable<Text>,
        outbox_url -> Nullable<Text>,
        follower_url -> Nullable<Text>,
        following_url -> Nullable<Text>,
        shared_inbox -> Nullable<Text>,
        webfinger -> Nullable<Text>,
    }
}

joinable!(user_profile -> user_ (user_id));

allow_tables_to_appear_in_same_query!(
    user_,
    user_profile,
);
