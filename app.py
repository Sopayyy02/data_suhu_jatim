import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Dashboard Suhu Jawa Timur",
    layout="wide"
)

st.title("Dashboard Suhu Jawa Timur")
st.write("Visualisasi Data Suhu BMKG Jawa Timur")


# =========================
# LOAD DATA
# =========================

@st.cache_data

def load_data():

    df = pd.read_csv("data/data_gabungan.csv")

    df["tanggal"] = pd.to_datetime(df["tanggal"])

    # Tambahan kolom
    df["tahun"] = df["tanggal"].dt.year
    df["bulan"] = df["tanggal"].dt.month_name()
    df["hari"] = df["tanggal"].dt.day

    return df


# Load dataframe
df = load_data()


# =========================
# SIDEBAR FILTER
# =========================

st.sidebar.header("Filter Dashboard")

# FILTER DAERAH
pilih_daerah = st.sidebar.multiselect(
    "Pilih Daerah",
    options=sorted(df["daerah"].unique()),
    default=sorted(df["daerah"].unique())
)

# FILTER TAHUN
pilih_tahun = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df["tahun"].unique()),
    default=sorted(df["tahun"].unique())
)

# FILTER BULAN
pilih_bulan = st.sidebar.multiselect(
    "Pilih Bulan",
    options=df["bulan"].unique(),
    default=df["bulan"].unique()
)

# FILTER TANGGAL
min_date = df["tanggal"].min()
max_date = df["tanggal"].max()

pilih_tanggal = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
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

# Filter tanggal
if len(pilih_tanggal) == 2:

    start_date = pd.to_datetime(pilih_tanggal[0])
    end_date = pd.to_datetime(pilih_tanggal[1])

    filtered_df = filtered_df[
        (filtered_df["tanggal"] >= start_date) &
        (filtered_df["tanggal"] <= end_date)
    ]


# =========================
# METRIC
# =========================

st.subheader("Ringkasan Data")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Rata-rata TN",
    round(filtered_df["tm"].mean(), 2)
)

col2.metric(
    "Rata-rata TX",
    round(filtered_df["tx"].mean(), 2)
)

col3.metric(
    "Rata-rata TAVG",
    round(filtered_df["tavg"].mean(), 2)
)


# =========================
# TABEL DATA
# =========================

st.subheader("Data Suhu")

st.dataframe(
    filtered_df,
    use_container_width=True
)


# =========================
# GRAFIK LINE TAVG
# =========================

st.subheader("Tren Suhu Rata-rata")

fig_line = px.line(
    filtered_df,
    x="tanggal",
    y="tavg",
    color="daerah",
    markers=True,
    title="Tren TAVG Setiap Daerah"
)

fig_line.update_layout(
    xaxis_title="Tanggal",
    yaxis_title="TAVG",
    hovermode="x unified"
)

st.plotly_chart(
    fig_line,
    use_container_width=True
)


# =========================
# GRAFIK BAR TN TX
# =========================

st.subheader("Perbandingan TN dan TX")

fig_bar = px.bar(
    filtered_df,
    x="daerah",
    y=["tm", "tx"],
    barmode="group",
    title="Perbandingan Suhu Minimum dan Maksimum"
)

st.plotly_chart(
    fig_bar,
    use_container_width=True
)


# =========================
# GRAFIK BOXPLOT
# =========================

st.subheader("Distribusi Suhu")

fig_box = px.box(
    filtered_df,
    x="daerah",
    y="tavg",
    color="daerah",
    title="Distribusi TAVG Tiap Daerah"
)

st.plotly_chart(
    fig_box,
    use_container_width=True
)


# =========================
# GRAFIK HEATMAP SEDERHANA
# =========================

st.subheader("Heatmap Suhu")

pivot_df = filtered_df.pivot_table(
    values="tavg",
    index="daerah",
    columns="tanggal",
    aggfunc="mean"
)

fig_heatmap = px.imshow(
    pivot_df,
    aspect="auto",
    title="Heatmap TAVG"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)
