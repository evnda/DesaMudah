import re
import mysql.connector
from config import Config
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    render_template, redirect, url_for,
    session, request, flash, current_app
)
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from functools import wraps
from database import get_db_connection
from config import Config
from flask import send_from_directory
from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.config.from_object(Config)
UPLOAD_FOLDER = os.path.join(
    app.root_path, 'uploads', 'dokumen')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HASIL_FOLDER = os.path.join(app.root_path, 'uploads', 'hasil')
os.makedirs(HASIL_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

# =====================================
# DEKORATOR LOGIN
# =====================================

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu.", "error")
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


# =====================================
# HALAMAN BERANDA
# =====================================

@app.route("/")
def index():
    return render_template("index.html")


# =====================================
# REGISTRASI MASYARAKAT
# =====================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        nama = request.form.get("nama", "").strip()
        email = request.form.get("email", "").strip().lower()
        no_hp = request.form.get("no_hp", "").strip()
        alamat = request.form.get("alamat", "").strip()
        password = request.form.get("password", "")
        konfirmasi = request.form.get("konfirmasi_password", "")

        if not nama or not email or not password:
            flash("Nama, email, dan password wajib diisi.", "error")
            return redirect(url_for("register"))

        if password != konfirmasi:
            flash("Konfirmasi password tidak cocok.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password minimal 8 karakter.", "error")
            return redirect(url_for("register"))

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():
                flash("Email sudah terdaftar.", "error")
                return redirect(url_for("register"))

            password_hash = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO users
                (nama, email, password, no_hp, alamat, role)
                VALUES (%s, %s, %s, %s, %s, 'masyarakat')
            """, (
                nama, email, password_hash, no_hp, alamat
            ))

            connection.commit()

            flash("Registrasi berhasil. Silakan login.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            if connection:
                connection.rollback()

            print("Error registrasi:", e)
            flash("Terjadi kesalahan saat registrasi.", "error")

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    return render_template("register.html")


# =====================================
# LOGIN
# =====================================


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, nama, email, password, role
                FROM users
                WHERE email = %s
            """, (email,))

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password"], password
            ):
                session.clear()
                session["user_id"] = user["id"]
                session["nama"] = user["nama"]
                session["email"] = user["email"]
                session["role"] = user["role"]

                flash("Login berhasil!", "success")
                return redirect(url_for("dashboard"))

            flash("Email atau password salah.", "error")

        except Exception as e:
            print("Error login:", e)
            flash("Terjadi kesalahan saat login.", "error")

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    return render_template("login.html")


# =====================================
# LAYANAN
# =====================================

@app.route('/layanan')
def daftar_layanan():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM layanan
            WHERE status_aktif = 1
            ORDER BY id ASC
        """)

        data_layanan = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'layanan.html',
        layanan=data_layanan
    )



@app.route('/layanan/<int:id>')
def detail_layanan(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM layanan
            WHERE id = %s AND status_aktif = 1
        """, (id,))

        layanan = cursor.fetchone()

        if layanan is None:
            return "Layanan tidak ditemukan", 404

        cursor.execute("""
            SELECT nama_persyaratan, keterangan
            FROM persyaratan
            WHERE layanan_id = %s
            ORDER BY id ASC
        """, (id,))

        persyaratan = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'detail_layanan.html',
        layanan=layanan,
        persyaratan=persyaratan
    )


