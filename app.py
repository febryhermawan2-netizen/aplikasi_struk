import streamlit as st
import os
from google import genai
from PIL import Image
import json
import pandas as pd
import io

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Pemindai Struk", page_icon="🧾")

# 2. Setup Client AI
try:
    # Mengambil API Key dari Secrets Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("API Key tidak ditemukan di Secrets. Pastikan sudah diatur di Streamlit Cloud.")
    st.stop()

st.title("🧾 Aplikasi Pencatat Pengeluaran")

# 3. Kamera
foto_kamera = st.camera_input("Ambil Foto Struk")

if foto_kamera:
    st.info("Memproses gambar...")
    try:
        gambar = Image.open(foto_kamera)
        
        # Instruksi ke AI
        instruksi = """
        Analisa struk ini dan berikan output dalam format JSON saja:
        {
          "nama_toko": "nama",
          "tanggal": "tanggal",
          "daftar_barang": [{"nama": "item", "harga": 0}],
          "total_pembelanjaan": 0
        }
        """
        
        # Panggil Gemini
        respons = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=[instruksi, gambar]
        )
        
        # Bersihkan teks JSON
        teks = respons.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(teks)
        
        st.write(f"Toko: {data['nama_toko']}")
        
        # Tampilkan Tabel
        tabel = pd.DataFrame(data['daftar_barang'])
        st.dataframe(tabel)
        
        # Tombol Download
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            tabel.to_excel(writer, index=False)
        
        st.download_button("Download Excel", buffer.getvalue(), "struk.xlsx")
        
    except Exception as e:
        st.error(f"Error: {e}")
