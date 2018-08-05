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

async function accountFromToken(token){
    const text = "select * from token inner join userprofile on userprofile.id = token.user_id where token.key = $1"
    return pool.query(text, [token])
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

            user = await accountFromToken("155d65450328a7fbf4915bb0a829ee7cadf4a631")[0]
            const artifacts = { user: 'info' };

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

/*
accountFromToken("155d65450328a7fbf4915bb0a829ee7cadf4a631").then(res=>{
    console.log(res.rows)
})
*/

accountFromToken("155d65450328a7fbf4915bb0a829ee7cadf4a631").then(res=>{
    console.log(res.rows[0])
})
pool.end()