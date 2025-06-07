from flask import Flask
from stores import stores_bp
from users import users_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(stores_bp)
app.register_blueprint(users_bp)

if __name__ == "__main__":
    app.run(debug=True)
