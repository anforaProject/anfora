use actix_form_data::{Field, Form, Value, Error, FileMeta};
use actix_web::{http::StatusCode,HttpResponse, ResponseError};
use bytes::Bytes;
use futures::stream::{Stream, TryStreamExt};
use crate::api::APIError;

use std::{pin::Pin};
use std::path::{Path, PathBuf};

use uuid::Uuid;

//use crate::db::posts as dbposts;

#[derive(Clone, Debug, serde::Deserialize, serde::Serialize)]
pub struct JsonError {
    msg: String,
}

impl<T> From<T> for JsonError
where
    T: std::error::Error,
{
    fn from(e: T) -> Self {
        JsonError {
            msg: format!("{}", e),
        }
    }
}

#[derive(Clone, Debug, serde::Deserialize, serde::Serialize, thiserror::Error)]
#[error("Errors occurred")]
pub struct Errors {
    errors: Vec<JsonError>,
}

impl From<JsonError> for Errors {
    fn from(e: JsonError) -> Self {
        Errors { errors: vec![e] }
    }
}

impl ResponseError for Errors {
    fn status_code(&self) -> StatusCode {
        StatusCode::BAD_REQUEST
    }

    fn error_response(&self) -> HttpResponse {
        HttpResponse::BadRequest().json(self)
    }
}




pub async fn upload(uploaded_content: Value) -> HttpResponse {
    //println!("Uploaded Content: {:#?}", uploaded_content.copy().map());

    // TODO: Insert media here
    //let path = Path::new(uploaded_content.map().get("file").unwrap());

    let filepath = match uploaded_content.map(){
        Some(mut map) => {
            match map.remove("file"){
                Some(filemeta) => {
                    match filemeta.file(){
                        Some(filemeta) => filemeta.saved_as.unwrap().clone(),
                        _ => PathBuf::from("/")
                    }                   
                },
                _ => PathBuf::from("/")
            }
        },
        _ => PathBuf::from("/")
    };

    let filename = match filepath.file_name(){
        Some(name) => name.to_str().unwrap(),
        None => ""
    };

    println!("{:?}",filename);

    HttpResponse::Created().finish()

}


pub async fn save_file(
    filename: String,
    ctype: String,
    stream: Pin<Box<dyn Stream<Item = Result<Bytes, Error>>>>,
)->Result<String, JsonError>{
    println!("{} {}", filename, ctype);

    let stream = stream.err_into::<JsonError>();    

    let uuid = Uuid::new_v4();
    // TODO: Add extension to file 
    let name = format!("/home/yabirgb/anfora_uploads/{}", uuid.to_simple());

    let file = actix_fs::file::create(name.clone()).await?;

    if let Err(e) = actix_fs::file::write_stream(file, stream).await {
        actix_fs::remove_file(filename.clone()).await?;
        return Err(e);
    }

    Ok(name)

}