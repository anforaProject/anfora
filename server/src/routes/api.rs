use crate::{api::{user::*}};

use actix_web::{client::Client, error::ErrorBadRequest, *};
use serde::Serialize;

pub fn config(cfg: &mut web::ServiceConfig){
    cfg.service(
        web::scope("/api/v1")
            .service(
                web::resource("/user/register")
                    .route(web::post().to(register_user))
            )
    );    
}
