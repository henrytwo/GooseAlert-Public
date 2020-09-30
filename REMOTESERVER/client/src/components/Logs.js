import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import Button from "react-bootstrap/Button";
import ApiService from "../services/ApiService";
import React from "react";
import '../stylesheet/App.css';
import Navbar from "./Navbar";
import * as firebase from "firebase";
import ReactDOM from "react-dom";

function LogObject(data) {
    var message = data['message'];
    var timestamp = data['timestamp'];
    var type = data['type'];

    return <>
        <div className="log-object">
            {message}<br/>
            {timestamp}<br/>
            {type}
        </div>

    </>
}

function LogsPanel(data) {
    var logEvents = data['logEvents'];

     var logItems = Object.keys(logEvents).map((id) => {

        return <LogObject key={id} message={logEvents[id]['message']} timestamp={logEvents[id]['timestamp']} type={logEvents[id]['type']}/>

    });


    return <>
        <p style={{"color": "black"}}>
            {logItems}
        </p>
    </>
}

class Logs extends React.Component {


    render() {

        var logEvents = []

        const db = firebase.firestore();

        db.collection("logs").orderBy('unixtime', 'desc').limit(100).onSnapshot(function(querySnapshot) {
                var events = [];
                querySnapshot.docChanges().forEach(function(change) {
                   if (change.type === "added") {
                       events.push(change.doc.data());
                   }
                });

                if (!sessionStorage.logEvents) {
                    sessionStorage.logEvents = '[]'
                }

                logEvents = events.concat(logEvents);

                ReactDOM.render(
                     <LogsPanel logEvents={logEvents}/>,
                    document.getElementById('logs-placeholder')
                );
        });

        return <>

            <span id="logs-placeholder"></span>


        </>
    }
}

export default Logs;