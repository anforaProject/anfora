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

const server = new Hapi.server({port: 4000})

accountFromToken = (token) => {
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
            return accountFromToken(token).then(
                res=>{
                    const isValid = res.rows.length !== 0;
                    const credentials = { token };
                    const artifacts = { user: res.rows[0] };
                    return { isValid, credentials, artifacts };
                }
            )  
        }
    });

    server.route({
        method: 'GET',
        path: '/api/v1/streaming/user',
        config: {
            auth: 'simple',
            id: 'homeTimeline'
        },
        handler: async function (request, h) {
            return {info: 'success!'}
        }
    })

    await server.start();

    return server;
}

/*
accountFromToken("155d65450328a7fbf4915bb0a829ee7cadf4a631").then(res=>{
    console.log(res.rows)
})
*/

accountFromToken("155d65450328a7fbf4915bb0a829ee7cadf4a631").then(res=>{
    console.log(res.rows[0])
})

start()
.then((server) => console.log(`Server listening on ${server.info.uri}`))
.catch(err => {

    console.error(err);
    process.exit(1);
})

