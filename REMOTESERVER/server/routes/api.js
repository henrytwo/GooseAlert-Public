const jwt                = require('jsonwebtoken');
const validator          = require('validator');
const express            = require('express');
const request            = require('request');
const MjpegProxy         = require('mjpeg-proxy').MjpegProxy;
const firebase_admin     = require('firebase-admin')

const permissions        = require('../services/permissions');

//const permissions        = require('../services/permissions');
//const logger             = require('../services/logger');
require('dotenv').config();

JWT_SECRET             = process.env.JWT_SECRET;

function forwardResponse(response, res) {
    if (response) {
        console.log('Command forwarded', response.body, response.statusCode)

        return res.status(response.statusCode).send(JSON.parse(response.body))
    } else {
        return res.status(500).send({
            error: 'Something went wrong'
        });
    }
}

module.exports = function(router) {
    router.use(express.json());

    router.post('/lightON', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/lightON', {

            'executor': req.email
        }, function(error, response, body) {
     
            forwardResponse(response, res);
        })

    });

    router.post('/lightOFF', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/lightOFF', {

            'executor': req.email
        }, function(error, response, body) {
      
            forwardResponse(response, res);
        })

    });

    router.post('/privacyON', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/privacyON', {

            'executor': req.email
        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/privacyOFF', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/privacyOFF', {

            'executor': req.email
        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/arm', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/arm', {

            'executor': req.email
        }, function(error, response, body) {
            forwardResponse(response, res);
        })

    });

    router.post('/disarm', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/disarm', {

            'executor': req.email
        }, function(error, response, body) {
   
            forwardResponse(response, res);
        })

    });

    router.post('/switchON', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/switchON', {

            'executor': req.email
        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/switchOFF', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/switchOFF', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/deskON', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/deskON', {

            'executor': req.email
        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/deskOFF', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/deskOFF', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/home', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/home', {

            'executor': req.email
        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/leaving', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/leaving', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/goodnight', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/goodnight', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/reboot', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/reboot', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/SILENT', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/SILENT', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/UNSILENT', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/UNSILENT', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });


    router.post('/pcsuspend', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/pcsuspend', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/pclock', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/pclock', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/popomode', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/popomode', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });

    router.post('/discomode', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/discomode', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });


    router.post('/nodiscomode', permissions.isAdmin, function (req, res) {

        request.post(process.env.REMOTE_SERVER_ADDRESS + '/nodiscomode', {

            'executor': req.email

        }, function(error, response, body) {

            forwardResponse(response, res);
        })

    });


    router.get('/camera', permissions.isViewer, function (req, res) {

        console.log(process.env.REMOTE_SERVER_ADDRESS + '/0?' + req.email)

        new MjpegProxy(process.env.REMOTE_SERVER_ADDRESS + '/0?' + req.email).proxyRequest(req, res)

    });


    router.get('/doorcamera', permissions.isAdmin, function (req, res) {


        new MjpegProxy(process.env.DOOR_CAMERA_ADDRESS).proxyRequest(req, res)

    });

    router.get('/permissions', function (req, res) {

        var token = req.query.token;

        if (token) {

            permissions.verifyToken({'token' : token}, function (authData) {
               if (authData) {

                    var user = authData['user'];
                    var uid = authData['uid'];

                    firebase_admin.firestore().collection('authentication').doc('authorizedUsers').get()
                        .then(doc => {
                            if (!doc.exists) {
                                console.log('No such document!');

                                return res.status(500).send({
                                    error: 'DB Error'
                                });
                            } else {
                                console.log('Document data:', doc.data());

                                var permissions = {};

                                for (var permission in doc.data()) {

                                    permissions[permission] = doc.data()[permission].includes(uid);

                                }

                                return res.json(permissions);

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
                        error: 'Invalid Token'
                    });
                }

            });

        } else {
                return res.status(401).send({
                    error: 'Invalid Request'
                });
        }
    });



}