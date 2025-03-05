import os
import requests
from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import jwt
import datetime
from functools import wraps
from config import SECRET_KEY, FILE_DIRECTORY, AUTH_URL
from utils import allowed_file, generate_access_token, generate_refresh_token

def token_required(f):
    """Декоратор для проверки токена"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.username = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def register_routes(app):
    # Получение списка файлов в директории
    @app.route('/api/filesinfo', methods=['GET'])
    def get_files_info():
        try:
            files = []
            for filename in os.listdir(FILE_DIRECTORY):
                if allowed_file(filename):
                    file_path = os.path.join(FILE_DIRECTORY, filename)
                    file_info = {
                        "name": filename,
                        "size": str(os.path.getsize(file_path)),
                        "creation_date": datetime.utcfromtimestamp(os.path.getctime(file_path)).strftime(
                            '%Y-%m-%d %H:%M:%S'),
                        "content": ""
                    }
                    # Чтение содержимого файла
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_info["content"] = file.read()

                    files.append(file_info)

            return jsonify(files), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/register', methods=['POST'])
    def register():
        """Регистрация пользователя"""
        username = request.json.get('username')
        password = request.json.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Отправляем запрос на внешний сервер для регистрации
        response = requests.post('http://localhost:8080/User/register',
                                 json={"login": username, "password": password})
        if response.status_code == 201:
            # Если регистрация успешна, производим авторизацию
            access_token = generate_access_token(username)
            refresh_token = generate_refresh_token(username)
            return jsonify({
                "message": "Registration successful",
                "access_token": access_token,
                "refresh_token": refresh_token
            }), 201
        else:
            # Возвращаем ошибку, если регистрация на сервере не удалась
            return jsonify({"error": response.json().get("error", "Registration failed")}), response.status_code

    @app.route('/api/login', methods=['POST'])
    def login():
        """Авторизация пользователя"""
        username = request.json.get('username')
        password = request.json.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Отправляем запрос на внешний сервер для авторизации
        response = requests.post(AUTH_URL, json={"login": username, "password": password})
        if response.status_code == 200:
            access_token = generate_access_token(username)
            refresh_token = generate_refresh_token(username)
            return jsonify({"access_token": access_token, "refresh_token": refresh_token})
        return jsonify({"error": "Invalid credentials"}), 401

    @app.route('/api/files', methods=['GET'])
    @token_required
    def get_files():
        """Получение списка файлов пользователя"""
        user_dir = os.path.join(FILE_DIRECTORY, request.username)
        try:
            files = os.listdir(user_dir)
            return jsonify(files), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/upload', methods=['POST'])
    @token_required
    def upload_file():
        """Загрузка файла"""
        user_dir = os.path.join(FILE_DIRECTORY, request.username)
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_dir, filename))
            return jsonify({"message": f"File {filename} uploaded successfully"}), 200
        return jsonify({"error": "File type not allowed"}), 400

    @app.route('/api/download/<filename>', methods=['GET'])
    @token_required
    def download_file(filename):
        """Скачивание файла"""
        user_dir = os.path.join(FILE_DIRECTORY, request.username)
        try:
            return send_from_directory(user_dir, filename, as_attachment=True)
        except Exception as e:
            return jsonify({"error": str(e)}), 404

    @app.route('/api/delete/<filename>', methods=['DELETE'])
    @token_required
    def delete_file(filename):
        """Удаление файла"""
        user_dir = os.path.join(FILE_DIRECTORY, request.username)
        file_path = os.path.join(user_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": f"File {filename} deleted successfully"}), 200
        return jsonify({"error": "File not found"}), 404

    @app.route('/api/file_info/<filename>', methods=['GET'])
    @token_required
    def get_file_info(filename):
        """Получение информации о файле по названию"""
        user_dir = os.path.join(FILE_DIRECTORY, request.username)
        file_path = os.path.join(user_dir, filename)
        if os.path.exists(file_path):
            file_info = {
                "filename": filename,
                "size": os.path.getsize(file_path),
                "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            return jsonify(file_info), 200
        return jsonify({"error": "File not found"}), 404
