require('dotenv').config();
const express         = require('express');
const cors            = require('cors');
const fs              = require('fs');

const bodyParser      = require('body-parser');
const methodOverride  = require('method-override');
const morgan          = require('morgan');
const cookieParser    = require('cookie-parser');
const RateLimit       = require('express-rate-limit');

const port            = process.env.PORT || 3005;

// Start services
const Raven           = require('raven');

const firebase_admin = require('firebase-admin')


var serviceAccount = require("./firebase_key.json");

firebase_admin.initializeApp({
  credential: firebase_admin.credential.cert(serviceAccount),
  databaseURL: "<REDACTED>"
});

Raven.config(process.env.SERVER_RAVEN_KEY).install();
Raven.context(function() {
    var app = express();

    app.enable('trust proxy'); // For reverse proxy

    // Start routers
    app.use(express.static('../client/build/'));

    var apiRouter = express.Router();
    require('./routes/api')(apiRouter);
    app.use('/api', apiRouter);

    require('./routes/routes')(app);

    app.listen(port, function () {
        console.log('listening on *:' + port);
    });



});