@app.route('/ajukan/<int:id>', methods=['GET', 'POST'])
def ajukan_layanan(id):

    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM layanan
            WHERE id = %s AND status_aktif = 1
        """, (id,))

        layanan = cursor.fetchone()

        if layanan is None:
            flash('Layanan tidak ditemukan.', 'danger')
            return redirect(url_for('daftar_layanan'))

        cursor.execute("""
            SELECT *
            FROM persyaratan
            WHERE layanan_id = %s
            ORDER BY id ASC
        """, (id,))

        persyaratan = cursor.fetchall()

        if request.method == 'POST':

            data_formulir = {
                'nama_lengkap': request.form.get('nama_lengkap', '').strip(),
                'nik_dummy': request.form.get('nik_dummy', '').strip(),
                'alamat': request.form.get('alamat', '').strip(),
                'no_hp': request.form.get('no_hp', '').strip(),
                'keterangan': request.form.get('keterangan', '').strip()
            }

            if not all([
                data_formulir['nama_lengkap'],
                data_formulir['alamat'],
                data_formulir['no_hp']
            ]):
                flash('Nama, alamat, dan nomor HP wajib diisi.', 'danger')
                return render_template(
                    'form_pengajuan.html',
                    layanan=layanan,
                    persyaratan=persyaratan
                )

            files = request.files.getlist('dokumen')

            if len(files) != len(persyaratan) or not files:
                flash('Unggah satu dokumen untuk setiap persyaratan.', 'danger')
                return render_template(
                    'form_pengajuan.html',
                    layanan=layanan,
                    persyaratan=persyaratan
                )

            file_data = []

            for file in files:
                if not file or not file.filename:
                    flash('Semua dokumen wajib dipilih.', 'danger')
                    return render_template(
                        'form_pengajuan.html',
                        layanan=layanan,
                        persyaratan=persyaratan
                    )

                ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''

                if ext not in ALLOWED_EXTENSIONS:
                    flash('Format dokumen harus PDF, JPG, JPEG, atau PNG.', 'danger')
                    return render_template(
                        'form_pengajuan.html',
                        layanan=layanan,
                        persyaratan=persyaratan
                    )

                file.seek(0, os.SEEK_END)
                ukuran = file.tell()
                file.seek(0)

                if ukuran == 0 or ukuran > MAX_FILE_SIZE:
                    flash('Ukuran setiap dokumen harus lebih dari 0 dan maksimal 2 MB.', 'danger')
                    return render_template(
                        'form_pengajuan.html',
                        layanan=layanan,
                        persyaratan=persyaratan
                    )

                nama_aman = secure_filename(file.filename)

                nama_simpan = (
                    uuid.uuid4().hex + '_' + nama_aman
                )

                file_data.append({
                    'file': file,
                    'nama': nama_simpan,
                    'asli': nama_aman,
                    'ukuran': ukuran,
                    'tipe': file.mimetype
                })

            nomor = 'DM-' + datetime.now().strftime('%Y%m%d%H%M%S') + '-' + uuid.uuid4().hex[:4].upper()

            file_tersimpan = []

            try:
                cursor.execute("""
                    INSERT INTO pengajuan
                    (nomor_pengajuan, user_id, layanan_id,
                     data_formulir, status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    nomor,
                    session['user_id'],
                    id,
                    json.dumps(data_formulir, ensure_ascii=False),
                    'menunggu_verifikasi'
                ))

                pengajuan_id = cursor.lastrowid

                for item in file_data:
                    lokasi = os.path.join(
                        UPLOAD_FOLDER,
                        item['nama']
                    )

                    item['file'].save(lokasi)
                    file_tersimpan.append(lokasi)

                    cursor.execute("""
                        INSERT INTO dokumen_pengajuan
                        (pengajuan_id, nama_file, path_file,
                         tipe_file, ukuran_file)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        pengajuan_id,
                        item['asli'],
                        lokasi,
                        item['tipe'],
                        item['ukuran']
                    ))

                cursor.execute("""
                    INSERT INTO riwayat_status
                    (pengajuan_id, aktor_id, status, catatan)
                    VALUES (%s, %s, %s, %s)
                """, (
                    pengajuan_id,
                    session['user_id'],
                    'menunggu_verifikasi',
                    'Pengajuan berhasil dikirim oleh masyarakat.'
                ))

                conn.commit()

                flash(
                    f'Pengajuan berhasil dikirim. Nomor: {nomor}',
                    'success'
                )

                return redirect(url_for('daftar_layanan'))

            except Exception:
                conn.rollback()

                for lokasi in file_tersimpan:
                    if os.path.exists(lokasi):
                        os.remove(lokasi)

                raise

        return render_template(
            'form_pengajuan.html',
            layanan=layanan,
            persyaratan=persyaratan
        )

    finally:
        cursor.close()
        conn.close()


@app.route('/pengajuan-saya')
def pengajuan_saya():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'masyarakat':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.nomor_pengajuan,
                p.status,
                p.catatan_admin,
                p.hasil_dokumen,
                p.tanggal_pengajuan,
                p.updated_at,
                l.nama_layanan
            FROM pengajuan p
            JOIN layanan l ON p.layanan_id = l.id
            WHERE p.user_id = %s
            ORDER BY p.tanggal_pengajuan DESC
        """, (session['user_id'],))

        daftar_pengajuan = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'pengajuan_saya.html',
        pengajuan=daftar_pengajuan
    )

