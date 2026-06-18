# Laporan Tugas Akhir
## Implementasi Histogram Matching pada Citra Struk dan Tiket Menggunakan Aplikasi Berbasis Web

**Mata Kuliah** : Pengolahan dan Analisis Citra Digital  
**Nama** : Danish Rahadian  
**Program Studi** : Teknik Informatika  
**Tanggal Pengerjaan** : 17 Juni 2026

---

## 1. Pendahuluan

Pengolahan citra digital merupakan salah satu cabang ilmu komputer yang berfokus pada manipulasi dan analisis citra secara komputasional. Salah satu permasalahan yang sering muncul dalam pengolahan citra adalah inkonsistensi kualitas visual antarcitra dalam satu dataset. Inkonsistensi ini dapat berupa perbedaan kecerahan, kontras, maupun distribusi warna, yang umumnya disebabkan oleh perbedaan kondisi pencahayaan, jenis kamera, atau pengaturan eksposur pada saat pengambilan gambar.

Pada tugas akhir mata kuliah ini, penulis mengimplementasikan teknik Histogram Matching sebagai pendekatan untuk menormalisasi distribusi intensitas piksel pada citra struk dan tiket. Histogram Matching dipilih karena merupakan teknik yang secara langsung beroperasi pada distribusi statistik intensitas citra, sehingga cocok digunakan untuk menyeragamkan tampilan visual sekumpulan citra dari sumber yang berbeda-beda.

Hasil implementasi dikemas dalam bentuk aplikasi web interaktif menggunakan Streamlit agar dapat digunakan secara langsung oleh pengguna tanpa memerlukan pengetahuan pemrograman.

---

## 2. Landasan Teori

### 2.1 Histogram Citra

Histogram citra adalah representasi grafis dari distribusi intensitas piksel dalam sebuah citra. Pada citra grayscale, histogram menggambarkan jumlah piksel pada setiap nilai intensitas dari 0 (hitam) hingga 255 (putih). Pada citra berwarna (RGB), histogram dihitung secara terpisah untuk masing-masing kanal warna Red (R), Green (G), dan Blue (B).

Histogram memberikan informasi tentang karakteristik tonal suatu citra. Citra yang terlalu gelap akan memiliki histogram yang terpusat di nilai intensitas rendah, sementara citra yang terlalu terang akan memiliki histogram yang terpusat di nilai intensitas tinggi.

### 2.2 Histogram Matching

Histogram Matching (atau Histogram Specification) adalah teknik pengolahan citra yang bertujuan mengubah distribusi intensitas suatu citra sumber agar mengikuti distribusi intensitas citra referensi. Proses ini berbeda dari Histogram Equalization yang hanya meratakan distribusi menuju distribusi uniform. Histogram Matching memungkinkan pengguna menentukan secara eksplisit distribusi tujuan berdasarkan citra referensi tertentu.

Secara matematis, proses Histogram Matching dilakukan melalui dua tahap:

**Tahap 1: Komputasi Cumulative Distribution Function (CDF)**

Untuk citra sumber dan citra referensi, dihitung terlebih dahulu fungsi distribusi kumulatif masing-masing:

```
CDF_src(v) = jumlah piksel dengan intensitas <= v / total piksel
CDF_ref(v) = jumlah piksel dengan intensitas <= v / total piksel
```

**Tahap 2: Pemetaan Intensitas**

Untuk setiap nilai intensitas `v` pada citra sumber, dicari nilai intensitas `v'` pada citra referensi sedemikian sehingga:

```
CDF_ref(v') >= CDF_src(v)
```

Nilai `v'` inilah yang digunakan sebagai nilai baru piksel tersebut pada citra hasil. Proses ini diterapkan secara terpisah pada setiap kanal warna (R, G, B) untuk mempertahankan informasi warna.

### 2.3 Implementasi dengan scikit-image

Fungsi `skimage.exposure.match_histograms` mengimplementasikan proses di atas secara efisien menggunakan pemetaan CDF invers. Parameter `channel_axis=-1` menginstruksikan fungsi untuk memproses setiap kanal warna secara independen, sehingga distribusi warna dari citra referensi dapat ditransfer secara akurat ke citra sumber.

---

## 3. Dataset

Dataset yang digunakan adalah kumpulan citra struk dan tiket dalam format JPEG dengan karakteristik sebagai berikut:

| Subset | Jumlah Citra |
|--------|-------------|
| Train  | 626 citra   |
| Test   | 347 citra   |
| **Total** | **973 citra** |

