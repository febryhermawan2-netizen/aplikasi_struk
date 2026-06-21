import streamlit as st
from google import genai
from PIL import Image
import json
import pandas as pd
import io
import re # Tambahan pustaka untuk mencari teks secara paksa

# Konfigurasi Halaman
st.set_page_config(page_title="Pemindai Struk", page_icon="🧾")

# Setup Client AI
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("API Key tidak ditemukan. Pastikan sudah diatur di Secrets Streamlit.")
    st.stop()

st.title("🧾 Aplikasi Pencatat Pengeluaran")

# Kamera
foto_kamera = st.camera_input("Ambil Foto Struk")

if foto_kamera:
    st.info("Memproses gambar... Mohon tunggu.")
    try:
        gambar = Image.open(foto_kamera)
        
        # Panggil Gemini 
        respons = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents=[
                "Analisa struk ini dan berikan output WAJIB dalam format JSON saja tanpa teks lain: {\"nama_toko\": \"nama\", \"tanggal\": \"tanggal\", \"daftar_barang\": [{\"nama\": \"item\", \"harga\": 0}], \"total_pembelanjaan\": 0}",
                gambar
            ]
        )
        
        # TEKNIK BARU: Mencari paksa pola JSON di dalam teks balasan AI
        teks_ai = respons.text
        pola_json = re.search(r'\{.*\}', teks_ai, re.DOTALL)
        
        if pola_json:
            teks_bersih = pola_json.group(0)
            data = json.loads(teks_bersih)
            
            st.success("Berhasil dianalisa!")
            st.write(f"**Toko:** {data.get('nama_toko', 'Tidak terbaca')}")
            
            # Tabel
            if 'daftar_barang' in data and len(data['daftar_barang']) > 0:
                tabel = pd.DataFrame(data['daftar_barang'])
                st.dataframe(tabel, use_container_width=True)
                
                # Download Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    tabel.to_excel(writer, index=False)
                
                st.download_button("📥 Download Excel", buffer.getvalue(), "struk.xlsx")
            else:
                st.warning("Daftar barang tidak ditemukan di struk ini.")
                
        else:
            st.error("AI tidak mengembalikan format data yang bisa dibaca. Silakan foto ulang.")
            with st.expander("Lihat balasan mentah AI"):
                st.write(teks_ai)
                
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
