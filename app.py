import os
import sys
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')

from flask import Flask, render_template, flash, redirect, url_for, session
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

from scripts.auth_checker import authenticate as ldap_authenticate
from scripts.current_month_year import get_current_month_year
from scripts.uid_openldap_getting import authenticate_and_get_info as ldap_uid



from scripts.forms import LoginForm, WorkHoursForm
from scripts.forms import WorkHoursForm



app = Flask(__name__)
app.secret_key = os.urandom(32)  # Keep your secret key here

csrf = CSRFProtect(app)  # Initialize CSRF after app creation


def authenticate_user(username, password):
    try:
        return ldap_authenticate(username, password)
    except Exception as e:
        print("LDAP auth error:", e)
        return False


def getting_unig_id(username, password):
    try:
        return ldap_uid(username, password).get("entryUUID")
    except Exception as e:
        print("LDAP auth error:", e)
        return False


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if authenticate_user(username, password):
            uid = getting_unig_id(username, password)
            if uid:
                session['username'] = username
                session['uid'] = uid

                month_name, year, calendar_weeks, month_num = get_current_month_year()

                return render_template(
                    'success.html',
                    user=username,
                    month=month_name,
                    month_num=month_num,
                    year=year,
                    calendar_weeks=calendar_weeks,
                    uid=uid
                )

        flash("Something went wrong, please check login or password.")
        return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/work_hours/<int:year>/<int:month>/<int:day>', methods=['GET', 'POST'])
def work_hours(year, month, day):
    if 'uid' not in session:
        flash("Please log in.")
        return redirect(url_for('login'))

    try:
        date_obj = datetime(year, month, day)
    except ValueError:
        flash("Invalid date.")
        return redirect(url_for('login'))

    form = WorkHoursForm()

    if form.validate_on_submit():
        # here can doing anythong to insert some data into db 
        # example:
        # save_task(session['uid'], date_obj, form.task_name.data, form.start_time.data, form.end_time.data, form.extra_info.data)

        flash("Task successfully added!")
        return redirect(url_for('work_hours', year=year, month=month, day=day))

    return render_template('work_hours.html', date=date_obj, uid=session['uid'], form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
