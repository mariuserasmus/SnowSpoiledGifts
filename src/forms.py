from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length

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
