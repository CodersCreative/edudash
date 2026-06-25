from flask import Flask
from flask_cors import CORS
from model_database import db
import google_books_api_wrapper.api as books

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

GOOGLE_BOOKS_CLIENT = books.GoogleBooksAPI();
