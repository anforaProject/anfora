use diesel::prelude::PgConnection;
use diesel::dsl::{insert_into};
use diesel::result::Error;
use diesel;
use crate::schema::{user_, user_::dsl::*, user_profile, user_profile::dsl::*};
use argon2::{self, Config};

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

#[derive(Insertable, Clone, Debug)]]
#[table_name="user_"]
pub struct NewUser{
    pub username: String,
    pub email: String,
    pub password_secured: String,
    pub is_admin: bool,
    pub can_login: bool,
}

impl User{
    pub fn create(conn: &PgConnection, user: &NewUser)->Result<Self, Error>{
        insert_into(user_).values(user).get_result::<Self>(conn)
    }

    pub fn read(conn: &PgConnection, user_id: i32)-> Result<Self, Error>{
        user_find(user_id).first::<Self>(conn)
    }
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

#[derive(Clone, Debug)]]
#[table_name="user_profile"]
pub struct NewUserProfileForm{
    pub username: String,
    pub email: String,
    pub password_secured: String,
    pub is_admin: bool,
    pub can_login: bool,
    pub inbox_url Option<String>,
    pub outbox_url Option<String>,
    pub follower_url Option<String>,
    pub following_url Option<String>,
    pub shared_inbox Option<String>,
    pub webfinger Option<String>,

    pub is_remote: Option<bool>
}

#[derive(Insertable, Clone, Debug)]]
#[table_name="user_profile"]
pub struct NewUserProfile{
    pub user_id: i32,
    pub inbox_url Option<String>,
    pub outbox_url Option<String>,
    pub follower_url Option<String>,
    pub following_url Option<String>,
    pub shared_inbox Option<String>,
    pub webfinger Option<String>,

    pub is_remote: Option<bool>
}

impl User_profile{
    pub fn register(conn: &PgConnection, user: &NewUserProfileForm) -> Result<Self, Error>{
        let mut new_user = form.clone();
        // TODO: Take this salt from other place
        let salt = b"randomsalt213123123";
        let config = Config::default();

        let hashed_password = argon2::hash_encoded(form.password_secured, salt, &config)
                                        .expect("Error hashing password");
        
        new_user.password_secured = hashed_password;

        // TODO: Add outbox_url, inbos_url ....

        Self::create(&conn, &new_user)
    }

    fn create(conn: &PgConnection, new_user_profile: &NewUserProfileForm)->Result<Self, Error>{

        let new_user = NewUser{
            username: new_user_profile.username,
            email: new_user_profile.email,
            password_secured: new_user_profile.password_secured,
            is_admin: new_user_profile.is_admin,
            can_login: new_user_profile.can_login
        };

        let user = new_user.create(conn, new_user).expect("Error crating user for profile");

        let new_profile = NewUserProfile{
            user_id: user.id,
            // TODO: Update the AP urls
        }

        insert_into(user_profile).values(new_profile).get_result::<Self>(conn)
    }
}

