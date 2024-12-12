from flask import Flask, request, jsonify, render_template, abort
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
import jwt, os, datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app) 
app.config['SECRET_KEY'] = 'isahc8u2e0921e12osa00-=[./vds]'  # Ganti dengan secret key
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'qwdu92y17wesu81')
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME', 'masteraldi2809@gmail.com'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD', 'xthezwlpdajgtlav')
)

mail = Mail(app)
s = URLSafeTimedSerializer(app.config['JWT_SECRET_KEY'])
uri = "mongodb+srv://rizkydwisaputrar1:iqyCCfGc7vg9j_r@halosus.mwdayc6.mongodb.net/?retryWrites=true&w=majority&appName=halosus"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    db = client.web_sekolah
    users_collection = db.users
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    
# Fungsi untuk verifikasi token
@app.route('/verify-token', methods=['POST'])
def verify_token():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print(decoded_token['role'])
        return jsonify({'valid': True, 'username': decoded_token['username'],'role': decoded_token['role']})
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'message': 'Invalid token'}), 403
@app.errorhandler(404)
def page_not_found(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404

@app.route('/invalid')
def invalid():
    abort(404)
    
from . import view, api_login, api_guru, api_murid