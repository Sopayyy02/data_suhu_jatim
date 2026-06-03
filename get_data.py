import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ======================================
# KONFIGURASI
# ======================================
FILE_DATA = "data/data_suhu_lama.xlsx"

daerah_list = {
    "Surabaya": "35.78.10.1001",
    "Malang": "35.73.05.1001",
    "Sidoarjo": "35.15.06.1001",
    "Kediri": "35.71.01.1001",
    "Pasuruan": "35.14.10.1001"
}

# ======================================
# LOAD DATA LAMA
# ======================================
path_file = Path(FILE_DATA)

if not path_file.exists():
    raise FileNotFoundError(
        f"File tidak ditemukan: {FILE_DATA}"
    )

df_lama = pd.read_excel(FILE_DATA)

df_lama.columns = df_lama.columns.str.strip().str.upper()

df_lama["TANGGAL"] = pd.to_datetime(df_lama["TANGGAL"])

tanggal_terakhir = df_lama["TANGGAL"].max().date()
hari_ini = datetime.now().date()

print(f"Tanggal terakhir data: {tanggal_terakhir}")
print(f"Hari ini: {hari_ini}")

# ======================================
# CEK APAKAH SUDAH UPDATE
# ======================================
if tanggal_terakhir >= hari_ini:
    print("Data sudah paling baru. Tidak ada update.")
    exit()

# ======================================
# GENERATE RANGE TANGGAL
# ======================================
tanggal_update = []

current = tanggal_terakhir + timedelta(days=1)

while current <= hari_ini:
    tanggal_update.append(current)
    current += timedelta(days=1)

print(f"Akan update {len(tanggal_update)} hari")

hasil_baru = []

# ======================================
# AMBIL DATA BMKG
# ======================================
for tanggal in tanggal_update:

    print(f"\nUpdate tanggal {tanggal}")

    for nama_daerah, kode in daerah_list.items():

        print(f"Mengambil data {nama_daerah}...")

        url = (
            f"https://api.bmkg.go.id/"
            f"publik/prakiraan-cuaca?adm4={kode}"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            cuaca = data["data"][0]["cuaca"][0]

            suhu_list = []

            for item in cuaca:
                suhu = item.get("t")

                if suhu is not None:
                    suhu_list.append(float(suhu))

            if len(suhu_list) == 0:
                print(f"Tidak ada data suhu {nama_daerah}")
                continue

            tn = min(suhu_list)
            tx = max(suhu_list)
            tavg = sum(suhu_list) / len(suhu_list)

            hasil_baru.append({
    "TANGGAL": pd.Timestamp(tanggal),
    "DAERAH": nama_daerah,
    "TN": round(tn, 2),
    "TX": round(tx, 2),
    "TAVG": round(tavg, 2)
})

        except Exception as e:
            print(f"Gagal {nama_daerah}")
            print(e)

# ======================================
# GABUNG DATA
# ======================================
df_baru = pd.DataFrame(hasil_baru)

if df_baru.empty:
    print("Tidak ada data baru.")
    exit()

df_gabungan = pd.concat(
    [df_lama, df_baru],
    ignore_index=True
)

# Hapus duplicate
df_gabungan = df_gabungan.drop_duplicates(
    subset=["TANGGAL", "DAERAH"],
    keep="last"
)

df_gabungan = df_gabungan.sort_values(
    ["TANGGAL", "DAERAH"]
)

# ======================================
# OVERWRITE FILE LAMA
# ======================================
df_gabungan.to_excel(
    FILE_DATA,
    index=False
)

print("\nUpdate selesai!")
print(f"Jumlah data sekarang: {len(df_gabungan)}")

# ======================================
# BERSIHKAN MEMORY
# ======================================
del df_lama
del df_baru
del df_gabungan
del hasil_baru

print("Memory dibersihkan.")