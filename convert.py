import pandas as pd
import json

print("Membaca dan membersihkan JSON...")
cleaned_data = []
with open('data/imei_mitra.json', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line: continue
        if line.endswith(','): line = line[:-1]
        try:
            cleaned_data.append(json.loads(line))
        except:
            continue

df = pd.DataFrame(cleaned_data)
df = df.fillna("")

print("Menyimpan ke format Parquet...")
# Anda mungkin perlu menginstal pyarrow: pip install pyarrow
df.to_parquet('imei_mitra_compressed.parquet', engine='pyarrow')
print("Selesai! Cek ukuran file imei_mitra_compressed.parquet Anda.")