# =====================================
# PENGAJUAN
# =====================================


@app.route('/admin/pengajuan')
def admin_pengajuan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    # Daftar status yang boleh digunakan sebagai filter
    daftar_status = {
        'menunggu_verifikasi': 'Pengajuan Baru',
        'menunggu_persetujuan': 'Menunggu Persetujuan Kepala Desa',
        'sedang_diproses': 'Sedang Diproses',
        'selesai': 'Pengajuan Selesai',
        'perlu_perbaikan': 'Perlu Perbaikan',
        'ditolak': 'Ditolak'
    }

    status_filter = request.args.get('status', '').strip()

    if status_filter not in daftar_status:
        status_filter = ''

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.nomor_pengajuan,
                p.status,
                p.tanggal_pengajuan,
                p.updated_at,
                u.nama,
                l.nama_layanan
            FROM pengajuan p
            JOIN users u ON p.user_id = u.id
            JOIN layanan l ON p.layanan_id = l.id
            WHERE (%s = '' OR p.status = %s)
            ORDER BY p.tanggal_pengajuan DESC
        """, (status_filter, status_filter))

        daftar_pengajuan = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'admin_pengajuan.html',
        pengajuan=daftar_pengajuan,
        status_filter=status_filter,
        daftar_status=daftar_status
    )


@app.route('/admin/pengajuan/<int:id>')
def detail_admin_pengajuan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    print("DATABASE AKTIF:",conn.database)

    try:
        cursor.execute("""
            SELECT
                p.*,
                u.nama,
                u.email,
                l.nama_layanan,
                l.perlu_persetujuan
            FROM pengajuan p
            JOIN users u ON p.user_id = u.id
            JOIN layanan l ON p.layanan_id = l.id
            WHERE p.id = %s
        """, (id,))

        pengajuan = cursor.fetchone()

        if pengajuan is None:
            return "Pengajuan tidak ditemukan", 404

        cursor.execute("""
            SELECT *
            FROM dokumen_pengajuan
            WHERE pengajuan_id = %s
        """, (id,))

        dokumen = cursor.fetchall()
        
        cursor.execute("""
            SELECT
                r.*,
                u.nama AS nama_aktor
            FROM riwayat_status r
            LEFT JOIN users u ON r.aktor_id = u.id
            WHERE r.pengajuan_id = %s
            ORDER BY r.created_at DESC
        """, (id,))

        riwayat = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    data_formulir = json.loads(
        pengajuan['data_formulir'] or '{}'
    )

    return render_template(
        'detail_admin_pengajuan.html',
        pengajuan=pengajuan,
        dokumen=dokumen,
        riwayat=riwayat,
        data_formulir=data_formulir
    )



@app.route('/admin/pengajuan/<int:id>/proses', methods=['POST'])
def proses_pengajuan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    aksi = request.form.get('aksi')
    catatan = request.form.get('catatan', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.user_id,
                p.status,
                l.perlu_persetujuan
            FROM pengajuan p
            JOIN layanan l ON p.layanan_id = l.id
            WHERE p.id = %s
            FOR UPDATE
        """, (id,))

        data = cursor.fetchone()

        if data is None:
            conn.rollback()
            return "Pengajuan tidak ditemukan", 404

        if data['status'] != 'menunggu_verifikasi':
            conn.rollback()
            flash('Pengajuan ini sudah pernah diproses.', 'error')
            return redirect(url_for('detail_admin_pengajuan', id=id))

        if aksi == 'terima':
            if data['perlu_persetujuan'] == 1:
                status_baru = 'menunggu_persetujuan'
                pesan = 'Pengajuan diteruskan kepada kepala desa untuk persetujuan.'
            else:
                status_baru = 'sedang_diproses'
                pesan = 'Pengajuan diterima dan sedang diproses.'

        elif aksi == 'perbaikan':
            status_baru = 'perlu_perbaikan'
            pesan = catatan

        elif aksi == 'tolak':
            status_baru = 'ditolak'
            pesan = catatan

        else:
            conn.rollback()
            flash('Tindakan tidak valid.', 'error')
            return redirect(url_for('detail_admin_pengajuan', id=id))

        if aksi in ['perbaikan', 'tolak'] and not catatan:
            conn.rollback()
            flash('Catatan wajib diisi.', 'error')
            return redirect(url_for('detail_admin_pengajuan', id=id))

        cursor.execute("""
            UPDATE pengajuan
            SET status = %s,
                catatan_admin = %s
            WHERE id = %s
        """, (status_baru, catatan or None, id))

        cursor.execute("""
            INSERT INTO riwayat_status
            (pengajuan_id, aktor_id, status, catatan)
            VALUES (%s, %s, %s, %s)
        """, (
            id,
            session['user_id'],
            status_baru,
            pesan
        ))
        # Membuat notifikasi untuk masyarakat
        if aksi == 'terima':
            if data['perlu_persetujuan'] == 1:
                judul_notifikasi = "Pengajuan Diteruskan"
                isi_notifikasi = "Pengajuan kamu telah diverifikasi admin dan diteruskan kepada kepala desa."
            else:
                judul_notifikasi = "Pengajuan Diterima"
                isi_notifikasi = "Pengajuan kamu telah diterima admin dan sedang diproses."

        elif aksi == 'perbaikan':
            judul_notifikasi = "Pengajuan Perlu Perbaikan"
            isi_notifikasi = f"Pengajuan kamu perlu diperbaiki. Catatan admin: {catatan}"

        else:
            judul_notifikasi = "Pengajuan Ditolak"
            isi_notifikasi = f"Pengajuan kamu ditolak. Alasan: {catatan}"

        buat_notifikasi(
            cursor,
            data['user_id'],
            judul_notifikasi,
            isi_notifikasi
        )

        conn.commit()
        flash('Pengajuan berhasil diperbarui.', 'success')

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('detail_admin_pengajuan', id=id))

