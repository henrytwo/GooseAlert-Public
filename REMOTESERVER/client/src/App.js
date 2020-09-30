import React from 'react';
import ReactDOM from 'react-dom';
import Button from 'react-bootstrap/Button';
import ButtonToolbar from 'react-bootstrap/ButtonToolbar';
import * as $ from 'jquery';
import logo from './logo.svg';
import * as FirebaseInstance from 'firebase'
import './stylesheet/App.css';
import * as firebase from 'firebase';
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import RouterPage from './components/RouterPage'
import Navbar from './components/Navbar'
import ApiService from './services/ApiService'
import FirebaseService from "./services/FirebaseService";
import * as swal from 'sweetalert2'

const firebaseConfig = {
  apiKey: "AIzaSyBewkXfocFJmdisRpSX0RT52Q7NMIiFixk",
  authDomain: "goosealert-6fd53.firebaseapp.com",
  databaseURL: "https://goosealert-6fd53.firebaseio.com",
  projectId: "goosealert-6fd53",
  storageBucket: "goosealert-6fd53.appspot.com",
  messagingSenderId: "996918742506",
  appId: "1:996918742506:web:d09a508b9cdd8aad"
};

firebase.initializeApp(firebaseConfig);

const db = firebase.firestore();

firebase.auth().onAuthStateChanged(function(user) {

    if (user) {
        sessionStorage.token = user.ra;

        ApiService.permissions(function (data) {


            console.log('User Permissions: ', data)

            if (data) {

                sessionStorage.permissions = JSON.stringify(data);

                if (!data['viewer']) {
                    console.log('No permission')

                    FirebaseService.logoutImmediately(function() {
                        swal.fire('Error', 'You don\'t have permission to access this page.', 'error');
                    });


                }

            } else {
                sessionStorage.permissions = '{"admin":true,"viewer":true,"developer":true}'
            }

            ReactDOM.render(
                    <StateManager/>,
                    document.getElementById('content')
            );


        });
    } else {
          sessionStorage.token = '';

          ReactDOM.render(
            <StateManager />,
            document.getElementById('content')
          );
    }


});

class StateManager extends React.Component {
    render() {
        if (sessionStorage.token) {
            return <RouterPage/>
        } else {
            return <Login/>
        }
    }
}

function App() {
  return (
    <div className="App">
      <header className="App-header">


          <span id="content"></span>

      </header>
    </div>
  );
}

export default App;
