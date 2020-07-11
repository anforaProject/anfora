#[macro_use]
pub extern crate failure;
#[macro_use]
pub extern crate diesel;
pub extern crate actix;
pub extern crate actix_web;
pub extern crate chrono;
pub extern crate serde_json;
use diesel::prelude::*;
use diesel::r2d2::{self, ConnectionManager};

pub mod api;
pub mod routes;
pub mod db;
pub mod schema;

pub type DbPool = r2d2::Pool<ConnectionManager<PgConnection>>;