@app.route('/admin/pengajuan/<int:id>/selesaikan', methods=['POST'])
def selesaikan_pengajuan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    file = request.files.get('hasil_dokumen')

    if not file or file.filename == '':
        flash('Silakan pilih dokumen hasil terlebih dahulu.', 'error')
        return redirect(url_for('detail_admin_pengajuan', id=id))

    ekstensi = file.filename.rsplit('.', 1)[-1].lower()

    if '.' not in file.filename or ekstensi not in {'pdf', 'jpg', 'jpeg', 'png'}:
        flash('Format dokumen harus PDF, JPG, JPEG, atau PNG.', 'error')
        return redirect(url_for('detail_admin_pengajuan', id=id))

    if file.content_length and file.content_length > MAX_FILE_SIZE:
        flash('Ukuran dokumen maksimal 2 MB.', 'error')
        return redirect(url_for('detail_admin_pengajuan', id=id))

    nama_file = f"hasil_{id}_{uuid.uuid4().hex}.{ekstensi}"
    path_file = os.path.join(HASIL_FOLDER, nama_file)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, user_id, status
            FROM pengajuan
            WHERE id = %s
            FOR UPDATE
        """, (id,))

        data = cursor.fetchone()

        if not data:
            flash('Pengajuan tidak ditemukan.', 'danger')
            return redirect(url_for('admin_pengajuan'))
        file.save(path_file)

        cursor.execute("""
            UPDATE pengajuan
            SET status = 'selesai',
                hasil_dokumen = %s
            WHERE id = %s
        """, (nama_file, id))

        cursor.execute("""
            INSERT INTO riwayat_status
            (pengajuan_id, aktor_id, status, catatan)
            VALUES (%s, %s, %s, %s)
        """, (
            id,
            session['user_id'],
            'selesai',
            'Pengajuan telah selesai diproses oleh admin.'
        ))
        buat_notifikasi(
            cursor,
            data['user_id'],
            "Dokumen Pengajuan Selesai",
            "Pengajuan kamu telah selesai diproses. Silakan buka halaman Pengajuan Saya untuk mengunduh dokumen hasil."
            )
        
        conn.commit()
        flash('Pengajuan berhasil diselesaikan!', 'success')

    except Exception:
        conn.rollback()

        if os.path.exists(path_file):
            os.remove(path_file)

        raise

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('detail_admin_pengajuan', id=id))


@app.route('/admin/status-pengajuan')
def admin_status_pengajuan():
    return redirect(url_for('admin_pengajuan'))



@app.route('/admin/status-pengajuan/<int:id>')
def detail_status_pengajuan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.*,
                u.nama,
                u.email,
                l.nama_layanan,
                l.perlu_persetujuan
            FROM pengajuan p
            JOIN users u ON p.user_id = u.id
            JOIN layanan l ON p.layanan_id = l.id
            WHERE p.id = %s
        """, (id,))

        pengajuan = cursor.fetchone()

        if pengajuan is None:
            return "Pengajuan tidak ditemukan", 404

        cursor.execute("""
            SELECT *
            FROM dokumen_pengajuan
            WHERE pengajuan_id = %s
        """, (id,))

        dokumen = cursor.fetchall()

        cursor.execute("""
            SELECT
                r.*,
                u.nama AS nama_aktor
            FROM riwayat_status r
            LEFT JOIN users u ON r.aktor_id = u.id
            WHERE r.pengajuan_id = %s
            ORDER BY r.created_at DESC
        """, (id,))

        riwayat = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    data_formulir = json.loads(
        pengajuan['data_formulir'] or '{}'
    )

    return render_template(
        'detail_status_pengajuan.html',
        pengajuan=pengajuan,
        dokumen=dokumen,
        riwayat=riwayat,
        data_formulir=data_formulir
    )


