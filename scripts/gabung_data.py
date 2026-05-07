import pandas as pd

# =========================
# BACA DATA
# =========================

# Data lama Excel
df_lama = pd.read_excel("../data/data_suhu_lama.xlsx")

# Data baru hasil BMKG
df_baru = pd.read_csv("../data/suhu_jatim_baru.csv")


# =========================
# SESUAIKAN NAMA KOLOM
# =========================

df_baru = df_baru.rename(columns={
    "Tanggal": "tanggal",
    "Nama Stasiun": "daerah",
    "TN": "tm",
    "TX": "tx",
    "TAVG": "tavg"
})


# =========================
# PILIH KOLOM YANG DIPAKAI
# =========================

df_baru = df_baru[
    ["tanggal", "daerah", "tm", "tx", "tavg"]
]


# =========================
# GABUNGKAN DATA
# =========================

df_gabungan = pd.concat(
    [df_lama, df_baru],
    ignore_index=True
)


# =========================
# HAPUS DATA KOSONG
# =========================

df_gabungan = df_gabungan.dropna(
    subset=["tm", "tx", "tavg"]
)


# =========================
# HAPUS DUPLIKAT
# =========================

df_gabungan = df_gabungan.drop_duplicates()


# =========================
# FORMAT TANGGAL
# =========================

df_gabungan["tanggal"] = pd.to_datetime(
    df_gabungan["tanggal"]
)

df_gabungan = df_gabungan.sort_values(
    by="tanggal"
)


# =========================
# SIMPAN HASIL
# =========================

df_gabungan.to_csv(
    "../data/data_gabungan.csv",
    index=False
)

df_gabungan.to_excel(
    "../data/data_gabungan.xlsx",
    index=False
)


# =========================
# OUTPUT
# =========================

print("Data berhasil digabung!")

print("\nJumlah data:")
print(len(df_gabungan))

print("\n5 data terakhir:")
print(df_gabungan.tail())