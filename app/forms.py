from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')




class TubeCalcForm(FlaskForm):
    lng1 = IntegerField('Length')
    qty1 = IntegerField('Quantity')
    ccl1 = BooleanField('Common Cut Left')
    ccr1 = BooleanField('Common Cut Right')

    lng2 = IntegerField('Length')
    qty2 = IntegerField('Quantity')
    ccl2 = BooleanField('Common Cut Left')
    ccr2 = BooleanField('Common Cut Right')

    lng3 = IntegerField('Length')
    qty3 = IntegerField('Quantity')
    ccl3 = BooleanField('Common Cut Left')
    ccr3 = BooleanField('Common Cut Right')

    lng4 = IntegerField('Length')
    qty4 = IntegerField('Quantity')
    ccl4 = BooleanField('Common Cut Left')
    ccr4 = BooleanField('Common Cut Right')

    lng5 = IntegerField('Length')
    qty5 = IntegerField('Quantity')
    ccl5 = BooleanField('Common Cut Left')
    ccr5 = BooleanField('Common Cut Right')

    lng6 = IntegerField('Length')
    qty6 = IntegerField('Quantity')
    ccl6 = BooleanField('Common Cut Left')
    ccr6 = BooleanField('Common Cut Right')

    lng7 = IntegerField('Length')
    qty7 = IntegerField('Quantity')
    ccl7 = BooleanField('Common Cut Left')
    ccr7 = BooleanField('Common Cut Right')

    lng8 = IntegerField('Length')
    qty8 = IntegerField('Quantity')
    ccl8 = BooleanField('Common Cut Left')
    ccr8 = BooleanField('Common Cut Right')

    lng9 = IntegerField('Length')
    qty9 = IntegerField('Quantity')
    ccl9 = BooleanField('Common Cut Left')
    ccr9 = BooleanField('Common Cut Right')

    lng10 = IntegerField('Length')
    qty10 = IntegerField('Quantity')
    ccl10 = BooleanField('Common Cut Left')
    ccr10 = BooleanField('Common Cut Right')

    submit = SubmitField('Submit')
