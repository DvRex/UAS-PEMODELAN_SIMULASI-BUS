# 🚌 Simulasi Antrian Halte Bus (Monte Carlo Method)

**Final Project UAS - Mata Kuliah Pemodelan & Simulasi**

Halo! 👋 Repo ini berisi *source code* lengkap untuk aplikasi dashboard simulasi antrian bus. Aplikasi ini dibuat menggunakan pendekatan **Monte Carlo** untuk memprediksi kinerja sistem transportasi (waktu tunggu, panjang antrian, dan utilitas bus) dalam menghadapi ketidakpastian kedatangan penumpang.

Yang bikin beda? Project ini udah diintegrasikan dengan **AI (Llama 3 via Groq)** untuk ngasih rekomendasi solusi teknis secara otomatis! 🤖✨

---

## 🌐 Live Demo
Coba Simulasi langsung melalui browser tanpa perlu instalasi:

### 👉 [Klik Disini untuk Membuka Website        (Streamlit)](https://simulasi-antrian-bus-monte-carlo.streamlit.app/)

---

## 🚀 Fitur Unggulan
1.  **Simulasi Monte Carlo:** Memprediksi ketidakpastian kedatangan penumpang (menggunakan Distribusi Poisson).
2.  **Dashboard Interaktif:** User bisa atur parameter (Interval Bus, Kapasitas, Rata-rata Penumpang) secara *real-time*.
3.  **Visualisasi Data:** Grafik dinamis *Confidence Interval* menggunakan library **Plotly**.
4.  **AI Consultant:** Fitur analisis cerdas yang terhubung ke Groq API untuk memberikan "Second Opinion" dan solusi konkret.
5.  **Smart Logic System:** Analisis otomatis berbasis aturan (*Rule-Based*) untuk mendiagnosa status sistem (Aman/Waspada/Kritis).

## 🛠️ Tech Stack
Project ini dibangun menggunakan teknologi Python modern:
* **Python** 🐍 (Core Logic)
* **Streamlit** 🎈 (Framework Dashboard Web)
* **Plotly** 📊 (Visualisasi Grafik Interaktif)
* **Groq API** 🧠 (AI Engine menggunakan model Llama-3-8b)
* **NumPy & Pandas** 🐼 (Komputasi Statistik & Dataframe)

## 💻 Cara Run di Laptop (Localhost)

Mau coba jalanin atau modifikasi project ini? Gas ikuti langkah ini:

1.  **Clone Repo ini**
    ```bash
    git clone https://github.com/DvRex/UAS-PEMODELAN_SIMULASI-BUS.git
    cd UAS-PEMODELAN_SIMULASI-BUS
    ```

2.  **Install Library**
    Pastikan Python sudah terinstall, lalu jalankan:
    ```bash
    pip install -r requirements.txt
    atau jika error bisa coba gunakan
    py -m pip install -r requirements.txt > Pastikan Step 1 Dan CD ke Folder sudah dilakukan
    ```
    
3.  **Setup .streamlit**
    Agar Streamlit bisa dijalankan silahkan
    * Buat folder baru bernama `.streamlit` di dalam folder project.
    * Di dalamnya, buat file bernama `secrets.toml`. > **Step selanjutnya bisa diskip jika ingin input API Manual atau Tidak menggunakan AI**
    * Isi file tersebut dengan:
        ```toml
        GROQ_API_KEY = "masukkan_api_key_groq_disini"
        ```
    ***Pastikan File secrets.toml ada di dalam folder .streamlit walaupun kosong!!!** 

    Jika Ingin Setiap Run streamlit localhost dan Fungsi AI Berfungsi Silahkan Isi API dari groq dengan contoh seperti di atas.      
    Untuk Mendapatan API Groq Bisa Melalui console.groq.com

5.  **Jalankan Aplikasi**
    ```bash
    streamlit run app.py 
    atau
    py -m streamlit run app.py
    ```

## 📂 Struktur File
* `app.py` → File utama (Main Program), berisi logika Monte Carlo, UI Streamlit, dan Integrasi AI.
* `requirements.txt` → Daftar pustaka (library) yang wajib diinstall.
* `.gitignore` → Konfigurasi agar file sampah/rahasia tidak ikut ter-upload.

---
**Mata Kuliah : Pemodelan Dan Simulasi**

**Institut Teknologi Dan Bisnis Nobel Indonesia**

*Jika project ini bermanfaat, jangan lupa kasih Star ⭐ ya!*
