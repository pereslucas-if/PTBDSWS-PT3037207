import os
import requests
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Carrega as variáveis do arquivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

# Variáveis do Mailgun e da aplicação (padrão dos slides do professor)
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['MY_PRIMARY_EMAIL'] = os.environ.get('MY_PRIMARY_EMAIL')
app.config['MY_INSTITUTIONAL_EMAIL'] = os.environ.get('MY_INSTITUTIONAL_EMAIL')
app.config['STUDENT_NAME'] = os.environ.get('STUDENT_NAME', 'Lucas Peres Gomes')
app.config['STUDENT_ID'] = os.environ.get('STUDENT_ID', 'PT3037207')

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


def send_async_email(app_context, recipients, subject, html_content):
    """Executa o envio via API do Mailgun em background"""
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
                    auth=("api", api_key),
                    data={
                        "from": api_from,
                        "to": [recipient],
                        "subject": subject,
                        "html": html_content
                    }
                )
                print(f"[Mailgun] Envio para {recipient} - Status: {response.status_code}")
            except Exception as e:
                print(f"[Mailgun] Erro ao enviar para {recipient}: {e}")


def send_email(subject, new_username):
    """Monta o HTML diretamente no Python e dispara a Thread"""
    recipients = list(set([
        app.config['FLASKY_ADMIN'],
        app.config['MY_INSTITUTIONAL_EMAIL'],
        app.config['MY_PRIMARY_EMAIL']
    ]))

    full_subject = app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject

    # HTML gerado diretamente sem precisar de ficheiro de template
    html_content = f"""
    <h3>Novo Usuário Cadastrado</h3>
    <p><b>Prontuário do Aluno:</b> {app.config['STUDENT_ID']}</p>
    <p><b>Nome do Aluno:</b> {app.config['STUDENT_NAME']}</p>
    <p><b>Novo Usuário Cadastrado:</b> {new_username}</p>
    """

    thr = Thread(
        target=send_async_email,
        args=[app.app_context(), recipients, full_subject, html_content]
    )
    thr.start()
    return thr


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is None or old_name != form.name.data:
            send_email(
                subject='Novo usuário cadastrado',
                new_username=form.name.data
            )
            flash('Um email foi enviado ao seu endereço.')

        session['name'] = form.name.data
        return redirect(url_for('index'))

    return render_template('index.html', form=form, name=session.get('name'))


if __name__ == '__main__':
    app.run(debug=True)