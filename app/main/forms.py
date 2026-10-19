from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


class NameForm(FlaskForm):
    name = StringField(
        'Nome de usuário',
        validators=[DataRequired(), Length(1, 64)]
    )

    send_email = BooleanField(
        'Deseja enviar e-mail para flaskaulasweb@zohomail.com?'
    )

    submit = SubmitField('Cadastrar')