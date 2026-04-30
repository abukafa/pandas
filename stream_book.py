import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

code = st.text_area("Tulis kode Python di sini:")
if st.button("Jalankan"):
    try:
        exec(code)
    except Exception as e:
        st.error(f"Error: {e}")
