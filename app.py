from flask import Flask
from models import db

app = Flask(__name__)

app.config["SECRET_KEY"] = "super-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///database.db"

db.init_app(app)

@app.route("/")
def home():
    return "SecureVault läuft erfolgreich!"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
