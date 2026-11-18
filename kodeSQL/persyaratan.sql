INSERT INTO persyaratan
(layanan_id, nama_persyaratan, keterangan)
VALUES

-- 1. Surat Keterangan Domisili
(1, 'Fotokopi KTP', 'Identitas pemohon.'),
(1, 'Fotokopi Kartu Keluarga', 'Kartu Keluarga pemohon.'),
(1, 'Surat Pengantar RT/RW', 'Surat pengantar dari lingkungan tempat tinggal.'),

-- 2. Surat Keterangan Usaha
(2, 'Fotokopi KTP', 'Identitas pemohon.'),
(2, 'Fotokopi Kartu Keluarga', 'Kartu Keluarga pemohon.'),
(2, 'Surat Pengantar RT/RW', 'Surat pengantar dari lingkungan tempat usaha.'),
(2, 'Keterangan Usaha', 'Informasi nama, jenis, dan lokasi usaha.'),

-- 3. Surat Pengantar Nikah
(3, 'Fotokopi KTP Calon Pengantin', 'Identitas calon pengantin.'),
(3, 'Fotokopi Kartu Keluarga', 'Kartu Keluarga calon pengantin.'),
(3, 'Surat Pengantar RT/RW', 'Surat pengantar dari lingkungan tempat tinggal.'),
(3, 'Dokumen Pendukung Pernikahan', 'Dokumen pendukung sesuai kebutuhan simulasi.'),

-- 4. Pengantar Perubahan Kartu Keluarga
(4, 'Fotokopi Kartu Keluarga', 'KK yang akan diperbarui.'),
(4, 'Fotokopi KTP', 'Identitas pemohon.'),
(4, 'Dokumen Pendukung Perubahan Data', 'Dokumen sesuai jenis perubahan data.'),

-- 5. Pengantar Pindah Domisili
(5, 'Fotokopi KTP', 'Identitas pemohon.'),
(5, 'Fotokopi Kartu Keluarga', 'Kartu Keluarga pemohon.'),
(5, 'Alamat Tujuan', 'Informasi alamat tempat tinggal tujuan.'),
(5, 'Surat Pengantar RT/RW', 'Surat pengantar dari lingkungan tempat tinggal.'),

-- 6. Surat Keterangan Tidak Mampu
(6, 'Fotokopi KTP', 'Identitas pemohon.'),
(6, 'Fotokopi Kartu Keluarga', 'Kartu Keluarga pemohon.'),
(6, 'Surat Pengantar RT/RW', 'Surat pengantar dari lingkungan tempat tinggal.');
