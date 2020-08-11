use diesel::dsl::*;
use diesel::prelude::PgConnection;
use diesel::result::Error;
use diesel::*;
use serde::{Deserialize, Serialize};

table! {
    user_view (id) {
        id -> Int4,
        username -> Varchar,
        acct -> Varchar,
        name -> Nullable<Text>,
        note -> Nullable<Text>,
        locked -> Bool,
        avatar -> Nullable<Text>,
        header -> Nullable<Text>,
        followers_count -> Int4,
        following_count -> Int4,
        statuses_count -> Int4,
    }
}

#[derive(Queryable, Identifiable, PartialEq, Debug, Serialize, Deserialize, Clone)]
#[table_name = "user_view"]
pub struct User_view {
    pub id: i32,
    pub username: String,
    pub acct: String,
    pub name: Option<String>,
    pub note: Option<String>,
    pub locked: bool,
    pub avatar: Option<String>,
    pub header: Option<String>,
    pub followers_count: i32,
    pub following_count: i32,
    pub statuses_count: i32,
}

impl User_view {
    pub fn get_by_username(conn: &PgConnection, username_provided: String) -> Result<Self, Error> {
        user_view::table
            .filter(user_view::username.eq(username_provided.to_owned()))
            .first::<Self>(conn)
    }

    pub fn get_by_id(conn: &PgConnection, id_provided: i32) -> Result<Self, Error> {
        user_view::table
            .filter(user_view::id.eq(id_provided))
            .first::<Self>(conn)
    }
}
