const firebase_admin = require('firebase-admin')

function getToken(req) {
    var token = '';

    if (req['headers']['x-access-token']) {
      token = req['headers']['x-access-token'];
    } else if (req.body.token) {
      token = req.body.token;
    } else if (req.query.token) {
      token = req.query.token;
    } else {
      token = false;
    }

    return {'token': token, 'isAPI': req.body.isAPI ? req.body.isAPI : false};
}

function verifyToken(data, callback) {

    var idToken = data['token']
    var isAPI = data['isAPI']

    console.log('Incoming token:', idToken, isAPI);

    if (isAPI) {
        return callback({'uid': idToken, 'isAPI': isAPI});
    }

    try {
        firebase_admin.auth().verifyIdToken(idToken)
            .then(function (decodedToken) {

                let uid = decodedToken.uid;
                console.log('Valid token', uid, decodedToken.email);

                return callback({'uid': uid, 'isAPI': isAPI, 'user': decodedToken}); // Legit token

            }).catch(function (error) {
            console.log('Invalid Token', error);

            return callback(false); // Invalid
        });
    } catch (e) {
        console.log(e);

        return callback(false); // Invalid
    }
}

function authenticate(req, res, next, permission) {
    verifyToken(getToken(req), function(authData) {
        if (authData) {

            var user = authData['user'];
            var uid = authData['uid'];
            var isAPI = authData['isAPI'];

            firebase_admin.firestore().collection('authentication').doc(isAPI ? 'externalKeys' : 'authorizedUsers').get()
                .then(doc => {
                    if (!doc.exists) {
                        console.log('No such document!');

                        return res.status(500).send({
                            error: 'DB Error'
                        });
                    } else {
                        console.log('Document data:', doc.data());

                        if (doc.data()[isAPI ? 'keys' : permission].includes(uid)) {

                            req.email = user ? user['email'] : 'API!';

                            return next();

                        } else {
                            return res.status(403).send({
                                error: 'Access Denied'
                            });
                        }

                    }
                })
                .catch(err => {
                    console.log('Error getting document', err);

                    return res.status(500).send({
                        error: 'DB Error'
                    });
                });

        } else {
            return res.status(401).send({
                error: 'Invalid Request'
            });
        }

    });
}

module.exports = {

    getToken: function (req) {
        return getToken(req);
    },

    verifyToken: function(token, callback) {
        return verifyToken(token, callback);
    },

    isViewer: function (req, res, next) {
        authenticate(req, res, next, 'viewer')
    },

    isAdmin: function (req, res, next) {
        authenticate(req, res, next, 'admin')
    },

    isDeveloper: function (req, res, next) {
        authenticate(req, res, next, 'developer')
    },
}