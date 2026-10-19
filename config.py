import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(basedir, '.env'))


MODO_PROFESSOR = True


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    API_KEY = os.environ.get('API_KEY')
    API_URL = os.environ.get('API_URL')
    API_FROM = os.environ.get('API_FROM')

    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'

    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')

    MY_PRIMARY_EMAIL = os.environ.get('MY_PRIMARY_EMAIL')

    MY_INSTITUTIONAL_EMAIL = os.environ.get(
        'MY_INSTITUTIONAL_EMAIL'
    )

    STUDENT_NAME = os.environ.get(
        'STUDENT_NAME',
        'Lucas Peres Gomes'
    )

    STUDENT_ID = os.environ.get(
        'STUDENT_ID',
        'PT3037207'
    )

    MODO_PROFESSOR = MODO_PROFESSOR