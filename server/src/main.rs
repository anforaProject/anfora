use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use ::routes;
use crate::DbPool

async fn index(
    pool: web::Data<DbPool>
) -> impl Responder {
    HttpResponse::Ok().body("Hello world!")
}

async fn index2(
    pool: web::Data<DbPool>
) -> impl Responder {
    HttpResponse::Ok().body("Hello world again!")
}

#[actix_rt::main]
async fn main() -> std::io::Result<()> {

    // set r2d2 connection to db
    let connspec = std::env::var("DATABASE_URL").expect("DATABASE_URL");
    let manager = ConnectionManager::<PgConnection>::new(connspec);

    let pool = r2d2::Pool::builder()
    .build(manager)
    .expect("Failed to create pool.");

    HttpServer::new(move || {
        App::new()
            .data(pool.clone())
            .route("/", web::get().to(index))
            .route("/again", web::get().to(index2))
            .configure(routes::api::config)
    })
    .bind("127.0.0.1:8000")?
    .run()
    .await
}
