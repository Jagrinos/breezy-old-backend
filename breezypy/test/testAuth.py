from flask import Flask, request, jsonify
import jwt
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SECRET_KEY = "your_secret_key_here"
REFRESH_SECRET_KEY = "your_refresh_secret_key_here"
USERS = {
    "admin": "admin",
    "user": "user"
}

def generate_access_token(username):
    return jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
    }, SECRET_KEY, algorithm="HS256")

def generate_refresh_token(username):
    return jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, REFRESH_SECRET_KEY, algorithm="HS256")

@app.route("/api/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    if username in USERS and USERS[username] == password:
        access_token = generate_access_token(username)
        refresh_token = generate_refresh_token(username)
        return jsonify({"access_token": access_token, "refresh_token": refresh_token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/refresh", methods=["POST"])
def refresh():
    refresh_token = request.json.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), 401
    try:
        data = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
        username = data["username"]
        new_access_token = generate_access_token(username)
        return jsonify({"access_token": new_access_token})
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

@app.route("/api/verify", methods=["GET"])
def verify():
    token = request.headers.get("Authorization")
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return jsonify({"username": data["username"]})
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Access token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
    return jsonify({"error": "Token required"}), 401

if __name__ == "__main__":
    app.run(debug=True)
