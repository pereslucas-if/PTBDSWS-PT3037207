from flask import render_template, session, redirect, url_for, flash

from . import main
from .forms import NameForm

from app.models import (
    inicializar_banco,
    carregar_usuarios,
    adicionar_usuario,
    carregar_emails
)

from app.email import send_email


inicializar_banco()


@main.route('/', methods=['GET', 'POST'])
def index():

    form = NameForm()

    if form.validate_on_submit():

        nome = form.name.data

        novo_usuario = adicionar_usuario(nome)

        if novo_usuario:

            send_email(
                subject='Novo usuário',
                new_username=nome,
                additional_email=form.email.data
            )

            session['name'] = nome

            flash('Usuário cadastrado e e-mails enviados com sucesso.')

        else:

            session['name'] = nome

            flash('Esse usuário já está cadastrado.')

        return redirect(url_for('main.index'))

    usuarios = carregar_usuarios()

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        usuarios=usuarios
    )


@main.route('/emailsEnviados')
def emails_enviados():

    emails = carregar_emails()

    return render_template(
        'emailsEnviados.html',
        emails=emails
    )