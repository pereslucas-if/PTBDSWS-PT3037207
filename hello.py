import os
import requests
from threading import Thread
from dotenv import load_dotenv
import json

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, '.env'))

USERS_FILE = os.path.join(basedir, 'usuarios.json')


def carregar_usuarios():
    if not os.path.exists(USERS_FILE):
        usuarios = [
            {
                "nome": "john",
                "funcao": "Administrator"
            }
        ]

        with open(USERS_FILE, 'w', encoding='utf-8') as arquivo:
            json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)

        return usuarios

    with open(USERS_FILE, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)


def salvar_usuarios(usuarios):
    with open(USERS_FILE, 'w', encoding='utf-8') as arquivo:
        json.dump(usuarios, arquivo, ensure_ascii=False, indent=4)


def adicionar_usuario(nome):
    usuarios = carregar_usuarios()

    for usuario in usuarios:
        if usuario['nome'].lower() == nome.lower():
            return False

    usuarios.append({
        "nome": nome,
        "funcao": "User"
    })

    salvar_usuarios(usuarios)
    return True


app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'

app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'

app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

app.config['MY_PRIMARY_EMAIL'] = os.environ.get('MY_PRIMARY_EMAIL')

app.config['MY_INSTITUTIONAL_EMAIL'] = os.environ.get(
    'MY_INSTITUTIONAL_EMAIL'
)

app.config['STUDENT_NAME'] = os.environ.get(
    'STUDENT_NAME',
    'Lucas Peres Gomes'
)

app.config['STUDENT_ID'] = os.environ.get(
    'STUDENT_ID',
    'PT3037207'
)


bootstrap = Bootstrap(app)

moment = Moment(app)


class NameForm(FlaskForm):

    name = StringField(
        'Qual é o seu nome?',
        validators=[DataRequired()]
    )

    send_email = BooleanField(
        'Deseja enviar e-mail para flaskaulasweb@zohomail.com?'
    )

    submit = SubmitField('Submit')


def send_async_email(
    app_context,
    recipients,
    subject,
    html_content
):
    with app_context:

        api_key = app.config['API_KEY']
        api_url = app.config['API_URL']
        api_from = app.config['API_FROM']

        for recipient in recipients:

            if not recipient:
                continue

            try:

                response = requests.post(
                    api_url,
                    auth=('api', api_key),
                    data={
                        'from': api_from,
                        'to': [recipient],
                        'subject': subject,
                        'html': html_content
                    }
                )

                print(
                    f'[Mailgun] Envio para {recipient} - '
                    f'Status: {response.status_code}'
                )

                if response.status_code >= 400:
                    print(
                        f'[Mailgun] Resposta: {response.text}'
                    )

            except Exception as e:

                print(
                    f'[Mailgun] Erro ao enviar para '
                    f'{recipient}: {e}'
                )


def send_email(
    subject,
    new_username,
    send_to_primary=False
):

    recipients = [
        app.config['MY_INSTITUTIONAL_EMAIL']
    ]

    if send_to_primary:

        recipients.append(
            'flaskaulasweb@zohomail.com'
        )

    full_subject = (
        app.config['FLASKY_MAIL_SUBJECT_PREFIX']
        + ' '
        + subject
    )

    html_content = f"""
    <h3>Novo Usuário Cadastrado</h3>

    <p>
        <b>Prontuário do Aluno:</b>
        {app.config['STUDENT_ID']}
    </p>

    <p>
        <b>Nome do Aluno:</b>
        {app.config['STUDENT_NAME']}
    </p>

    <p>
        <b>Novo Usuário Cadastrado:</b>
        {new_username}
    </p>
    """

    thr = Thread(
        target=send_async_email,
        args=[
            app.app_context(),
            recipients,
            full_subject,
            html_content
        ]
    )

    thr.start()

    return thr


@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        '404.html'
    ), 404


@app.errorhandler(500)
def internal_server_error(e):

    return render_template(
        '500.html'
    ), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    if form.validate_on_submit():
        nome = form.name.data

        novo_usuario = adicionar_usuario(nome)

        if novo_usuario:
            send_email(
                subject='Novo usuário cadastrado',
                new_username=nome,
                send_to_primary=form.send_email.data
            )

            session['name'] = nome

            if form.send_email.data:
                flash('Usuário cadastrado e e-mail enviado.')
            else:
                flash('Usuário cadastrado e e-mail institucional enviado.')

        else:
            session['name'] = nome
            flash('Esse usuário já está cadastrado.')

        return redirect(url_for('index'))

    usuarios = carregar_usuarios()

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        usuarios=usuarios
    )


if __name__ == '__main__':

    app.run(debug=True)