import requests
import pandas as pd
from datetime import datetime

# Daftar stasiun
daerah_list = {
    "Surabaya": "35.78.10.1001",
    "Malang": "35.73.05.1001",
    "Sidoarjo": "35.15.06.1001",
    "Kediri": "35.71.01.1001",
    "Pasuruan": "35.14.10.1001"
}

hasil = []

for nama_daerah, kode in daerah_list.items():

    print(f"Mengambil data {nama_daerah}...")

    url = f"https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4={kode}"

    try:
        response = requests.get(url)
        data = response.json()

        cuaca = data['data'][0]['cuaca'][0]

        suhu_list = []

        for item in cuaca:
            suhu_list.append(item["t"])

        tn = min(suhu_list)
        tx = max(suhu_list)
        tavg = sum(suhu_list) / len(suhu_list)

        hasil.append({
            "Tanggal": datetime.now().strftime("%Y-%m-%d"),
            "Nama Stasiun": nama_daerah,
            "TN": tn,
            "TX": tx,
            "TAVG": round(tavg, 2)
        })

    except Exception as e:
        print(f"Gagal {nama_daerah}")
        print(e)

# DataFrame
df = pd.DataFrame(hasil)

# Simpan CSV
df.to_csv("../data/suhu_jatim_baru.csv", index=False)

print(df)
print("Data berhasil disimpan!")