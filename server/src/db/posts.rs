use diesel::prelude::PgConnection;
use diesel::dsl::*;
use diesel::result::Error;
use diesel::*;
use crate::schema::{post, post::dsl::*, place, place::dsl::*, media, media::dsl::*};
use argon2::{self, Config};
use serde::{Serialize, Deserialize};
use serde_json;

#[derive(Debug, Clone, Queryable, Identifiable)]
#[table_name = "post"]
pub struct Post { 
    pub id: i32,
    pub uri: Option<String>,
    pub caption: Option<String>,
    pub profile_id: i32,
    pub status_type: String,
    pub in_reply_to_id: Option<i32>,
    pub reblog_of_id: Option<i32>,
    pub is_nsfw: bool,
    pub visibility: String,
    pub replies_count: u32,
    pub likes_count: u32,
    pub reblogs_count: u32,
    pub views_count: u32,
    pub lang: Option<String>,
    pub created_at: chrono::NaiveDateTime,
    pub updated_at: chrono::NaiveDateTime,
    pub delete_at: Option<chrono::NaiveDateTime>,
    pub location_id: Option<i32>
}

#[derive(Debug, Clone, Queryable, Identifiable)]
#[table_name = "media"]
pub struct Media{
    pub id: i32,
    pub status_id: i32,
    pub profile_id: i32,
    pub media_path: String,
    pub reference: Option<String>
    pub thumbnail_path: String,
    pub created_at: chrono::NaiveDateTime,
    pub updated_at: chrono::NaiveDateTime,
    pub mimetype: Option<String>,
    pub size: Option<i16>,
    pub orientation: String,
    pub metadata: Option<serde_json::Value>,
    pub procesed: bool,
    pub license: Option<String>
}

#[derive(Debug, Clone, Queryable, Identifiable)]
#[table_name = "place"]
pub struct Place{
    pub id: i32,
    pub identifaction: Option<String>,
    pub country: Option<String>,
    pub lat: Option<i32>,
    pub lon: Option<i32>,
    pub created_at: chrono::NaiveDateTime,
    pub updated_at: chrono::NaiveDateTime,
}

#[derive(Serialize, Deserialize, Insertable, AsChangeset, Clone, Debug)]
#[table_name="post"]
pub struct NewPost{
    pub uri: Option<String>,
    pub caption: Option<String>,
    pub profile_id: i32,
    pub status_type: Option<String>,
    pub in_reply_to_id: Option<i32>,
    pub reblog_of_id: Option<i32>,
    pub is_nsfw: bool,
    pub visibility: Option<String>,
    pub lang: Option<String>,
    pub delete_at: Option<chrono::NaiveDateTime>,
    pub location_id: Option<i32>
}

#[derive(Serialize, Deserialize, Insertable, AsChangeset, Clone, Debug)]
#[table_name="media"]
pub struct NewMedia{
    pub status_id: i32,
    pub profile_id: i32,
    pub media_path: String,
    pub reference: Option<String>
    pub thumbnail_path: String,
    pub mimetype: Option<String>,
    pub size: Option<i16>,
    pub orientation: String,
    pub metadata: Option<serde_json::Value>,
    pub procesed: bool,
    pub license: Option<String>
}

#[derive(Serialize, Deserialize, Insertable, AsChangeset, Clone, Debug)]
#[table_name = "place"]
pub struct NewPlace{
    pub identifaction: Option<String>,
    pub country: Option<String>,
    pub lat: Option<i32>,
    pub lon: Option<i32>
}

impl Place {
    pub fn create(conn: &PgConnection, place_form: &NewPlace)->Result<Self, Error>{
        insert_into(place).values(place_form).get_result::<Self>(conn)
    }

    pub fn get_by_id(conn: &PgConnection, id_of_place:i32)->Result<Self, Error>{
        place.find(id_of_place).first::<Self>(conn)
    }
}

impl Media{
    pub fn create(conn: &PgConnection, media_form: &NewMedia)->Result<Self, Error>{
        insert_into(media).values(media_form).get_result::<Self>(conn)
    }

    pub fn get_by_id(conn: &PgConnection, id_of_media:i32)->Result<Self, Error>{
        media.find(id_of_media).first::<Self>(conn)
    }  
}

impl Post{
    pub fn create(conn: &PgConnection, post_form: &NewPost)->Result<Self, Error>{
        insert_into(post).values(post_form).get_result::<Self>(conn)
    }

    pub fn get_by_id(conn: &PgConnection, id_of_post:i32)->Result<Self, Error>{
        post.find(id_of_post).first::<Self>(conn)
    }  
}