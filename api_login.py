from . import app, bcrypt, users_collection, mail, s
from flask import request, jsonify, url_for, render_template_string, flash, render_template
from flask_mail import Message
from itsdangerous import BadSignature, SignatureExpired
import jwt, re, datetime
# Fungsi login user dan menghasilkan token
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({"msg": "username salah"}), 404
    if not bcrypt.check_password_hash(user['password'], password):
        return jsonify({"msg": "password salah"}), 401
    if user['verify_email'] == False:
        return jsonify({"msg": "anda belum memverifikasi email"}), 401
    if user and bcrypt.check_password_hash(user['password'], password):
        # Membuat token dengan waktu kedaluwarsa 24 jam
        print(user['role'])
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'nama_lengkap': user['nama_lengkap'],
            'email': user['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({'token': token})
    else:
        return jsonify({'mesg': 'Invalid credentials'}), 401
    
def is_valid_email(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    return re.match(regex, email)

# Fungsi registrasi user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    nama_lengkap = data['nama_lengkap']
    email = data['email']
    re_password = data['re_password']

    if not username or not email or not password or not re_password:
        return jsonify({"msg": "All fields are required"}), 400

    if not is_valid_email(email):
        return jsonify({"msg": "Invalid email format"}), 400

    if password != re_password:
        return jsonify({"msg": "Passwords do not match"}), 400
    cek_username =  users_collection.find_one({'username':username})
    if cek_username:
        return jsonify({"msg": "Username already exists"}), 400
    cek_email =  users_collection.find_one({'email':email})
    if cek_email:
        return jsonify({"msg": "Email already exists"}), 400
    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Simpan user baru
    user = {
        'username': username,
        'password': hashed_password,
        'nama_lengkap': nama_lengkap,
        'email': email,
        'verify_email': False,
        'role':'murid'
    }
    try:
        token = s.dumps(email, salt='email-confirm')

        conf_email_url = url_for('confirm_email', token=token, _external=True)
        email_body = render_template_string('''
            Hello {{ username }},
            
            Anda menerima email ini, karena kami memerlukan verifikasi email untuk akun Anda agar aktif dan dapat digunakan.
            
            Silakan klik tautan di bawah ini untuk verifikasi email Anda. Tautan ini akan kedaluwarsa dalam 1 jam.
            
            confirm your email: {{ conf_email_url }}
            
            hubungi dukungan jika Anda memiliki pertanyaan.
            
            Untuk bantuan lebih lanjut, silakan hubungi tim dukungan kami di developer masteraldi2809@gmail.com .
            
            Salam Hangat,
            
            Admin
        ''', username=username,  conf_email_url=conf_email_url)

        msg = Message('Confirmasi Email Anda',
                    sender='masteraldi2809@gmail.com', recipients=[email])

        msg.body = email_body
        mail.send(msg)
        result = users_collection.insert_one(user)
        if result.inserted_id:
            return jsonify({'msg': 'User registered successfully, Please check your email for validation'}), 201
        else:
            return jsonify({'error': 'Failed to register user'}), 500
    except Exception as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500

@app.route('/confirm_email/<token>', methods=['GET','POST'])
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return jsonify({"msg": "Token telah kedaluwarsa"}), 400
    except BadSignature:
        return jsonify({"msg": "Token tidak valid"}), 400
    
    user = users_collection.find_one({'email':email})
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Update the verify_email field to True
    result = users_collection.update_one(
        {"email": email},          # Filter berdasarkan email atau id user
        {"$set": {"verify_email": True}} # Set field verify_email ke True
    )

    # Cek apakah update berhasil
    if result.modified_count > 0:
        return '''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Email Verify</title>
        </head>
        <body>
            <h1>Email Telah Terverifikasi </h1>
        </body>
        </html>
        '''.format(token)
    else:
        return jsonify({"msg":"update failed."}),500
@app.route("/verif_email",methods=["POST"])
def verif_email():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"msg": "Email harus diisi"})
        
    user = users_collection.find_one({'email':email})
    print(user)
    if not user:
        return jsonify({"msg": "Email tidak ditemukan"})
    verified_user = users_collection.find_one({'email':email,'verify_email':True})
    print(verified_user)
    if verified_user:
        return jsonify({"msg": "user sudah terverifikasi"})
    token = s.dumps(email, salt='email-confirm')
    conf_email_url = url_for('confirm_email', token=token, _external=True)
    email_body = render_template_string('''
        Hello {{ username }},
        
        Anda menerima email ini, karena kami memerlukan verifikasi email untuk akun Anda agar aktif dan dapat digunakan.
        
        Silakan klik tautan di bawah ini untuk verifikasi email Anda. Tautan ini akan kedaluwarsa dalam 1 jam.
        
        confirm your email: {{ conf_email_url }}
        
        hubungi dukungan jika Anda memiliki pertanyaan.
        
        Untuk bantuan lebih lanjut, silakan hubungi tim dukungan kami di developer masteraldi2809@gmail.com .
        
        Salam Hangat,
        
        Pejuang D4
    ''', username=user['username'],  conf_email_url=conf_email_url)
    msg = Message('Confirmasi Email Anda',
                sender='masteraldi2809@gmail.com', recipients=[email])
    msg.body = email_body
    mail.send(msg)
    flash("Silahkan cek email anda.")
    return jsonify({"msg":"Silahkan cek email anda."})

    
