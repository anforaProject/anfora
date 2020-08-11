use crate::api::APIError;
use crate::db::{
    user::{NewUserProfileForm, User, User_profile},
    user_view::User_view,
};
use crate::DbPool;

use actix_web::error::BlockingError;
use actix_web::{web, App, Error, HttpResponse, HttpServer, Responder};
use diesel::prelude::*;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct Register {
    pub username: String,
    pub email: String,
    pub password: String,
    pub password_confirmation: String,
    pub admin: bool,
}

#[derive(Serialize, Deserialize)]
pub struct LoginResponse {
    pub jwt: String,
}

#[derive(Serialize, Deserialize)]
pub struct UserQuery {
    pub username: Option<String>,
    pub user_id: Option<i32>,
}

pub fn register_user_action(
    form: &Register,
    conn: &PgConnection,
) -> Result<User_profile, APIError> {
    // TODO: Ensure that registrations are open

    // Check that the password match
    if form.password != form.password_confirmation {
        return Err(APIError::err("Password does not match", 400));
    }

    let user_form = NewUserProfileForm {
        username: form.username.to_owned(),
        email: form.email.to_owned(),
        password_secured: form.password.to_owned(),
        is_admin: false,
        can_login: true,
        is_remote: Some(false),
        follower_url: None,
        following_url: None,
        inbox_url: None,
        outbox_url: None,
        webfinger: None,
        shared_inbox: None,
        url: "".to_owned(),
    };

    let user_profile_result = match User_profile::register(conn, &user_form) {
        Ok(profile) => profile,
        Err(e) => return Err(APIError::err("Error registering user", 400)),
    };

    Ok(user_profile_result)
}

pub fn get_user_data_action(form: &UserQuery, conn: &PgConnection) -> Result<User_view, APIError> {
    let mut user_profile: Option<User_view> = match form.username.clone() {
        Some(username) => match User_view::get_by_username(conn, username) {
            Ok(user) => Some(user),
            _ => None,
        },
        _ => None,
    };

    match user_profile {
        Some(user) => return Ok(user),
        _ => {}
    }

    let mut user_profile = match form.user_id {
        Some(id_) => match User_view::get_by_id(conn, id_) {
            Ok(user) => Some(user),
            _ => None,
        },
        _ => None,
    };

    match user_profile {
        Some(user) => return Ok(user),
        _ => {}
    }

    Err(APIError::err(
        "No user found with the given parameters",
        404,
    ))
}

pub async fn register_user(
    pool: web::Data<DbPool>,
    form: web::Json<Register>,
) -> Result<HttpResponse, Error> {
    let conn = pool.get().expect("couldn't get db connection from pool");

    let user = web::block(move || register_user_action(&form, &conn)).await;

    // TODO: Return jwt information
    match user {
        Ok(user) => Ok(HttpResponse::Ok().json(user)),
        Err(BlockingError::Error(e)) => Ok(e.response()),
        Err(BlockingError::Canceled) => Ok(HttpResponse::InternalServerError().finish()),
    }
}

pub async fn get_user_data(
    pool: web::Data<DbPool>,
    form: web::Json<UserQuery>,
) -> Result<HttpResponse, Error> {
    let conn = pool.get().expect("couldn't get db connection from pool");

    let user = web::block(move || get_user_data_action(&form, &conn)).await;

    match user {
        Ok(user) => Ok(HttpResponse::Ok().json(user)),
        Err(BlockingError::Error(e)) => Ok(e.response()),
        Err(BlockingError::Canceled) => Ok(HttpResponse::InternalServerError().finish()),
    }

    // TODO: Return login information instead of the user created
}
