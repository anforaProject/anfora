//Hapi stuff
const Hapi = require('hapi')
const Nes = require('nes')
const AuthBearer = require('hapi-auth-bearer-token')
//DB
const { Pool, Client } = require('pg')

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'anforadb',
    password: '',
    port: 5432,
  })

const server = new Hapi.server()

const accountFromToken = (token, req, next) =>{
    
}

const start = async () => {
    
    await server.register([Nes, AuthBearer])


    server.auth.strategy('simple', 'bearer-access-token', {
        allowQueryToken: true,              // optional, false by default
        validate: async (request, token, h) => {

            // here is where you validate your token
            // comparing with token from your database for example
            const isValid = true

            const credentials = { token };
            const artifacts = { test: 'info' };

            return { isValid, credentials, artifacts };
        }
    });

    server.route({
        method: 'GET',
        path: '/api/v1/timelines/home',
        config: {
            id: 'homeTimeline'
        }
    })
}