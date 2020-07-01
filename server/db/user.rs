#[derive(Debug, Queryable)]
#[table_name = "user_"]
pub struct User{
    pub id: i32,
    pub username: String,
    pub email: String,
    pub password_secured: String,
    pub is_admin: bool,
    pub is_banned: bool,
    pub can_login: bool,
    pub created_at: chrono::NaiveDateTime,
    pub updated_at: chrono::NaiveDateTime,
    pub deleted_at: Option<chrono::NaiveDateTime>,
    pub email_verified_at: Option<chrono::NaiveDateTime>,
    pub is_twofa_enabled: bool,
    pub twofa_codes: Option<diesel::pg::types::sql_types::Json>,
    pub twofa_secret: Option<String>m
    pub twofa_setup_at: Option<chrono::NaiveDateTime>,
    pub delete_after: Option<chrono::NaiveDateTime>
}

#[derive(Debug, Queryable)]
#[table_name = "user_profile"]
pub struct User_profile{
    pub user_id: i32,
    pub domain: Option<String>,
    pub status: Option<String>,
    pub name: Option<String>,
    pub bio: Option<String>,
    pub is_private: bool,
    pub is_artist: bool,
    pub website: Option<String>,
    pub avatar_url: Option<String>,
    pub header_url: Option<String>,
    pub profile_layout: String,
    pub location: Option<String>,
    pub is_recommendable: bool,
    pub is_remote: bool,
    pub private_key: Option<String>,
    pub public_key: Option<String>,
    pub unlisted: bool,
    pub inbox_url: Option<String>,
    pub outbox_url: Option<String>,
    pub follower_url: Option<String>,
    pub following_url: Option<String>,
    pub shared_inbox: Option<String>,
    pub webfinger: Option<String>
}