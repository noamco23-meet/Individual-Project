from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
from collections import OrderedDict
import json
config = {
  "apiKey": "AIzaSyBwW3x-5gkCMy3bhaeOFXkcgaUGJmpGjyw",
  "authDomain": "personal-project-51039.firebaseapp.com",
  "projectId": "personal-project-51039",
  "storageBucket": "personal-project-51039.appspot.com",
  "messagingSenderId": "573878428747",
  "appId": "1:573878428747:web:2aebcb6dd0a166882759ce",
  "measurementId": "G-X2BSVG1JHX",
  "databaseURL":"https://personal-project-51039-default-rtdb.europe-west1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

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
    try:
        numOfUsers = len(db.child("Users").get().val())
    except:
        numOfUsers = 0
    return render_template("login.html", numOfUsers=numOfUsers)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        group = request.form.get('group')
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            user = {"name": name, "email":email, "password":password, "group":group, "balance":500, "history":[]}
            db.child("Users").child(login_session['user']['localId']).set(user)
            return redirect(url_for('home'))
        except:
            error = "Authentication failed."
    return render_template("signup.html", GROUPS=GROUPS)

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=db.child("Users").child(login_session['user']['localId']).get().val())



@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':

        other_email = request.form['other_email']
        amount = int(request.form['amount'])

        for user in db.child("Users").get().val():

            user_dict = json.loads(json.dumps(db.child("Users").child(user).get().val()))

            if user_dict["email"] == other_email:
                second_user_localId = user
                second_user_name = user_dict['name']
                final_second_user_dict = user_dict
        try:
            first_user_new_balance={'balance':db.child("Users").child(login_session['user']['localId']).get().val()['balance'] - amount}
            print(first_user_new_balance)
            db.child("Users").child(login_session['user']['localId']).update(first_user_new_balance)
            second_user_new_balance = {'balance':((final_second_user_dict['balance']) + amount)}
            print(second_user_new_balance)
            db.child("Users").child(second_user_localId).update(second_user_new_balance)

            
            db.child("Users").child(login_session['user']['localId']).update(db.child("Users").child(login_session['user']['localId'])['history'].append[f"Sent {amount} to {second_user_name}"])

        except:

            error = "Error while transferring money"
        return redirect(url_for('home'))
    else:

        user = db.child("Users").child(login_session['user']['localId']).get().val()
        users = db.child("Users").get().val()

        return render_template("transfer.html", user=user, users=users)


if __name__ == '__main__':
    app.run(debug=True)


#add dialog box to confirm money transfer