import os
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime

from scripts.auth_checker import authenticate as ldap_authenticate
from scripts.current_month_year import get_current_month_year


app = Flask(__name__)
app.secret_key = os.urandom(32)

''' seems this function not needed at all, just check it later again !
def authenticate_user(username, password):
    try:
        return ldap_authenticate(username, password)
    except Exception as e:
        print("LDAP auth error:", e)
        return False
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            # ✅ Get full calendar info including month number
            month_name, year, calendar_weeks, month_num = get_current_month_year()

            return render_template(
                'success.html',
                user=username,
                month=month_name,
                month_num=month_num,
                year=year,
                calendar_weeks=calendar_weeks
            )
        else:
            flash("Something goes wrong, please check login or password.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/work_hours/<int:year>/<int:month>/<int:day>')
def work_hours(year, month, day):
    try:
        date_obj = datetime(year, month, day)
    except ValueError:
        flash("Invalid date.")
        return redirect(url_for('login'))

    return render_template('work_hours.html', date=date_obj)

if __name__ == '__main__':
    app.run(debug=True)
