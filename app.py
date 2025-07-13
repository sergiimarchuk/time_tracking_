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
        # here can doing Something to insert some data into db 
        # example:
        # save_task(session['uid'], date_obj, form.task_name.data, form.start_time.data, form.end_time.data, form.extra_info.data)

        flash("Task successfully added!")
        return redirect(url_for('work_hours', year=year, month=month, day=day))

    return render_template('work_hours.html', date=date_obj, uid=session['uid'], form=form)

@app.route('/calendar')
def calendar():
    if 'uid' not in session:
        flash("Please log in.")
        return redirect(url_for('login'))

    username = session.get('username')
    uid = session.get('uid')

    month_name, year, calendar_weeks, month_num = get_current_month_year()
    today = datetime.today()

    return render_template(
        'success.html',
        user=username,
        uid=uid,
        month=month_name,
        year=year,
        month_num=month_num,
        calendar_weeks=calendar_weeks,
        today_year=today.year,
        today_month=today.month,
        today_day=today.day
    )




####
from flask import request
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/opt/dev-py/TimeTracking-dev/uploads'  # Make sure this directory exists
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/auto_form', methods=['GET', 'POST'])
def auto_form():
    if 'uid' not in session:
        flash("Please log in.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        oil_file = request.files.get('oil_file')
        antifreeze_file = request.files.get('antifreeze_file')
        extra_info = request.form.get('extra_info')

        if oil_file and allowed_file(oil_file.filename):
            filename = secure_filename(oil_file.filename)
            oil_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if antifreeze_file and allowed_file(antifreeze_file.filename):
            filename = secure_filename(antifreeze_file.filename)
            antifreeze_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # You can save `extra_info` or log it
        print("Extra Info:", extra_info)

        flash("Files uploaded successfully.")
        return redirect(url_for('auto_form'))

    username = session.get('username')
    uid = session.get('uid')

    month_name, year, calendar_weeks, month_num = get_current_month_year()
    today = datetime.today()

    return render_template(
        'auto_form.html',
        user=username,
        uid=uid,
        month=month_name,
        year=year,
        month_num=month_num,
        calendar_weeks=calendar_weeks,
        today_year=today.year,
        today_month=today.month,
        today_day=today.day
    )


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
