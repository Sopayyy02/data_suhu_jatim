import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# ======================================
# KONFIGURASI
# ======================================
FILE_DATA = "data/data_suhu_lama.xlsx"

daerah_list = {
    "SURABAYA": "35.78.15.1003",
    "MALANG": "35.07.12.2007",
    "SIDOARJO": "35.15.17.2014",
    "KEDIRI": "35.06.13.2002",
    "PASURUAN": "35.14.11.2001"
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
df_lama["DAERAH"] = (
    df_lama["DAERAH"]
    .astype(str)
    .str.strip()
    .str.upper()
)
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
        print(url)

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # ambil semua slot prakiraan
            semua_slot = []

            for grup in data["data"][0]["cuaca"]:
                semua_slot.extend(grup)

            suhu_list = []
            rh_list = []
            ff_list = []
            wd_deg_list = []
            wd_list = []
            rr_list = []

            for item in semua_slot:

                suhu = item.get("t")
                hu = item.get("hu")
                ws = item.get("ws")
                wd_deg = item.get("wd_deg")
                wd = item.get("wd")
                rr = item.get("tp")

                if suhu is not None:
                    suhu_list.append(float(suhu))

                if hu is not None:
                    rh_list.append(float(hu))

                if ws is not None:
                    ff_list.append(float(ws))

                if wd_deg is not None:
                    wd_deg_list.append(float(wd_deg))

                if wd:
                    wd_list.append(str(wd).upper())

                if rr is not None:
                    rr_list.append(float(rr))

            if len(suhu_list) == 0:
                print(f"Tidak ada data suhu {nama_daerah}")
                continue

            tn = min(suhu_list)
            tx = max(suhu_list)
            tavg = sum(suhu_list) / len(suhu_list)

            rh_avg = (
                sum(rh_list) / len(rh_list)
                if rh_list else None
            )

            ff_x = max(ff_list) if ff_list else None
            ff_avg = (
                sum(ff_list) / len(ff_list)
                if ff_list else None
            )

            ddd_x = (
                wd_deg_list[ff_list.index(ff_x)]
                if ff_list and ff_x is not None
                else None
            )

            ddd_car = (
                max(set(wd_list), key=wd_list.count)
                if wd_list else None
            )

            rr = sum(rr_list) if rr_list else 0

            hasil_baru.append({
                "TANGGAL": pd.Timestamp(tanggal),
                "DAERAH": nama_daerah,
                "TN": round(tn, 2),
                "TX": round(tx, 2),
                "TAVG": round(tavg, 2),
                "RH_AVG": round(rh_avg, 2) if rh_avg else None,
                "DDD_X": round(ddd_x, 2) if ddd_x else None,
                "DDD_CAR": ddd_car,
                "RR": round(rr, 2),
                "FF_X": round(ff_x, 2) if ff_x else None,
                "FF_AVG": round(ff_avg, 2) if ff_avg else None
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

