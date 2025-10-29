from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class EmailSignupForm(FlaskForm):
    """Form for email signup"""

    name = StringField(
        'Name',
        validators=[
            DataRequired(message='Please enter your name'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Please enter your email'),
            Email(message='Please enter a valid email address')
        ]
    )

    interests = SelectMultipleField(
        'What are you interested in?',
        choices=[
            ('3d_printing', '3D Printing'),
            ('sublimation', 'Sublimation'),
            ('vinyl', 'Vinyl'),
            ('giftboxes', 'Giftboxes'),
            ('candles_soaps', 'Candles and Soaps'),
            ('seasonal_events', 'Seasonal Events & Specials')
        ]
    )


class RegistrationForm(FlaskForm):
    """Form for user registration"""

    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Please enter your name'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ]
    )

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please enter your email'),
            Email(message='Please enter a valid email address')
        ]
    )

    phone = StringField(
        'Phone Number',
        validators=[
            Length(max=20, message='Phone number must be less than 20 characters')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Please enter a password'),
            Length(min=6, max=100, message='Password must be at least 6 characters')
        ]
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ]
    )


class LoginForm(FlaskForm):
    """Form for user login"""

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please enter your email'),
            Email(message='Please enter a valid email address')
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Please enter your password')
        ]
    )


class EditProfileForm(FlaskForm):
    """Form for editing user profile"""

    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Please enter your name'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ]
    )

    email = StringField(
        'Email Address',
        validators=[
            DataRequired(message='Please enter your email'),
            Email(message='Please enter a valid email address')
        ]
    )

    phone = StringField(
        'Phone Number',
        validators=[
            Length(max=20, message='Phone number must be less than 20 characters')
        ]
    )
