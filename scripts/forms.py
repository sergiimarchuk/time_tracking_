from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TimeField, TextAreaField
from wtforms.validators import DataRequired, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Go')

class WorkHoursForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    extra_info = TextAreaField('Extra Info (optional)')
    submit = SubmitField('Add Task')

    def validate_end_time(self, field):
        if self.start_time.data and field.data <= self.start_time.data:
            raise ValidationError('End time must be after start time.')

class ContactForm(FlaskForm):
    email = StringField('Your Email', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
