'''from flask import Flask, render_template, request
import subprocess
import sys
sys.path.insert(0, '/opt/dev-py/prTimeTracking/libs')


app = Flask(__name__)
def authenticate_user(username, password):
    try:
        result = subprocess.run(
            ['python3', './scripts/auth_checker.py', username, password],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception as e:
        print("Ошибка при вызове auth_checker.py:", e)
        return False

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success = authenticate_user(username, password)
        if success:
            return render_template('success.html', user=username)
        else:
            # Show the LDAP error on the page for debugging
            return f"Неверный логин или пароль<br>{username, password}<pre></pre>", 401
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

'''


from flask import Flask, render_template, request, flash, redirect, url_for
import subprocess
import os

app = Flask(__name__)
app.secret_key = os.urandom(240000)

def authenticate_user(username, password):
    try:
        result = subprocess.run(
            ['python3', './scripts/auth_checker.py', username, password],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception as e:
        print("Ошибка при вызове auth_checker.py:", e)
        return False

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            return render_template('success.html', user=username)
        else:
            flash("Something goes wrong, please check login or password.")
            return redirect(url_for('login'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)