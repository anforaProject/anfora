use actix_web::http::StatusCode;
use actix_web::{web, HttpResponse, ResponseError};
use serde_json::{json, to_string_pretty};
pub mod uploads;
pub mod user;

#[derive(Fail, Debug)]
#[fail(display = "{{\"error\":\"{}\"}}", message)]
pub struct APIError {
    pub message: String,
    pub code: u16,
}

impl APIError {
    pub fn err(msg: &str, cod: u16) -> Self {
        APIError {
            message: msg.to_string(),
            code: cod,
        }
    }

    pub fn response(&self) -> HttpResponse {
        let err_json = json!({"Error": &self.message});
        HttpResponse::build(StatusCode::from_u16(self.code).unwrap()).json(err_json)
    }
}

impl ResponseError for APIError {
    // builds the actual response to send back when an error occurs
    fn error_response(&self) -> web::HttpResponse {
        let err_json = json!({ "error": self.message });
        web::HttpResponse::build(StatusCode::from_u16(404).unwrap()).json(err_json)
    }
}
