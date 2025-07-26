import os
import sys
sys.path.insert(0, '/opt/dev-py/TimeTracking-dev/libs')

from flask import Flask, render_template, flash, redirect, url_for, session
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

from scripts.auth_checker import authenticate as ldap_authenticate
from scripts.current_month_year import get_current_month_year
from scripts.uid_openldap_getting import authenticate_and_get_info as ldap_uid

from scripts.forms import AutoUploadForm


from scripts.forms import LoginForm, WorkHoursForm, AutoUploadForm

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
    
from scripts.db_ops import get_user_id_by_uid, create_user_if_not_exists
    
@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if authenticate_user(username, password):
            uid = getting_unig_id(username, password)
            #uid = getting_unig_id(username, password).get("entryUUID")
            if uid:
                session['username'] = username
                session['uid'] = uid

                # ✅ Ensure user exists in DB
                user_id = get_user_id_by_uid(uid)
                if not user_id:
                    user_id = create_user_if_not_exists(
                        uid,
                        vor_name=username,
                        nach_name='LDAP',
                        email=f'{username}@example.com'
                    )

                month_name, year, calendar_weeks, month_num = get_current_month_year()
                return render_template(
                    'success.html',
                    user=username, month=month_name,
                    month_num=month_num, year=year,
                    calendar_weeks=calendar_weeks, uid=uid
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



from datetime import datetime
import os
from werkzeug.utils import secure_filename
from scripts.db_ops import get_user_id_by_uid, create_user_if_not_exists, insert_vehicle, insert_vehicle_file, get_user_files_by_uid

@app.route('/auto_form', methods=['GET', 'POST'])
def auto_form():
    if 'uid' not in session or 'username' not in session:
        flash("Please log in.")
        return redirect(url_for('login'))

    uid = session.get('uid')
    username = session.get('username')
    form = AutoUploadForm()

    if form.validate_on_submit():
        plate_number = form.plate_number.data
        oil_file = form.oil_file.data
        antifreeze_file = form.antifreeze_file.data
        extra_info = form.extra_info.data

        if not (allowed_file(oil_file.filename) and allowed_file(antifreeze_file.filename)):
            flash("Invalid file type.")
            return redirect(url_for('auto_form'))

        # Get user_id from DB
        user_id = get_user_id_by_uid(uid)
        if not user_id:
            flash("User not found.")
            return redirect(url_for('login'))

        # Current year and month strings
        now = datetime.now()
        year_str = now.strftime("%Y")
        month_str = now.strftime("%m")

        # Get original extensions
        oil_ext = os.path.splitext(oil_file.filename)[1].lower()
        antifreeze_ext = os.path.splitext(antifreeze_file.filename)[1].lower()

        # Build new filenames
        oil_filename = f"{year_str}_{month_str}_{user_id}_Oil_Level{oil_ext}"
        antifreeze_filename = f"{year_str}_{month_str}_{user_id}_Antifreeze_Level{antifreeze_ext}"

        # Secure the filenames
        oil_filename = secure_filename(oil_filename)
        antifreeze_filename = secure_filename(antifreeze_filename)

        # Save files
        oil_path = os.path.join(app.config['UPLOAD_FOLDER'], oil_filename)
        antifreeze_path = os.path.join(app.config['UPLOAD_FOLDER'], antifreeze_filename)

        oil_file.save(oil_path)
        antifreeze_file.save(antifreeze_path)

        # DB insert
        vehicle_id = insert_vehicle(user_id, plate_number, extra_info)
        insert_vehicle_file(vehicle_id, 'oil_level', oil_filename)
        insert_vehicle_file(vehicle_id, 'antifreeze_level', antifreeze_filename)

        flash("Vehicle info and files uploaded successfully.")
        return redirect(url_for('auto_form'))

    return render_template('auto_form.html', form=form, user=username, uid=uid)




from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if 'uid' not in session:
        flash("Unauthorized access.")
        return redirect(url_for('login'))

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


from scripts.db_ops import get_user_files_by_uid


@app.route('/list_files')
def list_files():
    if 'uid' not in session:
        flash("Please log in.")
        return redirect(url_for('login'))

    uid = session['uid']
    username = session.get('username')  

    files = get_user_files_by_uid(uid)
    return render_template('list_files.html', files=files, user=username)  # ✅ Correct




from scripts.forms import ContactForm  # make sure this is imported
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        email = form.email.data
        message = form.message.data
        print(f"Contact form submitted by {email}: {message}")
        flash("Message sent successfully!")
        return redirect(url_for('contact'))
    uid = session['uid']
    username = session.get('username')      

    return render_template('contact.html', form=form, user=username)  # <-- this is crucial



@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
