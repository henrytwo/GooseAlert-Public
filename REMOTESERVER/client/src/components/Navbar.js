import React from "react";
import '../stylesheet/Navbar.css'
import FirebaseService from '../services/FirebaseService'
import { Link, BrowserRouter } from "react-router-dom";
import * as firebase from "firebase";
import ReactDOM from "react-dom";
import ApiService from "../services/ApiService";

function StatusIndicator(status) {
    // Ready
    // Armed
    // Not Ready
    // Alarm

    status = status['status']

    switch (status) {
        case "ALARM":
            return <>

                      <div id="navstatus-alarm" className="mainnav-status">
                          <div className="spacer"></div>
                          <div className="spacer-compensation">ALARM!</div>
                      </div>
            </>

            break

        case "ARMED":
            return <>

                      <div id="navstatus-armed" className="mainnav-status">
                          <div className="spacer"></div>
                          <div className="spacer-compensation">ARMED</div>
                      </div>
            </>

            break

        case "READY":
            return <>

                      <div id="navstatus-ready" className="mainnav-status">
                          <div className="spacer"></div>
                          <div className="spacer-compensation">READY</div>
                      </div>
            </>

            break

        case "NOTREADY":
            return <>

                      <div id="navstatus-notready" className="mainnav-status">
                          <div className="spacer"></div>
                          <div className="spacer-compensation">NOT READY</div>
                      </div>
            </>

            break

    }
}

function Overlay(data) {
    var show = data['show']

    // Okay, I know this is janky af but I couldn't figure out an easy way to ge the router to response to these things

    if(show) {
        return <>
          <div className="overlay">
                <ul className="overlay-list">
                  <li>
                     <a href="javascript: window.location.href='/'" className="js-navbar-link scrollLink overlayLink">Dashboard</a>
                  </li>
                  <li>
                      <a href="javascript: window.location.href='/logs'" className="js-navbar-link scrollLink overlayLink">Logs</a>
                  </li>

                  {/*
                  <li>
                      <Link to="/configuration" className="js-navbar-link scrollLink overlayLink">Configuration</Link>
                  </li>
                  <li>
                      <Link to="/developer" className="js-navbar-link scrollLink overlayLink">Developer</Link>
                  </li>*/}

                  <li>
                      <a className="js-navbar-link scrollLink overlayLink" onClick={FirebaseService.logout}>Logout</a>
                  </li>

              </ul>
          </div>
      </>
    } else {
        return <></>
    }


}


class Navbar extends React.Component {



  render() {
       var showOverlay = false

     function toggleBurger() {
          console.log('Toggleing')
          showOverlay = !showOverlay;


            ReactDOM.render(

                <Overlay show={showOverlay}/>,
                    document.getElementById('overlayPlaceholder')
            );

      }


    const db = firebase.firestore();

    db.collection("settings").doc("systemState")
        .onSnapshot(function(doc) {
            console.log("System State: ", doc.data());

            if (doc.data()['alarm']) {
                var status = 'ALARM';
            } else if (doc.data()['armed']) {
                var status = 'ARMED';
            } else if (doc.data()['ready']) {
                var status = 'READY';
            } else {
                var status = 'NOTREADY';
            }

            ReactDOM.render(
                    <StatusIndicator status={status}/>,
                    document.getElementById('status')
            );

    });

    return <>

      <div id="mainnav" className="navbar navbar-expand-md nav-active">


          <div id="navham" className="hamburger hamburger--slider pull-right show-smol-ui">
              <div className="hamburger-box" onClick={toggleBurger}>
                  <div className="hamburger-inner" id="hamburger"></div>
              </div>
          </div>


          <div id="mainnav-table">

              <div id="mainnav-logo" class="hide-widescreen-ui">
                  <div className="spacer"></div>
                  <div className="spacer-compensation">
                      <img src="goosealert-wide-white.png" style={{"height": "60px"}}></img>
                  </div>
              </div>

              <div id="mainnav-inner" class="hide-widescreen-ui">
                  <div className="spacer"></div>
                  <div className="spacer-compensation">
                      <ul id="navbutton-list">
                          <li className="nav-item">
                              <Link to="/" className="js-navbar-link scrollLink navobject">Dashboard</Link>
                          </li>
                          <li className="nav-item">
                              <Link to="/logs" className="js-navbar-link scrollLink navobject">Logs</Link>
                          </li>

                          {/*
                          <li className="nav-item">
                              <Link to="/configuration" className="js-navbar-link scrollLink navobject">Configuration</Link>
                          </li>
                          <li className="nav-item">
                              <Link to="/developer" className="js-navbar-link scrollLink navobject">Developer</Link>
                          </li>*/}

                          <li className="nav-item">
                              <a className="js-navbar-link scrollLink navobject" onClick={FirebaseService.logout}>Logout</a>
                          </li>
                      </ul>
                  </div>
              </div>


              <span id="status"></span>
          </div>
      </div>

      <span id="overlayPlaceholder"></span>


    </>
  }
}

export default Navbar;