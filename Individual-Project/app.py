from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
from collections import OrderedDict
import json
import datetime

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



def find_user_through_email(email):
    for user in db.child("Users").get().val():

            user_dict = json.loads(json.dumps(db.child("Users").child(user).get().val()))

            if user_dict["email"] == email:
                second_user_localId = user
                second_user_name = user_dict['name']
                final_second_user_dict = user_dict
    return [second_user_localId, second_user_name, final_second_user_dict]


@app.route('/we_do_not_care')
def we_do_not_care():
    return render_template("we_do_not_care.html")

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
        num_of_users = len(db.child("Users").get().val())
        total_amount_stored = 0

        for user in db.child("Users").get().val():

            user_dict = json.loads(json.dumps(db.child("Users").child(user).get().val()))
            total_amount_stored += user_dict['balance']
        
    except:
        num_of_users = 0
    return render_template("login.html", num_of_users=num_of_users, total_amount_stored=total_amount_stored)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        group = request.form.get('group')
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            user = {"name": name, "email":email, "password":password, "group":group, "balance":500, "history":{"Started account":"Creation"}}
            db.child("Users").child(login_session['user']['localId']).set(user)
            return redirect(url_for('home'))
        except:
            error = "Authentication failed."
    return render_template("signup.html", GROUPS=GROUPS)

@app.route('/home', methods=['GET', 'POST'])
def home():
    user = db.child("Users").child(login_session['user']['localId']).get().val()
    return render_template("home.html", user=user, action=list(user['history'].values())[0])



@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':

        other_email = request.form['other_email']
        amount = int(request.form['amount'])

        user_info = find_user_through_email(other_email)
        second_user_localId = user_info[0]
        second_user_name = user_info[1]
        final_second_user_dict = user_info[2]

        try:
            first_user_new_balance={'balance' : db.child("Users").child(login_session['user']['localId']).get().val()['balance'] - amount}
            db.child("Users").child(login_session['user']['localId']).update(first_user_new_balance)
            second_user_new_balance = {'balance':((final_second_user_dict['balance']) + amount)}
            db.child("Users").child(second_user_localId).update(second_user_new_balance)

            x = datetime.datetime.now()
            x = x.strftime("%A %d %H:%I")

            new_history_first_user = {f"Payed {amount} to {second_user_name} at {x}": "Payment"}
            user_name = db.child("Users").child(login_session['user']['localId']).child('name').get().val()
            new_history_second_user = {f"Received {amount} from {user_name} at {x}": "#baller"}
            db.child("Users").child(login_session['user']['localId']).child('history').update(new_history_first_user)
            db.child("Users").child(second_user_localId).child('history').update(new_history_second_user)

        except:

            error = "Error while transferring money"
        return redirect(url_for('home'))
    else:

        user = db.child("Users").child(login_session['user']['localId']).get().val()
        users = db.child("Users").get().val()

        return render_template("transfer.html", user=user, users=users)


@app.route('/history')
def history():
    return render_template("history.html", history_list = json.loads(json.dumps(db.child("Users").child(login_session['user']['localId']).get().val()))['history'])

# @app.route('/leaderboard')
# def leaderboard():
#     money_board = []
#     for user in db.child("Users").get().val():
#         user_dict = json.loads(json.dumps(db.child("Users").child(user).get().val()))
#         money_board.append(user_dict['balance'])
#         money_board = sorted(money_board)
    
#     user_order = []
#     for i in range(len(money_board)-1,0,-1):
#         print(money_board[i])
#         for user in db.child("Users").get().val():
#             user_dict = json.loads(json.dumps(db.child("Users").child(user).get().val()))
#             if (user_dict['balance']) == money_board[i]:
#                 user_info = find_user_through_email(user_dict['email'])
#                 user_order.append(user_info[0])
#                 print(user_dict)

   
#     return render_template("leaderboard.html", user_order=user_order, users=db.child("Users"))

@app.route('/user_hall')
def user_hall():
    return render_template("user_hall.html", users=json.loads(json.dumps(db.child("Users").get().val())))


@app.route('/logout')
def logout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)






#add dialog box to confirm money transfer