Berdasarkan pengamatan terhadap sampel citra, sebagian besar citra dalam dataset memiliki latar belakang putih (kertas struk) dengan teks berwarna hitam atau abu-abu. Rentang resolusi citra bervariasi antara 439 hingga 992 piksel untuk lebar, dan 605 hingga 2333 piksel untuk tinggi. Rata-rata kecerahan piksel pada sampel 50 citra dari subset train adalah **237.14** dari skala 0 sampai 255, mengindikasikan bahwa citra-citra dalam dataset umumnya cerah dan memiliki banyak area putih.

---

## 4. Dataset Validasi

Untuk keperluan pengujian fungsional aplikasi, dibuat dataset validasi sebanyak 20 citra yang dimodifikasi secara programatik dari subset test. Modifikasi dilakukan menggunakan delapan jenis degradasi untuk mensimulasikan kondisi citra yang buruk di dunia nyata.

### 4.1 Jenis Degradasi

| Jenis Degradasi | Jumlah Citra | Metode | Rata-rata Kecerahan |
|----------------|-------------|--------|---------------------|
| dark | 4 | Kecerahan dikalikan 0.35 | 76.2 |
| very_dark | 3 | Kecerahan dikalikan 0.18 | 41.2 |
| overexposed | 2 | Kecerahan dikalikan 1.55 lalu di-clip 255 | 239.6 |
| low_contrast | 3 | Piksel dikompres ke rentang [100, 214] | 205.3 |
| warm_tint | 2 | Gelap + kanal R diperkuat 1.35, kanal B dilemahkan 0.65 | 84.4 |
| cool_tint | 2 | Gelap + kanal B diperkuat 1.35, kanal R dilemahkan 0.65 | 81.5 |
| noisy_dark | 2 | Gelap + noise Gaussian (mu=0, sigma=12) | 72.3 |
| faded | 2 | Piksel dikompres ke rentang [90, 214] (memudar) | 221.0 |

### 4.2 Alasan Pemilihan Degradasi

Kedelapan jenis degradasi tersebut dipilih karena merepresentasikan kondisi nyata yang sering terjadi pada pengambilan foto struk, yaitu:

- Pencahayaan kurang (dark, very_dark, noisy_dark) mensimulasikan pemotretan di tempat gelap atau menggunakan kamera ponsel dengan kualitas rendah.
- Overexposed mensimulasikan penggunaan flash yang terlalu kuat atau pencahayaan dari belakang.
- Low contrast mensimulasikan struk yang dicetak dengan tinta kurang pekat.
- Warm tint dan cool tint mensimulasikan pengaruh cahaya lampu pijar atau lampu neon terhadap warna citra.
- Faded mensimulasikan struk lama yang warnanya memudar.

Dataset validasi dibuat menggunakan skrip `make_validation.py` dengan seed acak yang tetap (seed=42), sehingga hasilnya bersifat deterministik dan dapat direproduksi kapan saja.

---

## 5. Perancangan dan Implementasi Sistem

### 5.1 Arsitektur Sistem

Sistem dibangun dalam satu file utama `app.py` dengan arsitektur yang memisahkan lapisan logika dan lapisan antarmuka. Fungsi-fungsi pengolahan citra berdiri sendiri dan tidak bergantung pada Streamlit, sehingga dapat diuji secara terpisah.

```
uas/
├── app.py               # Aplikasi Streamlit utama
├── make_validation.py   # Skrip pembuatan dataset validasi
├── report_stats.py      # Skrip analisis statistik
├── requirements.txt     # Dependensi Python
├── README.md            # Dokumentasi penggunaan
├── LAPORAN.md           # Laporan ini
├── outputs/             # Citra hasil disimpan di sini
├── validation/          # 20 citra validasi terdegradasi
├── train/               # 626 citra dataset train
└── test/                # 347 citra dataset test
```

### 5.2 Alur Pemrosesan

Alur pemrosesan utama pada aplikasi adalah sebagai berikut:

1. Pengguna mengunggah citra atau memilih citra dari tab validasi.
2. Citra sumber dibaca menggunakan Pillow dan dikonversi ke mode RGB.
3. Jika opsi resize diaktifkan, citra yang lebarnya melebihi 1600 piksel akan diperkecil secara proporsional menggunakan metode Lanczos.
4. Citra referensi dibaca dari folder dataset sesuai pilihan pengguna.
5. Fungsi `match_histograms` dari scikit-image diterapkan dengan parameter `channel_axis=-1`.
6. Citra hasil disimpan ke folder `outputs/` dengan nama yang menyertakan timestamp.
7. Tiga citra (sumber, referensi, hasil) ditampilkan berdampingan di antarmuka.
8. Pengguna dapat mengunduh citra hasil melalui tombol download.

### 5.3 Komponen Antarmuka

Antarmuka aplikasi terdiri dari:

