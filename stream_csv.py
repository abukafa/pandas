import streamlit as st
import pandas as pd
import glob
import matplotlib.pyplot as plt

st.title("Log Investigation Dashboard")

# load banyak csv
files = glob.glob("data/*.csv")
df = pd.concat([pd.read_csv(f) for f in files])

# normalisasi
# df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# hitung IP vs jumlah akun
ip_user = df.groupby('IP')['Name'].nunique().sort_values(ascending=False)

# tampil tabel
st.subheader("Top IP")
top_n = st.slider("Top N IP", 5, 50, 10)
st.dataframe(ip_user.head(top_n))

# pilih IP
selected_ip = st.selectbox("Pilih IP", ip_user.index)

# tampil akun dari IP
st.subheader("Akun dari IP terpilih")
st.write(df[df['IP'] == selected_ip]['Name'].unique())

# bar chart
st.subheader("Bar Chart")
data = ip_user.head(top_n)

fig, ax = plt.subplots()
data.plot(kind='bar', ax=ax)
plt.xticks(rotation=45)

st.pyplot(fig)

import altair as alt

data = ip_user.head(top_n).reset_index()
data.columns = ['IP', 'Jumlah']

chart = alt.Chart(data).mark_bar().encode(
    x='IP',
    y='Jumlah',
    tooltip=['IP', 'Jumlah']
)

st.altair_chart(chart, use_container_width=True)