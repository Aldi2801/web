from . import app, bcrypt, users_collection
from flask import request, jsonify, render_template, redirect, url_for
import jwt
import datetime

@app.route('/')
def hello_fly():
    # return 'hello from fly.io'
    return redirect(url_for("view_dashboard"))
@app.route('/login')
def view_login():
    return render_template("login.html")
@app.route('/register')
def view_register():
    return render_template("register.html")
@app.route('/dashboard')
def view_dashboard():
    return render_template("dashboard.html")
@app.route('/daftar_hadir_ujian')
def view_daftar_hadir_ujian():
    return render_template("daftar_hadir_siswa_ujian.html")
@app.route('/daftar_hadir')
def view_daftar_hadir():
    return render_template("daftar_hadir_siswa.html")
@app.route('/manage_jadwal')
def view_manage_jadwal():
    return render_template("manage_jadwal_new.html")
@app.route('/manage_kehadiran')
def view_manage_kehadiran():
    return render_template("manage_kehadiran.html")
@app.route('/manage_ujian')
def view_manage_ujian():
    return render_template("manage_ujian.html")
@app.route('/menu_pembayaran')
def view_menu_pembayaran():
    return render_template("menu_pembayaran.html")
@app.route('/verif_email')
def view_verif_email():
    return render_template("verif_email.html")
@app.route("/forgot_password")
def view_forgot_password():
    return render_template("forgot_password.html")