@app.route('/kepala/persetujuan')
def daftar_persetujuan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'kepala_desa':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.nomor_pengajuan,
                p.status,
                p.tanggal_pengajuan,
                u.nama,
                l.nama_layanan
            FROM pengajuan p
            JOIN users u ON p.user_id = u.id
            JOIN layanan l ON p.layanan_id = l.id
            WHERE p.status = 'menunggu_persetujuan'
            ORDER BY p.tanggal_pengajuan ASC
        """)

        daftar = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'daftar_persetujuan.html',
        pengajuan=daftar
    )


@app.route('/kepala/persetujuan/<int:id>')
def detail_persetujuan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'kepala_desa':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.*,
                u.nama,
                u.email,
                l.nama_layanan
            FROM pengajuan p
            JOIN users u ON p.user_id = u.id
            JOIN layanan l ON p.layanan_id = l.id
            WHERE p.id = %s
              AND p.status = 'menunggu_persetujuan'
        """, (id,))

        pengajuan = cursor.fetchone()

        if pengajuan is None:
            return "Pengajuan tidak ditemukan atau sudah diproses.", 404

        cursor.execute("""
            SELECT *
            FROM dokumen_pengajuan
            WHERE pengajuan_id = %s
        """, (id,))

        dokumen = cursor.fetchall()

        cursor.execute("""
            SELECT
                r.*,
                u.nama AS nama_aktor
            FROM riwayat_status r
            LEFT JOIN users u ON r.aktor_id = u.id
            WHERE r.pengajuan_id = %s
            ORDER BY r.created_at DESC
        """, (id,))

        riwayat = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    data_formulir = json.loads(
        pengajuan['data_formulir'] or '{}'
    )

    return render_template(
        'detail_persetujuan.html',
        pengajuan=pengajuan,
        dokumen=dokumen,
        riwayat=riwayat,
        data_formulir=data_formulir
    )


