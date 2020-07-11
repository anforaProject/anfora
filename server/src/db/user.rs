use diesel::prelude::PgConnection;
use diesel::dsl::*;
use diesel::result::Error;
use diesel::*;
use crate::schema::{user_, user_::dsl::*, user_profile, user_profile::dsl::*};
use argon2::{self, Config};
use serde::{Serialize, Deserialize};
use serde_json;

#[derive(Identifiable, PartialEq, Clone, Debug, Queryable)]
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
    pub twofa_codes: Option<serde_json::Value>,
    pub twofa_secret: Option<String>,
    pub twofa_setup_at: Option<chrono::NaiveDateTime>,
    pub delete_after: Option<chrono::NaiveDateTime>
}

#[derive(Serialize, Deserialize, Insertable, AsChangeset, Clone, Debug)]
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

    pub fn read(conn: &PgConnection, id_of_user: i32)-> Result<Self, Error>{
        user_.find(id_of_user).first::<Self>(conn)
    }
}

#[derive(Serialize, Deserialize, Debug, Queryable, AsChangeset)]
#[table_name="user_profile"]
pub struct User_profile{
    pub user_id: i32,
    pub domain: Option<String>,
    pub status: Option<String>,
    pub name: Option<String>,
    pub bio: Option<String>,
    pub is_private: Option<bool>,
    pub is_artist: Option<bool>,
    pub website: Option<String>,
    pub avatar_url: Option<String>,
    pub header_url: Option<String>,
    pub profile_layout: Option<String>,
    pub location: Option<String>,
    pub is_recommendable: Option<bool>,
    pub is_remote: Option<bool>,
    pub private_key: Option<String>,
    pub public_key: Option<String>,
    pub unlisted: Option<bool>,
    pub inbox_url: Option<String>,
    pub outbox_url: Option<String>,
    pub follower_url: Option<String>,
    pub following_url: Option<String>,
    pub shared_inbox: Option<String>,
    pub webfinger: Option<String>
}

#[derive(Clone, Debug)]
pub struct NewUserProfileForm{
    pub username: String,
    pub email: String,
    pub password_secured: String,
    pub is_admin: bool,
    pub can_login: bool,
    pub inbox_url: Option<String>,
    pub outbox_url: Option<String>,
    pub follower_url: Option<String>,
    pub following_url: Option<String>,
    pub shared_inbox: Option<String>,
    pub webfinger: Option<String>,

    pub is_remote: Option<bool>
}

#[derive(Insertable, AsChangeset, Clone, Debug)]
#[table_name="user_profile"]
pub struct NewUserProfile{
    pub user_id: i32,
    pub inbox_url: Option<String>,
    pub outbox_url: Option<String>,
    pub follower_url: Option<String>,
    pub following_url: Option<String>,
    pub shared_inbox: Option<String>,
    pub webfinger: Option<String>,

    pub is_remote: Option<bool>
}

impl User_profile{
    pub fn register(conn: &PgConnection, user: &NewUserProfileForm) -> Result<Self, Error>{
        let mut new_user = user.clone();
        // TODO: Take this salt from other place
        let salt = b"randomsalt213123123";
        let config = Config::default();

        let hashed_password = argon2::hash_encoded(user.password_secured.as_bytes(), salt, &config)
                                        .expect("Error hashing password");
        
        new_user.password_secured = hashed_password;

        // TODO: Add outbox_url, inbox_url ....

        Self::create(&conn, &new_user)
    }

    fn create(conn: &PgConnection, new_user_profile: &NewUserProfileForm)->Result<Self, Error>{

        let new_user = NewUser{
            username: new_user_profile.username.to_owned(),
            email: new_user_profile.email.to_owned(),
            password_secured: new_user_profile.password_secured.to_owned(),
            is_admin: new_user_profile.is_admin,
            can_login: new_user_profile.can_login
        };

        let user = User::create(conn, &new_user).expect("Error crating user for profile");

        let new_profile = NewUserProfile{
            user_id: user.id,
            inbox_url: new_user_profile.inbox_url.to_owned(),
            outbox_url: new_user_profile.outbox_url.to_owned(),
            follower_url: new_user_profile.follower_url.to_owned(),
            following_url: new_user_profile.following_url.to_owned(),
            shared_inbox: new_user_profile.shared_inbox.to_owned(),
            webfinger: new_user_profile.webfinger.to_owned(),
            is_remote: new_user_profile.is_remote.to_owned(),
            // TODO: Update the AP urls
        };

        insert_into(user_profile).values(new_profile).get_result::<Self>(conn)
    }
}

