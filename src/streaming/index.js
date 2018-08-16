var express = require('express');
var app = express();
var expressWs = require('express-ws')(app);
var cors = require('cors')
let sseExpress = require('sse-express');
var passport = require('passport')
var BearerStrategy = require('passport-http-bearer').Strategy;


//DB
const { Pool, Client } = require('pg')

const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'anforadb',
    password: '',
    port: 5432,
  })

accountFromToken = (token) => {
    const text = "select * from token inner join userprofile on userprofile.id = token.user_id where token.key = $1"
    return pool.query(text, [token])
}

passport.use(new BearerStrategy(
    function(token, done) {
        return accountFromToken(token)
        .then(res => {
            if (res.rows.length === 0){ 
                return done(null, false); 
            }

            return done(null, res.rows[0], { scope: 'all' });
        })
    }
));

app.use(cors())
 
app.get('/',
    passport.authenticate('bearer', { session: false }),
    function(req, res, next){
        console.log(req.user.username, req.testing);
        res.end();
    }
);

app.get('/updates',passport.authenticate('bearer', { session: false }), sseExpress(),  function(req, res) {
    res.sse({
        event: 'connected',
        data: {
          welcomeMsg: 'Hello world!'
        }
    });
    setInterval(function(){
        let i = 0;
        res.sse({
            event: 'update',
            data:{
                int: i,
                user: req.user.username
            }
        })  
        i += 1;
        console.log("pulse")
    }, 3000)
    
});

 
app.listen(4000);


