import * as firebase from "firebase";
import * as swal from 'sweetalert2'

function logoutImmediately(callback) {
    firebase.auth().signOut().then(function() {
              // Sign-out successful.

                console.log('Logged out!')

                if (callback) {
                    callback()
                }

            }, function(error) {
              // An error happened.
                console.log('Could\'t logout')

                swal.fire('Error', 'For some reason, we couldn\'t log you out', 'error');
            });
}

const FirebaseService = {
    updateToken: function(callback) {
        console.log('Updated token')

        firebase.auth().currentUser.getIdToken(true).then(function (idToken) {

            sessionStorage.token = idToken;

            if (callback) {
                callback();
            }

        }).catch(function (error) {
            // Handle error

            console.log('Couldn\'t update token')


            swal.fire('Error', 'Unable to update token', 'error');
        });
    },

    logoutImmediately: function(callback) {
       logoutImmediately(callback)
    },

    logout: function() {

        swal.fire({
          title: 'Logout',
          text: "Are you sure you want to logout?",
          type: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Logout'
        }).then((result) => {
          if (result.value) {
                logoutImmediately(function() {
                    swal.fire('Success', 'You have logged out successfully', 'success');
                });
          }
        })


    },

    login: function() {
        var provider = new firebase.auth.GoogleAuthProvider();
        firebase.auth().useDeviceLanguage();
        provider.setCustomParameters({
            'login_hint': 'user@example.com'
        });
        firebase.auth().signInWithPopup(provider).then(function(result) {
          // This gives you a Google Access Token. You can use it to access the Google API.
          var token = result.credential.accessToken;
          // The signed-in user info.
          var user = result.user;
          // ...
            console.log(token, user)
        }).catch(function(error) {
          // Handle Errors here.
          var errorCode = error.code;
          var errorMessage = error.message;
          // The email of the user's account used.
          var email = error.email;
          // The firebase.auth.AuthCredential type that was used.
          var credential = error.credential;
          // ...


                swal.fire('Error', 'Unable to login', 'error');
        });
    }

}

export default FirebaseService;