from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, PasswordField, RadioField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

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

    def validate(self, extra_validators=None):
        """Override validate to normalize email to lowercase"""
        rv = super(EmailSignupForm, self).validate(extra_validators)
        if self.email.data:
            self.email.data = self.email.data.lower().strip()
        return rv

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

    def validate(self, extra_validators=None):
        """Override validate to normalize email to lowercase"""
        rv = super(RegistrationForm, self).validate(extra_validators)
        if self.email.data:
            self.email.data = self.email.data.lower().strip()
        return rv


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

    def validate(self, extra_validators=None):
        """Override validate to normalize email to lowercase"""
        rv = super(LoginForm, self).validate(extra_validators)
        if self.email.data:
            self.email.data = self.email.data.lower().strip()
        return rv


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

    def validate(self, extra_validators=None):
        """Override validate to normalize email to lowercase"""
        rv = super(EditProfileForm, self).validate(extra_validators)
        if self.email.data:
            self.email.data = self.email.data.lower().strip()
        return rv


class CheckoutForm(FlaskForm):
    """Form for checkout with shipping address"""

    shipping_method = RadioField(
        'Shipping Method',
        choices=[
            ('pickup', 'Pickup in George - FREE'),
            ('own_courier', 'I will arrange my own Courier - FREE'),
            ('pudo', 'We arrange Courier (PUDO/Courier Guy) - See rates below')
        ],
        default='pickup',
        validators=[DataRequired(message='Please select a shipping method')]
    )

    pudo_option = SelectField(
        'PUDO Delivery Option',
        choices=[
            ('', '-- Select delivery option --'),
            ('locker_to_locker', 'Locker-to-Locker - R69'),
            ('locker_to_kiosk', 'Locker-to-Kiosk - R79'),
            ('locker_to_door', 'Locker-to-Door - R109'),
            ('kiosk_to_door', 'Kiosk-to-Door - R119')
        ],
        validators=[Optional()]
    )

    locker_location = TextAreaField(
        'PUDO Locker/Kiosk Location',
        validators=[
            Optional(),
            Length(max=500, message='Location must be less than 500 characters')
        ]
    )

    name = StringField(
        'Full Name',
        validators=[
            DataRequired(message='Please enter your name'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters')
        ]
    )

    phone = StringField(
        'Phone Number',
        validators=[
            DataRequired(message='Please enter your phone number'),
            Length(max=20, message='Phone number must be less than 20 characters')
        ]
    )

    address = StringField(
        'Street Address',
        validators=[
            Optional(),
            Length(max=200, message='Address must be less than 200 characters')
        ]
    )

    city = StringField(
        'City',
        validators=[
            Optional(),
            Length(max=100, message='City must be less than 100 characters')
        ]
    )

    state = StringField(
        'Province/State',
        validators=[
            Optional(),
            Length(max=100, message='Province/State must be less than 100 characters')
        ]
    )

    postal_code = StringField(
        'Postal Code',
        validators=[
            Optional(),
            Length(max=20, message='Postal code must be less than 20 characters')
        ]
    )

    country = StringField(
        'Country',
        validators=[
            Optional(),
            Length(max=100, message='Country must be less than 100 characters')
        ]
    )

    payment_method = RadioField(
        'Payment Method',
        choices=[
            ('eft', 'EFT/Bank Transfer'),
            ('cash_on_delivery', 'Cash on Delivery')
        ],
        default='eft',
        validators=[DataRequired(message='Please select a payment method')]
    )


class ChangePasswordForm(FlaskForm):
    """Form for changing user password"""

    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message='Please enter your current password')
        ]
    )

    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='Please enter a new password'),
            Length(min=6, max=100, message='Password must be at least 6 characters')
        ]
    )

    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your new password'),
            EqualTo('new_password', message='Passwords must match')
        ]
    )