@app.route('/kepala/persetujuan/<int:id>/proses', methods=['POST'])
def proses_persetujuan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'kepala_desa':
        return redirect(url_for('dashboard'))

    keputusan = request.form.get('keputusan')
    catatan = request.form.get('catatan', '').strip()

    if keputusan not in ['disetujui', 'ditolak']:
        flash('Keputusan tidak valid.', 'error')
        return redirect(url_for('detail_persetujuan', id=id))

    if keputusan == 'ditolak' and not catatan:
        flash('Alasan penolakan wajib diisi.', 'error')
        return redirect(url_for('detail_persetujuan', id=id))

    status_baru = (
        'sedang_diproses'
        if keputusan == 'disetujui'
        else 'ditolak'
    )

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.user_id,
                p.status,
                l.perlu_persetujuan
            FROM pengajuan p
            JOIN layanan l ON p.layanan_id = l.id
            WHERE p.id = %s
            FOR UPDATE
        """, (id,))
        data = cursor.fetchone()

        if data is None:
            conn.rollback()
            flash('Pengajuan tidak ditemukan atau sudah diproses.', 'error')
            return redirect(url_for('daftar_persetujuan'))

        cursor.execute("""
            INSERT INTO persetujuan
            (pengajuan_id, pejabat_id, keputusan, catatan)
            VALUES (%s, %s, %s, %s)
        """, (
            id,
            session['user_id'],
            keputusan,
            catatan or 'Pengajuan disetujui oleh kepala desa.'
        ))

        if keputusan == 'disetujui':
            judul_notifikasi = "Pengajuan Disetujui Kepala Desa"
            isi_notifikasi = (
                "Pengajuan kamu telah disetujui oleh kepala desa "
                "dan akan dilanjutkan ke tahap pemrosesan."
            )
        else:
            judul_notifikasi = "Pengajuan Ditolak Kepala Desa"
            isi_notifikasi = f"Pengajuan kamu ditolak oleh kepala desa. Catatan: {catatan}"

        buat_notifikasi(
            cursor,
            data['user_id'],
            judul_notifikasi,
            isi_notifikasi
        )

        cursor.execute("""
            UPDATE pengajuan
            SET status = %s,
                catatan_admin = %s
            WHERE id = %s
        """, (
            status_baru,
            catatan or None,
            id
        ))

        cursor.execute("""
            INSERT INTO riwayat_status
            (pengajuan_id, aktor_id, status, catatan)
            VALUES (%s, %s, %s, %s)
        """, (
            id,
            session['user_id'],
            status_baru,
            catatan or 'Pengajuan disetujui oleh kepala desa.'
        ))

        conn.commit()
        flash('Keputusan kepala desa berhasil disimpan.', 'success')

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('daftar_persetujuan'))


@app.route('/pengajuan/<int:id>/unduh-hasil')
def unduh_hasil_pengajuan(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT hasil_dokumen
            FROM pengajuan
            WHERE id = %s
              AND user_id = %s
              AND status = 'selesai'
        """, (id, session['user_id']))

        data = cursor.fetchone()

    finally:
        cursor.close()
        conn.close()

    if not data or not data['hasil_dokumen']:
        return "Dokumen tidak ditemukan atau akses ditolak.", 404

    return send_from_directory(
        HASIL_FOLDER,
        data['hasil_dokumen'],
        as_attachment=True
    )

def buat_notifikasi(cursor, user_id, judul, pesan):
    cursor.execute("""
        INSERT INTO notifikasi (user_id, judul, pesan)
        VALUES (%s, %s, %s)
    """, (user_id, judul, pesan))


@app.route('/kepala/riwayat-persetujuan')
def riwayat_persetujuan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'kepala_desa':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.nomor_pengajuan,
                p.status,
                p.tanggal_pengajuan,
                u.nama,
                l.nama_layanan,
                ps.keputusan,
                ps.catatan
            FROM persetujuan ps
            JOIN pengajuan p ON ps.pengajuan_id = p.id
            JOIN users u ON p.user_id = u.id
            JOIN layanan l ON p.layanan_id = l.id
            WHERE ps.pejabat_id = %s
            ORDER BY p.tanggal_pengajuan DESC
        """, (session['user_id'],))

        daftar_riwayat = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'riwayat_persetujuan.html',
        pengajuan=daftar_riwayat
    )


@app.route('/notifikasi')
def daftar_notifikasi():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'masyarakat':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM notifikasi
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (session['user_id'],))

        daftar = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'notifikasi.html',
        notifikasi=daftar
    )


@app.route('/kepala/semua-pengajuan')
def semua_pengajuan_kepala():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'kepala_desa':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.nomor_pengajuan,
                p.status,
                p.tanggal_pengajuan,
                p.updated_at,
                u.nama,
                l.nama_layanan
            FROM pengajuan p
            JOIN users u ON p.user_id = u.id
            JOIN layanan l ON p.layanan_id = l.id
            WHERE EXISTS (
                SELECT 1
                FROM riwayat_status rs
                WHERE rs.pengajuan_id = p.id
                AND rs.status = 'menunggu_persetujuan'
            )
            ORDER BY p.tanggal_pengajuan DESC
        """)

        daftar_pengajuan = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'semua_pengajuan_kepala.html',
        pengajuan=daftar_pengajuan
    )