- **Sidebar kiri**: Pengaturan mode referensi (default atau pilih manual dari dataset), opsi resize, dan opsi tampilkan histogram.
- **Tab "Upload Image"**: Pengguna mengunggah citra dari perangkat lokal.
- **Tab "Use Validation Image"**: Pengguna memilih citra dari dataset validasi yang telah terdegradasi, disertai penjelasan jenis degradasi.
- **Area utama**: Menampilkan tiga kolom (Original, Reference, Result) dan histogram perbandingan jika diaktifkan.
- **Tombol download**: Tersedia di bawah tampilan hasil.

### 5.4 Visualisasi Histogram

Aplikasi menampilkan visualisasi histogram dalam grid 3x3: tiga baris untuk Original, Reference, dan Result, serta tiga kolom untuk kanal R, G, dan B. Visualisasi ini dibuat menggunakan Matplotlib dengan backend non-interaktif (Agg) agar kompatibel dengan lingkungan server Streamlit.

---

## 6. Hasil Pengujian

### 6.1 Pengujian Fungsional

Pengujian fungsional dilakukan dengan menjalankan proses Histogram Matching terhadap seluruh 20 citra validasi menggunakan satu citra referensi dari subset train (`X00016469612.jpg`, rata-rata kecerahan = 244.76).

Hasil lengkap pengujian ditampilkan pada tabel berikut:

| Nama File | Jenis Degradasi | Kecerahan Awal | Kecerahan Hasil | Selisih Sebelum | Selisih Sesudah |
|-----------|----------------|----------------|-----------------|-----------------|-----------------|
| X51005301666_dark.jpg | dark | 66.5 | 244.6 | 178.3 | 0.12 |
| X51005361906_noisy_dark.jpg | noisy_dark | 73.8 | 244.4 | 171.0 | 0.33 |
| X51005361908_noisy_dark.jpg | noisy_dark | 70.8 | 244.3 | 173.9 | 0.42 |
| X51005568889_warm_tint.jpg | warm_tint | 80.6 | 244.3 | 164.2 | 0.46 |
| X51005568894_faded.jpg | faded | 222.3 | 244.2 | 22.5 | 0.58 |
| X51005605287_low_contrast.jpg | low_contrast | 208.0 | 244.5 | 36.8 | 0.23 |
| X51005663300_dark.jpg | dark | 86.7 | 244.5 | 158.0 | 0.25 |
| X51005677327_low_contrast.jpg | low_contrast | 208.4 | 244.2 | 36.4 | 0.51 |
| X51005746203_faded.jpg | faded | 219.7 | 244.5 | 25.1 | 0.29 |
| X51005746207_overexposed.jpg | overexposed | 238.1 | 246.2 | 6.7 | 1.39 |
| X51005757292_very_dark.jpg | very_dark | 35.1 | 245.1 | 209.6 | 0.30 |
| X51005764031_overexposed.jpg | overexposed | 241.1 | 246.0 | 3.6 | 1.25 |
| X51006008105_dark.jpg | dark | 63.4 | 245.2 | 181.4 | 0.40 |
| X51006556851_cool_tint.jpg | cool_tint | 81.7 | 244.0 | 163.1 | 0.71 |
| X51006828199_very_dark.jpg | very_dark | 44.0 | 244.9 | 200.7 | 0.17 |
| X51007231274_warm_tint.jpg | warm_tint | 88.3 | 250.1 | 156.5 | 5.38 |
| X51007391390_cool_tint.jpg | cool_tint | 81.3 | 244.1 | 163.5 | 0.64 |
| X51007846268_very_dark.jpg | very_dark | 44.6 | 250.7 | 200.2 | 5.99 |
| X51007846396_dark.jpg | dark | 88.2 | 250.5 | 156.5 | 5.69 |
| X51009568881_low_contrast.jpg | low_contrast | 199.7 | 244.1 | 45.1 | 0.64 |

Keterangan kolom:
- **Kecerahan Awal**: Rata-rata nilai piksel citra terdegradasi (skala 0-255)
- **Kecerahan Hasil**: Rata-rata nilai piksel setelah Histogram Matching
- **Selisih Sebelum**: Selisih absolut antara kecerahan citra sumber dan referensi
- **Selisih Sesudah**: Selisih absolut antara kecerahan hasil dan referensi

### 6.2 Analisis Hasil

Dari tabel di atas dapat diobservasi beberapa hal:

**Efektivitas normalisasi kecerahan.** Rata-rata selisih kecerahan sebelum proses matching adalah 122.65 satuan, sedangkan setelah proses matching turun menjadi 1.29 satuan. Ini menunjukkan reduksi deviasi sebesar **99.0%**, yang mengindikasikan bahwa algoritma bekerja sangat efektif dalam menyelaraskan distribusi kecerahan antarcitra.

