import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import json

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Fraud Investigation Dashboard", layout="wide")

st.title("🛡️ Fraud Investigation Dashboard")

# 1. PERSIAPAN & CACHING DATA
# Caching memastikan data 1 juta baris hanya dimuat 1x ke memori
# @st.cache_data
# def load_data():
#     # Buat list kosong untuk menampung data yang sudah dibersihkan
#     cleaned_data = []
    
#     # Buka file secara native menggunakan Python (sangat aman untuk file besar/1jt baris)
#     with open('data/imei_mitra.json', 'r', encoding='utf-8') as f:
#         for line in f:
#             # Hapus spasi kosong/enter di ujung baris
#             line = line.strip()
            
#             # Abaikan baris jika kebetulan kosong
#             if not line:
#                 continue
                
#             # Cek jika baris diakhiri dengan tanda koma, maka buang komanya
#             if line.endswith(','):
#                 line = line[:-1]
                
#             # Parse json mandiri dan masukkan ke list
#             try:
#                 cleaned_data.append(json.loads(line))
#             except json.JSONDecodeError:
#                 # Lewati baris yang benar-benar rusak agar aplikasi tidak crash
#                 continue

#     # Ubah list dictionary tersebut menjadi Pandas DataFrame
#     df = pd.DataFrame(cleaned_data)
    
#     # Isi nilai NaN (kosong) dengan string kosong agar mudah diproses
#     df = df.fillna("")
    
#     return df

@st.cache_data
def load_data():
    # Membaca jutaan baris parquet hanya butuh waktu sekian detik!
    df = pd.read_parquet('data/imei_mitra_compressed.parquet')
    return df

with st.spinner("Memuat 1 Juta Baris Data..."):
    df = load_data()

st.success(f"Berhasil memuat {len(df):,} baris data!")

# Layout Grid untuk Chart
col1, col2 = st.columns(2)

# ==========================================
# CHART 1: BAR CHART (Top 10 IP Address)
# ==========================================
with col1:
    with st.container(border=True):
        st.subheader("10 IP Address Terbanyak")
        # Agregasi
        top_ip = df[df['ip'] != ''].groupby('ip').size().reset_index(name='Total Akun')
        top_ip = top_ip.sort_values(by='Total Akun', ascending=False).head(10)
        
        # Visualisasi
        fig_bar = px.bar(top_ip, x='ip', y='Total Akun', color='Total Akun', 
                         color_continuous_scale='Blues', text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# CHART 2: DONUT CHART (Pola Kekosongan)
# ==========================================
with col2:
    with st.container(border=True):
        st.subheader("Pola Kekosongan Data")
        # Agregasi menggunakan np.select untuk performa tinggi
        conditions = [
            (df['imei'] != '') & (df['ip'] != ''),
            (df['imei'] == '') & (df['ip'] != ''),
            (df['imei'] != '') & (df['ip'] == '')
        ]
        choices = ['Lengkap', 'Hanya IMEI Kosong', 'Hanya IP Kosong']
        df['Status'] = np.select(conditions, choices, default='Kosong Semua')
        status_counts = df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        
        # Visualisasi
        fig_donut = px.pie(status_counts, names='Status', values='Jumlah', hole=0.5,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_donut, use_container_width=True)

# ==========================================
# CHART 3: GEO LOCATION MAP
# ==========================================
with st.container(border=True):
    st.subheader("Pemetaan Sebaran IP (Geo Map)")
    st.markdown("Sebaran geografis berdasarkan IP yang aktif.")
    
    # Simulasi Konversi IP ke Koordinat (Dalam produksi, gunakan library maxminddb/GeoIP)
    # Streamlit mendeteksi kolom bernama 'latitude' dan 'longitude' secara otomatis
    map_data = top_ip.copy()
    # Mocking koordinat di sekitar Indonesia untuk keperluan demo
    map_data['latitude'] = np.random.uniform(-10, 5, size=len(map_data))
    map_data['longitude'] = np.random.uniform(95, 140, size=len(map_data))
    
    # Streamlit memiliki native map yang sangat ringan
    st.map(map_data, size='Total Akun', color='#0ea5e9')

# ==========================================
# CHART 4 & TABEL: Baris Ketiga (2 Kolom)
# ==========================================
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True, height=550):
        st.subheader("Distribusi Akun per IMEI")
        # Agregasi
        imei_counts = df[df['imei'] != ''].groupby('imei').size().reset_index(name='Jumlah Akun')
        
        # Visualisasi Histogram dengan skala Logaritmik agar outlier (penipuan) terlihat
        fig_hist = px.histogram(imei_counts, x='Jumlah Akun', nbins=50,
                                title="Frekuensi Jumlah Akun dalam 1 Perangkat (Log Scale)",
                                color_discrete_sequence=['#A855F7'],
                                log_y=True) # <-- Skala logaritmik ditambahkan di sini
        st.plotly_chart(fig_hist, use_container_width=True)
        
with col4:
    with st.container(border=True, height=550):
        st.subheader("Banyak Akun dalam 1 Perangkat")
        # Menampilkan bentuk asli dari data agregasi imei_counts (Top 5 Paling Mencurigakan)
        st.dataframe(imei_counts.sort_values('Jumlah Akun', ascending=False).head(50), use_container_width=True)

# ==========================================
# STEP 4: PROMPT BAR CUSTOM QUERY
# ==========================================
st.divider()
st.subheader("🤖 Prompt Bar: Filter & Custom Table")
st.markdown("Gunakan sintaks Pandas Query untuk memfilter data. Contoh: `username == '01443328'` atau `Status == 'Hanya IMEI Kosong'`")

# Input Chat/Prompt
prompt = st.chat_input("Ketik kondisi filter Anda di sini...")

if prompt:
    st.write(f"**Menjalankan Query:** `{prompt}`")
    try:
        # Eksekusi filter menggunakan Pandas Query Engine
        filtered_df = df.query(prompt)
        
        st.success(f"Ditemukan {len(filtered_df):,} data yang cocok!")
        st.dataframe(filtered_df.head(100), use_container_width=True) # Tampilkan 100 teratas agar tidak lag
        
    except Exception as e:
        st.error(f"Format prompt tidak valid. Error: {e}")