@app.route('/kepala/rekap-pelayanan')
def rekap_pelayanan_kepala():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'kepala_desa':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Mengambil ringkasan pengajuan yang pernah diteruskan
        # kepada Kepala Desa.
        cursor.execute("""
            SELECT
                COUNT(*) AS total_pengajuan,

                COALESCE(SUM(
                    p.status = 'menunggu_persetujuan'
                ), 0) AS menunggu,

                COALESCE(SUM(
                    EXISTS (
                        SELECT 1
                        FROM persetujuan ps
                        WHERE ps.pengajuan_id = p.id
                        AND ps.keputusan = 'disetujui'
                    )
                ), 0) AS disetujui,

                COALESCE(SUM(
                    EXISTS (
                        SELECT 1
                        FROM persetujuan ps
                        WHERE ps.pengajuan_id = p.id
                        AND ps.keputusan = 'ditolak'
                    )
                ), 0) AS ditolak,

                COALESCE(SUM(
                    p.status = 'selesai'
                ), 0) AS selesai

            FROM pengajuan p
            WHERE EXISTS (
                SELECT 1
                FROM riwayat_status rs
                WHERE rs.pengajuan_id = p.id
                AND rs.status = 'menunggu_persetujuan'
            )
        """)

        ringkasan = cursor.fetchone()

        # Mengambil rekap berdasarkan jenis layanan
        cursor.execute("""
            SELECT
                l.nama_layanan,
                COUNT(p.id) AS jumlah
            FROM pengajuan p
            JOIN layanan l ON p.layanan_id = l.id
            WHERE EXISTS (
                SELECT 1
                FROM riwayat_status rs
                WHERE rs.pengajuan_id = p.id
                AND rs.status = 'menunggu_persetujuan'
            )
            GROUP BY l.id, l.nama_layanan
            ORDER BY jumlah DESC
        """)

        rekap_layanan = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template(
        'rekap_pelayanan_kepala.html',
        ringkasan=ringkasan,
        rekap_layanan=rekap_layanan
    )

@app.route('/kepala/statistik-pelayanan')
def statistik_pelayanan_kepala():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'kepala_desa':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('dashboard'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT status, COUNT(*) AS jumlah
        FROM pengajuan
        WHERE EXISTS (
            SELECT 1
            FROM riwayat_status rs
            WHERE rs.pengajuan_id = pengajuan.id
              AND rs.status = 'menunggu_persetujuan'
        )
        GROUP BY status
    """)

    data_statistik = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'statistik_pelayanan_kepala.html',
        data_statistik=data_statistik
    )

@app.route('/notifikasi/<int:id>/baca', methods=['POST'])
def baca_notifikasi(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'masyarakat':
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE notifikasi
            SET sudah_dibaca = 1
            WHERE id = %s AND user_id = %s
        """, (id, session['user_id']))

        conn.commit()
        flash('Notifikasi berhasil ditandai sudah dibaca.', 'success')

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('daftar_notifikasi'))

