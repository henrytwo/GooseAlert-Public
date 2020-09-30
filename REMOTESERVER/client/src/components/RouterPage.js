import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import Button from "react-bootstrap/Button";
import ApiService from "../services/ApiService";
import React from "react";
import '../stylesheet/App.css';
import Navbar from "./Navbar";
import Dashboard from "./Dashboard";
import Logs from "./Logs";
import { BrowserRouter as Router, Route } from "react-router-dom";

class RouterPage extends React.Component {
    render() {
        return <>


          <Router>

              <Navbar />


              <div>

                <Route exact path="/" component={Dashboard} />
                <Route exact path="/logs" component={Logs} />
              </div>
            </Router>
        </>
    }
}

export default RouterPage;