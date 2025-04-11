from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, IntegerField, BooleanField, SubmitField,
                     SelectField, SelectMultipleField)
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    name = StringField('Name', validators=[DataRequired()])
    city_from = StringField('City From', validators=[DataRequired()])
    submit = SubmitField('Register')


class AddJobForm(FlaskForm):
    job_title = StringField('Job Title', validators=[DataRequired()])
    team_leader_id = SelectField('Team Leader', coerce=int, validators=[DataRequired()])
    work_size = StringField('Work Size', validators=[DataRequired()])
    collaborators = StringField('Collaborators', validators=[DataRequired()])
    is_finished = BooleanField('Is job finished?')
    category_ids = SelectMultipleField('Categories', coerce=int)
    submit = SubmitField('Submit')


class AddDepartmentForm(FlaskForm):
    title = StringField('Title of department', validators=[DataRequired()])
    chief_id = SelectField('Chief', coerce=int, validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = StringField('Department Email', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditDepartmentForm(FlaskForm):
    title = StringField('Title of department', validators=[DataRequired()])
    chief_id = SelectField('Chief', coerce=int, validators=[DataRequired()])
    members = StringField('Members', validators=[DataRequired()])
    email = StringField('Department Email', validators=[DataRequired()])
    submit = SubmitField('Update')
