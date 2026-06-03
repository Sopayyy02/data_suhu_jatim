import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard BMKG Jawa Timur",
    layout="wide"
)

st.title("Dashboard Data BMKG Jawa Timur")
st.write("Visualisasi suhu dan cuaca dari dataset BMKG")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("data/data_suhu_lama.xlsx")

    # Rapikan nama kolom
    df.columns = df.columns.str.strip().str.upper()

    # Rename kolom
    df = df.rename(columns={
        "TANGGAL": "tanggal",
        "DAERAH": "daerah",
        "TN": "tn",
        "TX": "tx",
        "TAVG": "tavg",
        "RH_AVG": "rh_avg",
        "RR": "rr",
        "SS": "ss",
        "FF_X": "ff_x",
        "DDD_X": "ddd_x",
        "FF_AVG": "ff_avg",
        "DDD_CAR": "ddd_car"
    })

    # Parsing tanggal
    df["tanggal"] = pd.to_datetime(df["tanggal"])

    # Tambahan fitur waktu
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.month_name()
    df["hari"] = df["tanggal"].dt.day

    return df

df = load_data()

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("Filter Data")

pilih_daerah = st.sidebar.multiselect(
    "Daerah",
    options=sorted(df["daerah"].unique()),
    default=sorted(df["daerah"].unique())
)

pilih_tahun = st.sidebar.multiselect(
    "Tahun",
    options=sorted(df["tahun"].unique()),
    default=sorted(df["tahun"].unique())
)

pilih_bulan = st.sidebar.multiselect(
    "Bulan",
    options=df["bulan"].unique(),
    default=df["bulan"].unique()
)

# Filter tanggal
min_date = df["tanggal"].min().date()
max_date = df["tanggal"].max().date()

rentang_tanggal = st.sidebar.date_input(
    "Rentang Tanggal",
    [min_date, max_date]
)

# =========================
# FILTER DATA
# =========================
filtered_df = df[
    (df["daerah"].isin(pilih_daerah)) &
    (df["tahun"].isin(pilih_tahun)) &
    (df["bulan"].isin(pilih_bulan))
]

if len(rentang_tanggal) == 2:
    start_date = pd.to_datetime(rentang_tanggal[0])
    end_date = pd.to_datetime(rentang_tanggal[1])

    filtered_df = filtered_df[
        (filtered_df["tanggal"] >= start_date) &
        (filtered_df["tanggal"] <= end_date)
    ]

# =========================
# METRIC
# =========================
st.subheader("Ringkasan")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Jumlah Data", len(filtered_df))
col2.metric("Rata-rata TN", round(filtered_df["tn"].mean(), 2))
col3.metric("Rata-rata TX", round(filtered_df["tx"].mean(), 2))
col4.metric("Rata-rata TAVG", round(filtered_df["tavg"].mean(), 2))

# =========================
# TABLE
# =========================
st.subheader("Dataset")
kolom_tampil = [
    "tanggal",
    "daerah",
    "tn",
    "tx",
    "tavg",
    "rh_avg",
    "rr",
    "ss",
    "ff_x",
    "ddd_x",
    "ff_avg",
    "ddd_car"
]

st.dataframe(
    filtered_df[kolom_tampil],
    use_container_width=True
)
# =========================
# LINE CHART
# =========================
st.subheader("Tren Suhu Harian")

fig_line = px.line(
    filtered_df,
    x="tanggal",
    y="tavg",
    color="daerah",
    markers=True,
    title="Tren TAVG Setiap Daerah"
)

st.plotly_chart(fig_line, use_container_width=True)

# =========================
# BAR CHART
# =========================
st.subheader("Perbandingan TN dan TX")

avg_daerah = filtered_df.groupby("daerah")[["tn", "tx"]].mean().reset_index()

fig_bar = px.bar(
    avg_daerah,
    x="daerah",
    y=["tn", "tx"],
    barmode="group",
    title="Rata-rata Suhu Minimum dan Maksimum"
)

st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# BOXPLOT
# =========================
st.subheader("Distribusi Suhu")

fig_box = px.box(
    filtered_df,
    x="daerah",
    y="tavg",
    color="daerah"
)

st.plotly_chart(fig_box, use_container_width=True)

# =========================
# HEATMAP
# =========================
st.subheader("Heatmap Temperatur")

pivot_df = filtered_df.pivot_table(
    values="tavg",
    index="daerah",
    columns="tanggal",
    aggfunc="mean"
)

fig_heatmap = px.imshow(
    pivot_df,
    aspect="auto"
)

st.plotly_chart(fig_heatmap, use_container_width=True)