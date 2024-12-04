from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_uploads import IMAGES, UploadSet, configure_uploads
from flask_msearch import Search
from flask_migrate import Migrate
import os
import pdfkit

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config.from_pyfile('config.cfg')
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


search = Search(db=db)  # Manually pass the SQLAlchemy db instance
search.init_app(app)

migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'please login first'

path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

from shop.products import route, models, forms
from shop.admin import models, route, forms
from shop.customer import route, models, forms
from shop.carts import carts, models