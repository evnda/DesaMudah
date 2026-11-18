from database import get_db_connection
from werkzeug.security import generate_password_hash
from getpass import getpass


def buat_akun(nama, email, role):
    print(f"\nMembuat akun {role.upper()}")

    password = getpass("Masukkan password: ")
    konfirmasi = getpass("Ulangi password: ")

    if password != konfirmasi:
        print("Password tidak sama!")
        return

    if len(password) < 8:
        print("Password minimal 8 karakter!")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            print("Email sudah digunakan!")
            return

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users
            (nama, email, password, role)
            VALUES (%s, %s, %s, %s)
        """, (nama, email, password_hash, role))

        conn.commit()
        print(f"Akun {role} berhasil dibuat!")

    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan:", e)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    buat_akun(
        "Admin Desa",
        "admin@desamudah.test",
        "admin"
    )

    buat_akun(
        "Kepala Desa",
        "kepala@desamudah.test",
        "kepala_desa"
    )
