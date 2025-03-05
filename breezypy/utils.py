import jwt
import datetime
from config import ALLOWED_EXTENSIONS, SECRET_KEY, REFRESH_SECRET_KEY

def allowed_file(filename):
    """Проверка расширения файла"""
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

def generate_access_token(username):
    """Создание access-токена"""
    return jwt.encode(
        {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)},
        SECRET_KEY, algorithm="HS256"
    )


def generate_refresh_token(username):
    """Создание refresh-токена"""
    return jwt.encode(
        {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)},
        REFRESH_SECRET_KEY, algorithm="HS256"
    )