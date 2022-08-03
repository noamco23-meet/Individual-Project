from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

config = {
  "apiKey": "AIzaSyBwW3x-5gkCMy3bhaeOFXkcgaUGJmpGjyw",
  "authDomain": "personal-project-51039.firebaseapp.com",
  "projectId": "personal-project-51039",
  "storageBucket": "personal-project-51039.appspot.com",
  "messagingSenderId": "573878428747",
  "appId": "1:573878428747:web:2aebcb6dd0a166882759ce",
  "measurementId": "G-X2BSVG1JHX",
  "databaseURL":""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'

GROUPS = ["Group A", "Group B", "Group C", "Group D", "Group E", "Group F"]

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for('home'))
        except:
            error = "Authentication failed."
    return render_template("login.html")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        group = request.form.get('group')
        print(group)
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            return redirect(url_for('home'))
        except:
            error = "Authentication failed."
    return render_template("signup.html", GROUPS=GROUPS)

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True)