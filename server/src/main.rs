use actix_form_data::{Error, Field, Form, Value};
use futures::stream::StreamExt;

use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use anfora_server::routes::{api as routeAPI};
use diesel::prelude::*;
use diesel::r2d2::{self, ConnectionManager, Pool};
use anfora_server::api;

extern crate env_logger;

struct Gen;

pub type DbPool = Pool<ConnectionManager<PgConnection>>;

async fn index(
    pool: web::Data<DbPool>
) -> impl Responder {
    HttpResponse::Ok().body("Hello world!")
}

async fn index2(
    pool: web::Data<DbPool>
) -> impl Responder {
    HttpResponse::Ok().body("Server is receiving requests")
}

#[actix_rt::main]
async fn main() -> std::io::Result<()> {

    // set r2d2 connection to db
    let connspec = std::env::var("DATABASE_URL").expect("DATABASE_URL");
    let manager = ConnectionManager::<PgConnection>::new(connspec);

    env_logger::init();

    let pool = r2d2::Pool::builder()
    .build(manager)
    .expect("Failed to create pool.");

    let upload_media_form = Form::new()
    .field("field-name", Field::text())
    .field(
        "files",
        Field::file(|_, _, mut stream| async move {
            while let Some(res) = stream.next().await {
                res?;
            }
            Ok(None) as Result<_, Error>
        }),
    );


    HttpServer::new(move || {
        App::new()
            .data(pool.clone())
            .wrap(actix_web::middleware::Logger::default())
            .route("/", web::get().to(index))
            .route("/health", web::get().to(index2))
            .configure(routeAPI::config)
            .wrap(upload_media_form.clone())
            .service(
                web::resource("/media/upload")
                    .route(web::post().to(api::uploads::upload))
            )
    })
    .bind("127.0.0.1:8000")?
    .run()
    .await
}