**Konsistensi pada berbagai jenis degradasi.** Algoritma berhasil menangani degradasi yang sangat beragam, mulai dari citra sangat gelap (very_dark, rata-rata 41.2) hingga citra yang terlampau terang (overexposed, rata-rata 239.6), serta citra dengan pergeseran warna (warm_tint, cool_tint). Semua jenis degradasi berhasil dinormalisasi mendekati distribusi referensi.

**Variasi kecil pada beberapa citra.** Terdapat tiga citra yang menunjukkan selisih sesudah lebih tinggi dari rata-rata (X51007231274_warm_tint: 5.38, X51007846268_very_dark: 5.99, X51007846396_dark: 5.69). Hal ini kemungkinan disebabkan oleh perbedaan konten visual antara citra tersebut dan citra referensi. Karena Histogram Matching beroperasi pada distribusi statistik keseluruhan, konten visual yang sangat berbeda dari referensi dapat menghasilkan pemetaan yang sedikit tidak sempurna meskipun distribusi secara global sudah mendekati.

**Overexposed hampir tidak berubah.** Citra dengan jenis degradasi overexposed memiliki kecerahan awal yang sudah mendekati referensi (238.1 dan 241.1 berbanding 244.76), sehingga selisih perubahan kecil. Ini adalah perilaku yang wajar karena Histogram Matching tidak akan mengubah distribusi yang sudah serupa.

---

## 7. Dependensi dan Cara Menjalankan

### 7.1 Dependensi

| Library | Versi Minimum | Fungsi |
|---------|--------------|--------|
| streamlit | 1.35.0 | Framework antarmuka web |
| pillow | 10.0.0 | Pembacaan dan konversi format citra |
| numpy | 1.24.0 | Operasi array dan manipulasi piksel |
| scikit-image | 0.21.0 | Implementasi Histogram Matching |
| matplotlib | 3.7.0 | Visualisasi histogram |

### 7.2 Cara Menjalankan

```bash
pip install -r requirements.txt
python make_validation.py
streamlit run app.py
```

Aplikasi dapat diakses di browser pada alamat `http://localhost:8501`.

---

## 8. Keterbatasan

Histogram Matching adalah teknik yang beroperasi pada level statistik distribusi intensitas, bukan pada level konten semantik citra. Oleh karena itu, terdapat beberapa keterbatasan yang perlu dicatat:

1. **Tidak dapat memperbaiki blur.** Jika citra sumber mengalami motion blur atau out-of-focus, Histogram Matching tidak akan mengembalikan ketajaman detail tersebut karena blur adalah masalah spasial, bukan masalah distribusi intensitas.

2. **Tidak dapat memulihkan detail teks yang hilang.** Jika teks pada struk sudah tidak terbaca karena cetakan pudar atau kerusakan fisik, Histogram Matching tidak akan merekonstruksi informasi tersebut.

3. **Bergantung pada kualitas citra referensi.** Apabila citra referensi memiliki kualitas yang buruk atau distribusi intensitas yang tidak representatif, maka citra hasil akan mewarisi karakteristik tersebut.

4. **Potensi artefak warna.** Pada kasus di mana konten visual citra sumber dan referensi sangat berbeda (misalnya, dominasi warna berbeda), hasil matching dapat menampilkan pergeseran warna yang tidak alami.

5. **Tidak invariant terhadap konten.** Algoritma tidak memahami isi citra. Dua citra struk yang keduanya bersih tetapi dari jenis printer berbeda dapat menghasilkan matching yang secara statistik tepat namun secara visual kurang sesuai.

---

## 9. Kesimpulan

Pada tugas akhir ini telah berhasil diimplementasikan teknik Histogram Matching untuk normalisasi citra struk dan tiket dalam bentuk aplikasi web interaktif. Implementasi menggunakan fungsi `match_histograms` dari pustaka scikit-image yang bekerja secara per-kanal warna (R, G, B).

Pengujian terhadap 20 citra validasi dengan delapan jenis degradasi menunjukkan bahwa algoritma mampu mengurangi deviasi kecerahan rata-rata dari 122.65 menjadi 1.29, atau setara dengan reduksi sebesar 99.0%. Hasil ini membuktikan bahwa Histogram Matching efektif sebagai tahap pra-pemrosesan untuk menyeragamkan distribusi visual citra dalam dataset yang dikumpulkan dari berbagai kondisi pengambilan gambar.

Keterbatasan utama metode ini terletak pada sifatnya yang beroperasi di domain statistik intensitas tanpa mempertimbangkan konten spasial citra, sehingga tidak dapat mengatasi masalah seperti blur, noise frekuensi tinggi, atau kerusakan struktural pada citra.

---

*Laporan ini disusun sebagai bagian dari tugas akhir mata kuliah Pengolahan dan Analisis Citra Digital.*
