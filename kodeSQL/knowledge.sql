INSERT INTO knowledge_base
(intent, pertanyaan, kata_kunci, jawaban, kategori, status_aktif)
VALUES

(
    'salam',
    'Halo, hai, selamat pagi',
    'halo,hai,hello,selamat pagi,selamat siang,selamat sore',
    'Halo! Selamat datang di layanan DesaMudah. Ada yang bisa saya bantu? Kamu bisa bertanya tentang layanan surat, persyaratan, pengajuan, dan status permohonan.',
    'Salam',
    1
),

(
    'layanan',
    'Layanan apa saja yang tersedia?',
    'layanan,jenis layanan,jenis surat,surat apa',
    'DesaMudah menyediakan berbagai layanan administrasi desa. Kamu dapat melihat daftar layanan yang tersedia melalui menu Layanan pada dashboard masyarakat.',
    'Layanan',
    1
),

(
    'persyaratan',
    'Apa saja persyaratan pengajuan surat?',
    'syarat,persyaratan,dokumen,berkas',
    'Persyaratan bergantung pada jenis surat yang kamu ajukan. Silakan buka menu Layanan, pilih jenis surat yang dibutuhkan, lalu baca informasi persyaratannya sebelum mengajukan.',
    'Persyaratan',
    1
),

(
    'pengajuan',
    'Bagaimana cara mengajukan surat?',
    'ajukan,pengajuan,cara mengajukan,membuat surat',
    'Untuk mengajukan surat, login sebagai masyarakat, buka menu layanan, pilih jenis surat, lengkapi formulir, unggah dokumen persyaratan, lalu kirim pengajuan.',
    'Pengajuan',
    1
),

(
    'status',
    'Bagaimana cara mengecek status pengajuan?',
    'status,cek status,proses pengajuan,pengajuan saya',
    'Kamu dapat melihat perkembangan pengajuan melalui menu Pengajuan Saya pada dashboard masyarakat. Di sana kamu dapat memantau status permohonan.',
    'Status',
    1
),

(
    'verifikasi',
    'Bagaimana proses verifikasi pengajuan?',
    'verifikasi,diperiksa,admin,pemeriksaan',
    'Setelah pengajuan dikirim, admin desa akan memeriksa data dan dokumen yang kamu unggah. Jika ada kekurangan, kamu dapat diminta melakukan perbaikan.',
    'Verifikasi',
    1
),

(
    'persetujuan',
    'Siapa yang menyetujui surat?',
    'persetujuan,kepala desa,disetujui,tanda tangan',
    'Pengajuan yang membutuhkan persetujuan akan diteruskan kepada kepala desa setelah proses pemeriksaan admin selesai.',
    'Persetujuan',
    1
),

(
    'unduh_surat',
    'Bagaimana cara mengunduh surat?',
    'unduh,download,hasil surat,surat selesai',
    'Jika pengajuan sudah selesai dan dokumen hasil telah diunggah oleh admin, kamu dapat membuka menu Pengajuan Saya untuk mengunduh hasil surat.',
    'Hasil Surat',
    1
),

(
    'jam_pelayanan',
    'Kapan jam pelayanan desa?',
    'jam buka,jam pelayanan,jam operasional,kantor buka',
    'Untuk informasi jam pelayanan, silakan hubungi petugas desa melalui kontak yang tercantum pada halaman informasi DesaMudah.',
    'Informasi',
    1
);
