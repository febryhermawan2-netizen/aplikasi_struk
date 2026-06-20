import streamlit as st
from google import genai
from PIL import Image
import json
import pandas as pd
import io

# PENTING: Masukkan API Key Anda di bawah ini
client = genai.Client(api_key="AQ.Ab8RN6Lg4Fod0EyrERmd70Jx-GwZbFceQIVzuTIeM7h0S6SytA")

# Mengatur judul dan ikon halaman web
st.set_page_config(page_title="Pemindai Struk Keuangan", page_icon="🧾")

st.title("🧾 Aplikasi Pencatat Pengeluaran")
st.write("Foto struk belanja Anda, biarkan AI yang mencatatnya ke Excel!")

# Membuat tombol kamera langsung di layar
foto_kamera = st.camera_input("Ambil Foto Struk")

# Logika ketika pengguna selesai mengambil foto
if foto_kamera is not None:
    st.success("Foto berhasil diambil! AI sedang memproses data... Mohon tunggu sebentar.")
    
    try:
        # 1. Membaca foto dari memori
        gambar = Image.open(foto_kamera)
        
        # 2. Mengirim instruksi ke Gemini
        instruksi = """
        Tolong analisa foto struk belanja ini. 
        Ekstrak informasi berikut dan tampilkan murni dalam format JSON yang rapi tanpa tambahan teks apapun:
        {
          "nama_toko": "",
          "tanggal": "",
          "daftar_barang": [{"nama": "", "harga": 0}],
          "total_pembelanjaan": 0
        }
        """
        respons = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[instruksi, gambar]
        )
        
        # 3. Membersihkan teks menjadi format JSON
        teks_bersih = respons.text.strip()
        if teks_bersih.startswith("```json"): 
            teks_bersih = teks_bersih[7:]
        if teks_bersih.endswith("```"): 
            teks_bersih = teks_bersih[:-3]
        
        data_struk = json.loads(teks_bersih)
        
        # 4. Menampilkan hasil teks ke layar aplikasi
        st.write("### Hasil Analisis AI:")
        st.write(f"**Toko:** {data_struk['nama_toko']} | **Tanggal:** {data_struk['tanggal']}")
        
        baris_excel = []
        for barang in data_struk["daftar_barang"]:
            baris_excel.append({
                "Tanggal": data_struk["tanggal"],
                "Toko": data_struk["nama_toko"],
                "Nama Barang": barang["nama"],
                "Harga Satuan": barang["harga"]
            })
        
        # 5. Mengubah data menjadi tabel visual
        tabel = pd.DataFrame(baris_excel)
        st.dataframe(tabel, use_container_width=True)
        
        # 6. Menyiapkan tombol unduh file Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            tabel.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Download File Excel",
            data=buffer.getvalue(),
            file_name="Laporan_Pengeluaran_Otomatis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        st.error(f"Waduh, terjadi sedikit kesalahan saat membaca gambar: {e}")