var express = require('express');
var app = express();
var cors = require('cors')
let sseExpress = require('sse-express');
var passport = require('passport')
var BearerStrategy = require('passport-http-bearer').Strategy;
var redis = require('redis');


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
 
app.get('/',sseExpress(),
    function(req, res, next){
        res.sse({
            event: "Connected",
            data: {
                welcomeMsg: "hi"
            }
        });
    }
);


app.get('/api/v1/streaming/user',sseExpress(), passport.authenticate('bearer', { session: false }),  function(req, res) {
    
    var prefix = "timeline";
    var id = req.user.id;

    var channel = `${prefix}:${id}`;
    
    

    //Create connection to redis
    var sub = redis.createClient();

    sub.subscribe(channel);
    console.log("Connected to " + channel)
    sub.on("message", function(resource, message) {
        res.sse({
            event: message.substr(0,message.indexOf(' ')),
            data: message.substr(message.indexOf(' ')+1)
        });
    });


    req.on("close", function() {
        sub.unsubscribe();
    });
    
});

 
app.listen(4000);


