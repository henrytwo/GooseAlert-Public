import * as $ from "jquery";
import FirebaseService from "./FirebaseService";
import * as swal from 'sweetalert2'

function sendRequest(type, url, data, callback, ui) {

    if (ui) {
        swal.fire('Processing request...')
        swal.showLoading()
    }


    FirebaseService.updateToken(function () {


    })

    var request = {
            type: type,
            url: url,
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: data => {
                if (callback) callback(null, data)
            },
            error: data => {
                /*if (data && (data.status == 401 || data.status == 403) && Session.loggedIn() && !url.includes('changePassword')) {
                    this.logout(null, 'Permission error occurred. Please login again.')
                }*/

                if (!'error' in data) {
                    data['error'] = 'Something went wrong'
                }

                if (callback) callback(data)
            }
        };

        if (data) {
            request['data'] = type == 'POST' ? JSON.stringify(data) : data
        }

        if (sessionStorage.token) {
            request['beforeSend'] = xhr => {
                xhr.setRequestHeader('x-access-token', sessionStorage.token)
            }
        }

        $.ajax(request)

}

function handleResponse(err, data) {

    console.log(err, data);

    if (err) {
        swal.fire('Error', err.responseJSON['status'], 'error');
    } else {
        swal.fire('Success', data['status'], 'success')
    }

}

const ApiService = {

    sendRequest: function(type, url, data, callback, ui) {
        sendRequest(type, url, data, callback, ui)
    },

    arm: function() {
        sendRequest('POST', window.location.origin + '/api/arm', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    reboot: function() {
        sendRequest('POST', window.location.origin + '/api/reboot', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    silent: function() {
        sendRequest('POST', window.location.origin + '/api/SILENT', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    unsilent: function() {
        sendRequest('POST', window.location.origin + '/api/UNSILENT', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    disarm: function() {
        sendRequest('POST', window.location.origin + '/api/disarm', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    lightON: function() {
        sendRequest('POST', window.location.origin + '/api/lightON', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    lightOFF: function() {
        sendRequest('POST', window.location.origin + '/api/lightOFF', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    privacyON: function() {
        sendRequest('POST', window.location.origin + '/api/privacyON', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    privacyOFF: function() {
        sendRequest('POST', window.location.origin + '/api/privacyOFF', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    switchON: function() {
        sendRequest('POST', window.location.origin + '/api/switchON', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    switchOFF: function() {
        sendRequest('POST', window.location.origin + '/api/switchOFF', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    deskON: function() {
        sendRequest('POST', window.location.origin + '/api/deskON', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    deskOFF: function() {
        sendRequest('POST', window.location.origin + '/api/deskOFF', {}, function (err, data) {
            //alert('ok')

            handleResponse(err, data);
        }, true);
    },

    permissions: function(callback) {
        sendRequest('GET', window.location.origin + '/api/permissions?token=' + sessionStorage.token, {}, function (err, data) {
            //alert('ok')
            return callback(data)
        })
    }

}



export default ApiService;