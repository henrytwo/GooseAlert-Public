import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import Button from "react-bootstrap/Button";
import ApiService from "../services/ApiService";
import React from "react";
import '../stylesheet/App.css';
import Navbar from "./Navbar";
import * as firebase from "firebase";
import ReactDOM from "react-dom";

function filterName(name) {
    var email = name.split('@')

    email[0] = email[0].substring(0, 3) + '****'

    return email.join('@')
}

function ViewerObject(data) {

    var sessionsOpen = data['sessionsOpen'];
    var name = data['name'];

    return <>
        <div className="sensor-object">

            <h6>
                User: {filterName(name)}

                <br/>

                Active sessions: {sessionsOpen}
            </h6>



        </div>
    </>
}

function CameraViewers(data) {

    var viewers = data['viewers'];
    var totalViewers = 0;

    for (var i in viewers) {
        totalViewers += viewers[i];

    }

    var viewerItems = Object.keys(viewers).map((id) => {

        return <ViewerObject key={id} sessionsOpen={viewers[id]} name={id}/>

    });

    return <>
         <div id="camera-viewers-panel" className="dashboard-panel">
             Camera Viewers<br/>

            <h4>Total: {totalViewers}</h4>
            <br/>
            <h6>
                {viewerItems}
            </h6>
        </div>
    </>
}

function SensorObject(data) {
    var sensorData = data['sensorData'];

    return <>
        <div className={"sensor-object " + (sensorData['open'] ? 'sensor-open' : '')}>

            <h4>
               {sensorData['name']}
            </h4>

            <h6>
                Status: {sensorData['open'] ? 'OPEN' : 'CLOSED'}
            </h6>

            <h6>
                Last Opened: {sensorData['time_opened'] == -1 ? 'N/A (Not on file)' : new Date(sensorData['time_opened'] * 1000).toString()}
            </h6>

        </div>
    </>
}

function Sensors(data) {

    var sensors = data['sensors'];

    var sensorItems = Object.keys(sensors).map((id) => {

        return <SensorObject key={id} sensorData={sensors[id]}/>

    });

    return <>
         <div id="sensors-panel" className="dashboard-panel">
             Sensors<br/>

            <h6>
                {sensorItems}
            </h6>
        </div>
    </>
}

class Dashboard extends React.Component {



    render() {

        var permissions = JSON.parse(sessionStorage.permissions);

        let admin, viewer;

        if (permissions['admin']) {
            admin = <>

                <div className="col-md">
                    <button className="control-button" variant="danger" onClick={ApiService.arm}>Arm</button>
                    <button className="control-button" variant="success" onClick={ApiService.disarm}>Disarm</button>
                </div>

                <div className="col-md">
                    <button className="control-button" variant="danger" onClick={ApiService.silent}>Silent</button>
                    <button className="control-button" variant="success" onClick={ApiService.unsilent}>UnSilent</button>
                </div>

                <div className="col-md">
                    <button className="control-button" variant="info" onClick={ApiService.switchON}>Switch On</button>
                    <button className="control-button" variant="info" onClick={ApiService.switchOFF}>Switch Off</button>
                </div>

                <div className="col-md">
                    <button className="control-button" variant="info" onClick={ApiService.deskON}>Desk On</button>
                    <button className="control-button" variant="info" onClick={ApiService.deskOFF}>Desk Off</button>
                </div>


                <div className="col-md">
                    <button className="control-button" variant="info" onClick={ApiService.lightON}>Light On</button>
                    <button className="control-button" variant="info" onClick={ApiService.lightOFF}>Light Off</button>
                </div>

                <div className="col-md">
                    <button className="control-button" variant="info" onClick={ApiService.privacyON}>Privacy On</button>
                    <button className="control-button" variant="info" onClick={ApiService.privacyOFF}>Privacy Off</button>
                </div>

                <div className="col-md">
                    <button className="control-button" variant="info" onClick={ApiService.reboot}>Reboot</button>
                </div>
            </>
        } else {
            admin = <></>
        }

        if (permissions['viewer']) {
            viewer = <>

            </>
        }


        const db = firebase.firestore();

        db.collection("settings").doc("watching")
            .onSnapshot(function(doc) {
                console.log("Watching: ", doc.data());

                ReactDOM.render(
                        <CameraViewers viewers={doc.data()}/>,
                        document.getElementById('viewers')
                );

        });

        db.collection("settings").doc("sensorData")
            .onSnapshot(function(doc) {
                console.log("Sensors: ", doc.data());

                ReactDOM.render(
                        <Sensors sensors={doc.data()}/>,
                        document.getElementById('sensors')
                );

        });


        return <>

            <div id="camera-holder" className="row">
                <div className="col-xl-9">

                    <div id="camera-box">
                        <img id="camera-feed" alt="Loading..." src={ window.location.origin + '/api/camera?token='+ sessionStorage.token } sizes="width: 100%"></img>
                    </div>
                </div>
                <div className="col-xl-2">
                    <span id="viewers"></span>
                    <span id="sensors"></span>
                </div>


            </div>

            <div class="btn-group">
                <div class="row">
                {admin}

                {viewer}
                </div>
            </div>

        </>
    }
}

export default Dashboard;