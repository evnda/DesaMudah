
-- ==========================================
-- DATABASE DESAMUDAH
-- ==========================================

CREATE DATABASE IF NOT EXISTS desamudah
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE desamudah;

-- ==========================================
-- 1. TABEL USERS
-- ==========================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    no_hp VARCHAR(20),
    alamat TEXT,
    role ENUM('masyarakat', 'admin', 'kepala_desa')
        NOT NULL DEFAULT 'masyarakat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==========================================
-- 2. TABEL LAYANAN
-- ==========================================

CREATE TABLE layanan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_layanan VARCHAR(150) NOT NULL,
    kategori VARCHAR(100) NOT NULL,
    deskripsi TEXT,
    prosedur TEXT,
    estimasi_hari INT DEFAULT 3,
    perlu_persetujuan BOOLEAN DEFAULT FALSE,
    status_aktif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==========================================
-- 3. TABEL PERSYARATAN
-- ==========================================

CREATE TABLE persyaratan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    layanan_id INT NOT NULL,
    nama_persyaratan VARCHAR(150) NOT NULL,
    keterangan TEXT,

    FOREIGN KEY (layanan_id)
        REFERENCES layanan(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- 4. TABEL PENGAJUAN
-- ==========================================

CREATE TABLE pengajuan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nomor_pengajuan VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    layanan_id INT NOT NULL,
    data_formulir JSON,
    status ENUM(
        'menunggu_verifikasi',
        'perlu_perbaikan',
        'sedang_diproses',
        'menunggu_persetujuan',
        'selesai',
        'ditolak'
    ) NOT NULL DEFAULT 'menunggu_verifikasi',
    catatan_admin TEXT,
    hasil_dokumen VARCHAR(255),
    tanggal_pengajuan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    FOREIGN KEY (layanan_id)
        REFERENCES layanan(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- 5. TABEL DOKUMEN PENGAJUAN
-- ==========================================

CREATE TABLE dokumen_pengajuan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pengajuan_id INT NOT NULL,
    nama_file VARCHAR(255) NOT NULL,
    path_file VARCHAR(255) NOT NULL,
    tipe_file VARCHAR(50),
    ukuran_file INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pengajuan_id)
        REFERENCES pengajuan(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- 6. TABEL RIWAYAT STATUS
-- ==========================================

CREATE TABLE riwayat_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pengajuan_id INT NOT NULL,
    aktor_id INT NULL,
    status VARCHAR(50) NOT NULL,
    catatan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pengajuan_id)
        REFERENCES pengajuan(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (aktor_id)
        REFERENCES users(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- 7. TABEL PERSETUJUAN
-- ==========================================

CREATE TABLE persetujuan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pengajuan_id INT NOT NULL,
    pejabat_id INT NOT NULL,
    keputusan ENUM('disetujui', 'ditolak') NOT NULL,
    catatan TEXT,
    tanggal_persetujuan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pengajuan_id)
        REFERENCES pengajuan(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (pejabat_id)
        REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- 8. TABEL KNOWLEDGE BASE CHATBOT
-- ==========================================

CREATE TABLE knowledge_base (
    id INT AUTO_INCREMENT PRIMARY KEY,
    intent VARCHAR(100) NOT NULL,
    pertanyaan TEXT NOT NULL,
    kata_kunci TEXT,
    jawaban TEXT NOT NULL,
    kategori VARCHAR(100),
    status_aktif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==========================================
-- 9. TABEL CHAT LOGS
-- ==========================================

CREATE TABLE chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    pesan_user TEXT NOT NULL,
    jawaban_bot TEXT NOT NULL,
    intent_terdeteksi VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- 10. TABEL NOTIFIKASI
-- ==========================================

CREATE TABLE notifikasi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    judul VARCHAR(150) NOT NULL,
    pesan TEXT NOT NULL,
    sudah_dibaca BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==========================================
-- DATA AWAL LAYANAN
-- ==========================================

INSERT INTO layanan
(nama_layanan, kategori, deskripsi, prosedur, estimasi_hari, perlu_persetujuan)
VALUES
(
    'Surat Keterangan Domisili',
    'Surat Keterangan',
    'Layanan pembuatan surat keterangan domisili.',
    'Masyarakat mengisi formulir dan mengunggah dokumen persyaratan.',
    2, FALSE
),
(
    'Surat Keterangan Usaha',
    'Surat Keterangan',
    'Layanan pembuatan surat keterangan usaha.',
    'Masyarakat mengisi data usaha dan mengunggah dokumen persyaratan.',
    2, FALSE
),
(
    'Surat Pengantar Nikah',
    'Surat Pengantar',
    'Layanan pengajuan surat pengantar nikah.',
    'Masyarakat mengisi data calon pengantin dan mengunggah dokumen.',
    3, TRUE
),
(
    'Pengantar Perubahan Kartu Keluarga',
    'Administrasi Kependudukan',
    'Layanan pengantar untuk proses perubahan data kartu keluarga.',
    'Masyarakat mengisi formulir dan mengunggah dokumen pendukung.',
    3, FALSE
),
(
    'Pengantar Pindah Domisili',
    'Administrasi Kependudukan',
    'Layanan pengantar untuk proses pindah domisili.',
    'Masyarakat mengisi alamat asal, tujuan, dan dokumen pendukung.',
    3, FALSE
),
(
    'Surat Keterangan Tidak Mampu',
    'Surat Keterangan',
    'Layanan pengajuan surat keterangan tidak mampu.',
    'Masyarakat mengisi formulir dan melengkapi dokumen pendukung.',
    3, TRUE
);
