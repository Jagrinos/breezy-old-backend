import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
# Папка для хранения файлов
FILE_DIRECTORY = '../files'
ALLOWED_EXTENSIONS = {'txt'}


# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        files = os.listdir(FILE_DIRECTORY)
        print(files)
        return jsonify(files), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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


# Загрузка файла
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(FILE_DIRECTORY, filename))
        return jsonify({"message": f"File {filename} uploaded successfully"}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400


# Скачивание файла
@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(FILE_DIRECTORY, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# Удаление файла
@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_path = os.path.join(FILE_DIRECTORY, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"message": f"File {filename} deleted successfully"}), 200
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
