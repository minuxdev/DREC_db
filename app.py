from flask import Flask


app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'LAJDJFLA'