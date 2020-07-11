use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use anfora_server::routes::{api};
use diesel::prelude::*;
use diesel::r2d2::{self, ConnectionManager, Pool};

extern crate env_logger;

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

    HttpServer::new(move || {
        App::new()
            .data(pool.clone())
            .wrap(actix_web::middleware::Logger::default())
            .route("/", web::get().to(index))
            .route("/health", web::get().to(index2))
            .configure(api::config)
    })
    .bind("127.0.0.1:8000")?
    .run()
    .await
}