@app.route("/forgotpassword",methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"msg": "Email harus diisi"})
        
    user = users_collection.find_one({'email':email})
    if not user:
        return jsonify({"msg": "Email tidak ditemukan"})
    token = s.dumps(email, salt='reset-password')
    
    from_param = request.args.get('from')
    if "forgot_password.html" in from_param:
        mod = from_param.replace('forgot_password.html', '')
        reset_password_url = mod+"/reset_password.html?token="+token 
    else:
        reset_password_url = url_for('reset_password', token=token, _external=True)
    email_body = render_template_string('''
        Hello {{ user["name"] }},
        
        Anda menerima email ini, karena kami menerima permintaan untuk mengatur ulang kata sandi akun Anda.
        
        Silakan klik tautan di bawah ini untuk mengatur ulang kata sandi Anda. Tautan ini akan kedaluwarsa dalam 1 jam.
        
        Reset your password: {{ reset_password_url }}
        
        Jika Anda tidak meminta pengaturan ulang kata sandi, abaikan email ini atau hubungi dukungan jika Anda memiliki pertanyaan.
        
        Untuk bantuan lebih lanjut, silakan hubungi tim dukungan kami di developer masteraldi2809@gmail.com .
        
        Salam Hangat,
        
        Mriki_Project
    ''', user=user,  reset_password_url=reset_password_url)
    msg = Message('Reset Kata Sandi Anda',
                sender='masteraldi2809@gmail.com', recipients=[email])
    msg.body = email_body
    mail.send(msg)
    return jsonify({"msg": "Email untuk mereset kata sandi telah dikirim."})

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        try:
            email = s.loads(token, salt='reset-password', max_age=3600)
        except SignatureExpired:
            return jsonify({"msg": "Token telah kedaluwarsa"}), 400
        except BadSignature:
            return jsonify({"msg": "Token tidak valid"}), 400
        
        user = users_collection.find_one({'email':email})
        
        if not user:
            return jsonify({"msg": "User not found"}), 404
        data = request.get_json()
        password = data.get('password')

        # Hash the new password and update it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        result = users_collection.update_one(
            {"email": email},          # Filter berdasarkan email atau id user
            {"$set": {"password": hashed_password}} # Set field verify_email ke True
        )

        # Cek apakah update berhasil
        if result.modified_count > 0:
            flash('Password berhasil direset. Silakan login dengan password baru Anda.')
            return jsonify({"msg": "Sukses"})
        else:
            return jsonify({"msg":"update failed."}),500
    return render_template("reset_password.html",token=token)
