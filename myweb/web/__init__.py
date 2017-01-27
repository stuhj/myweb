#encoding=UTF-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = '123456'


login_manager = LoginManager(app)
login_manager.login_view = '/regloginpage'



app.jinja_env.add_extension('jinja2.ext.loopcontrols')
#加载配置文件
app.config.from_pyfile('app.conf')
db = SQLAlchemy(app)
from web import views,models
