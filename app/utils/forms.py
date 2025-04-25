from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange

# ----------------------------
# User Registration Form
# ----------------------------
class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    user_type = SelectField('Account Type', choices=[('candidate', 'Candidate'), ('employer', 'Employer')], validators=[DataRequired()])
    submit = SubmitField('Sign Up')


# ----------------------------
# Login Form
# ----------------------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


# ----------------------------
# Candidate Profile Form
# ----------------------------
class CandidateProfileForm(FlaskForm):
    experience = IntegerField('Years of Experience', validators=[DataRequired(), NumberRange(min=0, max=50)])
    education = SelectField('Education Level', choices=[
        ('High School', 'High School'),
        ('Bachelor\'s', 'Bachelor\'s'),
        ('Master\'s', 'Master\'s'),
        ('PhD', 'PhD')
    ], validators=[DataRequired()])
    skills = TextAreaField('Technical Skills (comma-separated)', validators=[DataRequired()])
    salary = IntegerField('Expected Salary', validators=[DataRequired(), NumberRange(min=1000)])
    submit = SubmitField('Save Profile')


# ----------------------------
# Post Job Form
# ----------------------------
class PostJobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    required_skills = TextAreaField('Required Skills (comma-separated)', validators=[DataRequired()])
    required_education = SelectField('Minimum Education', choices=[
        ('High School', 'High School'),
        ('Bachelor\'s', 'Bachelor\'s'),
        ('Master\'s', 'Master\'s'),
        ('PhD', 'PhD')
    ], validators=[DataRequired()])
    salary_min = IntegerField('Minimum Salary', validators=[DataRequired()])
    salary_max = IntegerField('Maximum Salary', validators=[DataRequired()])
    job_type = SelectField('Job Type', choices=[
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Remote', 'Remote')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Post Job')
