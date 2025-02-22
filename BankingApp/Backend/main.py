from flask import Flask
from models import db
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes import api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking.db'
app.config['JWT_SECRET_KEY'] = 'j2xvP6rAfwWpjV1UAugs3idnS6Z9Q6Z2'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app, origins="*")
jwt = JWTManager(app)

app.register_blueprint(api, url_prefix='/api')
@app.route('/')
def home():
    return "Banking App API"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)