# =====================================
# DASHBOARD
# =====================================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    role = session.get('role')

    if role == 'masyarakat':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT COUNT(*) AS jumlah
                FROM notifikasi
                WHERE user_id = %s AND sudah_dibaca = 0
            """, (session['user_id'],))

            jumlah_notifikasi = cursor.fetchone()['jumlah']

        finally:
            cursor.close()
            conn.close()

        return render_template(
            'dashboard_masyarakat.html',
            jumlah_notifikasi=jumlah_notifikasi
        )

    elif role == 'admin':
        return render_template('dashboard_admin.html')

    elif role == 'kepala_desa':
        return render_template('dashboard_kepala.html')

    else:
        return redirect(url_for('logout'))

# =====================================
# LOGOUT
# =====================================

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Anda berhasil logout.", "success")
    return redirect(url_for("login"))




def chatbot_jawab(pesan, role=None):
    pesan = pesan.lower().strip()

    pesan_bersih = re.sub(r'[^\w\s]', ' ', pesan)
    pesan_bersih = re.sub(r'\s+', ' ', pesan_bersih).strip()

    daftar_role = ['masyarakat', 'admin', 'kepala_desa']

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT intent, pertanyaan, kata_kunci, jawaban, kategori
            FROM knowledge_base
            WHERE status_aktif = 1
        """)

        data_pengetahuan = cursor.fetchall()

        # Menyamakan penulisan kategori agar tidak sensitif
        # terhadap huruf besar dan kecil.
        for data in data_pengetahuan:
            data['kategori_normal'] = (
                (data['kategori'] or '').strip().lower()
            )

        def cari_jawaban(data_list):
            jawaban_terbaik = None
            skor_tertinggi = 0

            for data in data_list:
                kata_kunci = data['kata_kunci'] or ""

                daftar_kata = [
                    kata.strip().lower()
                    for kata in kata_kunci.split(',')
                    if kata.strip()
                ]

                skor = 0

                for kata in daftar_kata:
                    kata_bersih = re.sub(
                        r'[^\w\s]', ' ', kata
                    )
                    kata_bersih = re.sub(
                        r'\s+', ' ', kata_bersih
                    ).strip()

                    if not kata_bersih:
                        continue

                    # Kata tunggal harus cocok sebagai satu kata utuh.
                    if ' ' not in kata_bersih:
                        if kata_bersih in pesan_bersih.split():
                            skor += 2

                    # Frasa harus cocok sebagai rangkaian kata.
                    elif kata_bersih in pesan_bersih:
                        skor += 3

                if skor > skor_tertinggi:
                    skor_tertinggi = skor
                    jawaban_terbaik = data['jawaban']

            return jawaban_terbaik

        role = (role or '').strip().lower()

        # Tahap 1: Cari jawaban khusus sesuai role pengguna.
        if role in daftar_role:

            pengetahuan_role = [
                data for data in data_pengetahuan
                if data['kategori_normal'] == role
            ]

            jawaban = cari_jawaban(pengetahuan_role)

            if jawaban:
                return jawaban

        # Tahap 2: Hanya boleh mengambil kategori umum.
        # Tidak boleh mengambil kategori milik role lain.
        kategori_umum = ['', 'umum', 'publik', 'pengunjung']

        pengetahuan_umum = [
            data for data in data_pengetahuan
            if data['kategori_normal'] in kategori_umum
        ]

        jawaban = cari_jawaban(pengetahuan_umum)

        if jawaban:
            return jawaban

        return (
            "Maaf, saya belum memahami pertanyaan tersebut. "
            "Silakan gunakan pertanyaan yang lebih spesifik "
            "sesuai fitur dan hak akses akun Anda."
        )

    except Exception as e:
        print("Error chatbot:", e)
        return "Maaf, chatbot sedang mengalami gangguan. Silakan coba kembali."

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


@app.route('/chatbot/pesan', methods=['POST'])
def chatbot_pesan():
    data = request.get_json(silent=True) or {}

    pesan = data.get('pesan', '').strip()

    if not pesan:
        return jsonify({
            'status': 'error',
            'jawaban': 'Silakan ketik pertanyaan terlebih dahulu.'
        }), 400

    # Mengambil role pengguna yang sedang login
    role = session.get('role')

    # Menampilkan role di terminal Flask
    print("ROLE CHATBOT:", role)

    # Memproses pertanyaan
    jawaban = chatbot_jawab(pesan, role)

    return jsonify({
        'status': 'success',
        'jawaban': jawaban
    })


if __name__ == "__main__":
    app.run(debug=True)

