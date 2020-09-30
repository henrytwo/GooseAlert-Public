import Button from "react-bootstrap/Button";
import React from "react";
import FirebaseService from "../services/FirebaseService"

class Login extends React.Component {
    render() {
        return <>

            <div id="login-background" style={{"background": "url('goose.jpg')"}}>
                <div id="login-tint">

                    <div class="login-spacer"></div>
                    <div id="login-box">
                        <img id="login-logo" src="goosealert-wide.png"></img>

                        <button class="control-button login-button" onClick={FirebaseService.login}><i className="fab fa-google"></i> Login with Google</button>
                    </div>

                </div>
            </div>
        </>
    }
}

export default Login;