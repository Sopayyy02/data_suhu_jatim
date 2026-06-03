import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard BMKG Jawa Timur",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# THEME / CSS
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0, 229, 255, 0.12), transparent 24%),
            radial-gradient(circle at top right, rgba(168, 85, 247, 0.12), transparent 22%),
            linear-gradient(135deg, #060816 0%, #0b1020 45%, #130f2a 100%);
        color: #e8ecff;
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", Inter, system-ui, sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: rgba(11, 16, 32, 0.72);
        backdrop-filter: blur(18px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .glass-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
        border: 1px solid rgba(255,255,255,0.12);
        backdrop-filter: blur(18px);
        border-radius: 22px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }

    .hero {
        background: linear-gradient(135deg, rgba(0,229,255,0.16), rgba(168,85,247,0.16));
        border: 1px solid rgba(255,255,255,0.14);
        backdrop-filter: blur(18px);
        border-radius: 28px;
        padding: 24px 24px 18px 24px;
        box-shadow: 0 16px 50px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.15rem;
        color: #ffffff;
        letter-spacing: 0.2px;
    }

    .hero p {
        margin: 0.45rem 0 0 0;
        color: rgba(232,236,255,0.78);
        font-size: 0.98rem;
    }

    .metric-wrap {
        background: linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 14px 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.22);
    }

    .metric-title {
        font-size: 0.84rem;
        color: rgba(232,236,255,0.75);
        margin-bottom: 4px;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
    }

    .metric-sub {
        font-size: 0.82rem;
        color: rgba(0,229,255,0.9);
        margin-top: 4px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00e5ff, #a855f7);
        color: #ffffff;
        border: none;
        border-radius: 14px;
        padding: 0.6rem 1rem;
        font-weight: 700;
        box-shadow: 0 8px 22px rgba(0,229,255,0.18);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 26px rgba(168,85,247,0.25);
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: rgba(255,255,255,0.04) !important;
        border-color: rgba(255,255,255,0.10) !important;
        color: #e8ecff !important;
    }

    label, .stMarkdown, .stText {
        color: #e8ecff !important;
    }

    .stDataFrame {
        background: rgba(255,255,255,0.02);
        border-radius: 18px;
        overflow: hidden;
    }

    hr {
        border-color: rgba(255,255,255,0.10) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
DATA_PATH = Path("data/data_suhu_lama.xlsx")

NUMERIC_COLS = [
    "tn", "tx", "tavg", "rh_avg", "rr", "ss", "ff_x", "ddd_x", "ff_avg"
]

RENAME_MAP = {
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
    "DDD_CAR": "ddd_car",
}

def safe_mean(series: pd.Series):
    if series is None or series.empty:
        return None
    val = series.mean()
    return None if pd.isna(val) else round(float(val), 2)

def safe_max(series: pd.Series):
    if series is None or series.empty:
        return None
    val = series.max()
    return None if pd.isna(val) else round(float(val), 2)

def safe_min(series: pd.Series):
    if series is None or series.empty:
        return None
    val = series.min()
    return None if pd.isna(val) else round(float(val), 2)

def fmt_num(val, suffix=""):
    if val is None or pd.isna(val):
        return "-"
    if float(val).is_integer():
        return f"{int(val)}{suffix}"
    return f"{val:.2f}{suffix}"

def render_metric_card(title, value, subtext=""):
    st.markdown(
        f"""
        <div class="metric-wrap">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

@st.cache_data(show_spinner=False)
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"File tidak ditemukan: {DATA_PATH.resolve()}"
        )

    df = pd.read_excel(DATA_PATH)
    df.columns = df.columns.str.strip().str.upper()
    df = df.rename(columns=RENAME_MAP)

    if "tanggal" not in df.columns or "daerah" not in df.columns:
        raise ValueError(
            "Kolom wajib tidak ditemukan. Pastikan ada TANGGAL dan DAERAH."
        )

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.dropna(subset=["tanggal", "daerah"]).copy()

    df["daerah"] = (
        df["daerah"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "ddd_car" in df.columns:
        df["ddd_car"] = (
            df["ddd_car"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    df["tahun"] = df["tanggal"].dt.year
    df["bulan_num"] = df["tanggal"].dt.month
    df["bulan"] = df["tanggal"].dt.strftime("%B")
    df["bulan_tahun"] = df["tanggal"].dt.strftime("%Y-%m")
    df["hari"] = df["tanggal"].dt.day

    df = df.sort_values(["tanggal", "daerah"]).reset_index(drop=True)
    return df

def apply_filters(df: pd.DataFrame):
    st.sidebar.markdown("## 🎛️ Filter")

    all_daerah = sorted(df["daerah"].dropna().unique().tolist())
    all_tahun = sorted(df["tahun"].dropna().unique().tolist())

    bulan_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    bulan_tersedia = [b for b in bulan_order if b in df["bulan"].unique()]

    if "selected_daerah" not in st.session_state:
        st.session_state.selected_daerah = all_daerah
    if "selected_tahun" not in st.session_state:
        st.session_state.selected_tahun = all_tahun
    if "selected_bulan" not in st.session_state:
        st.session_state.selected_bulan = bulan_tersedia
    if "date_range" not in st.session_state:
        st.session_state.date_range = [df["tanggal"].min().date(), df["tanggal"].max().date()]

    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    if st.sidebar.button("♻️ Reset Filter"):
        st.session_state.selected_daerah = all_daerah
        st.session_state.selected_tahun = all_tahun
        st.session_state.selected_bulan = bulan_tersedia
        st.session_state.date_range = [df["tanggal"].min().date(), df["tanggal"].max().date()]
        st.rerun()

    selected_daerah = st.sidebar.multiselect(
        "Daerah",
        options=all_daerah,
        default=st.session_state.selected_daerah,
        key="selected_daerah",
    )

    selected_tahun = st.sidebar.multiselect(
        "Tahun",
        options=all_tahun,
        default=st.session_state.selected_tahun,
        key="selected_tahun",
    )

    selected_bulan = st.sidebar.multiselect(
        "Bulan",
        options=bulan_tersedia,
        default=st.session_state.selected_bulan,
        key="selected_bulan",
    )

    date_range = st.sidebar.date_input(
        "Rentang Tanggal",
        value=st.session_state.date_range,
        min_value=df["tanggal"].min().date(),
        max_value=df["tanggal"].max().date(),
        key="date_range",
    )

    filtered = df[
        (df["daerah"].isin(selected_daerah)) &
        (df["tahun"].isin(selected_tahun)) &
        (df["bulan"].isin(selected_bulan))
    ].copy()

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered = filtered[
            (filtered["tanggal"] >= start_date) &
            (filtered["tanggal"] <= end_date)
        ].copy()

    return filtered

def nice_line_chart(filtered_df: pd.DataFrame):
    fig = px.line(
        filtered_df.sort_values("tanggal"),
        x="tanggal",
        y="tavg",
        color="daerah",
        markers=True,
        line_shape="spline",
        template="plotly_dark",
        title="Tren TAVG Harian"
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7)
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        legend_title_text="Daerah",
        title_font=dict(size=18),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        height=480,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig

def heatmap_chart(filtered_df: pd.DataFrame):
    pivot = filtered_df.pivot_table(
        values="tavg",
        index="daerah",
        columns="bulan_tahun",
        aggfunc="mean"
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=["#1f1d4a", "#2b7cff", "#00e5ff", "#a855f7"],
        template="plotly_dark",
        title="Heatmap TAVG per Daerah"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    return fig

def boxplot_chart(filtered_df: pd.DataFrame):
    fig = px.box(
        filtered_df,
        x="daerah",
        y="tavg",
        color="daerah",
        template="plotly_dark",
        title="Distribusi TAVG"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        showlegend=False,
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    return fig

def bar_avg_chart(filtered_df: pd.DataFrame):
    avg_daerah = (
        filtered_df.groupby("daerah", as_index=False)[["tn", "tx", "tavg"]]
        .mean()
        .sort_values("tavg", ascending=False)
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=avg_daerah["daerah"],
        y=avg_daerah["tn"],
        name="TN",
        marker_color="#00E5FF"
    ))
    fig.add_trace(go.Bar(
        x=avg_daerah["daerah"],
        y=avg_daerah["tx"],
        name="TX",
        marker_color="#A855F7"
    ))
    fig.add_trace(go.Bar(
        x=avg_daerah["daerah"],
        y=avg_daerah["tavg"],
        name="TAVG",
        marker_color="#6EE7FF"
    ))

    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        title="Rata-rata TN, TX, dan TAVG per Daerah",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
        legend_title_text="Variabel",
    )
    fig.update_xaxes(tickangle=-20, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig

def wind_chart(filtered_df: pd.DataFrame):
    if "ddd_car" not in filtered_df.columns:
        return None

    wind_df = (
        filtered_df["ddd_car"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    wind_df = wind_df[wind_df != "NAN"]

    if wind_df.empty:
        return None

    wind_counts = wind_df.value_counts().reset_index()
    wind_counts.columns = ["arah", "jumlah"]

    fig = px.pie(
        wind_counts,
        names="arah",
        values="jumlah",
        hole=0.5,
        template="plotly_dark",
        title="Distribusi Arah Angin Dominan"
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(
            colors=["#00E5FF", "#A855F7", "#6EE7FF", "#7C3AED", "#38BDF8", "#C084FC"]
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    return fig

# =========================
# LOAD DATA
# =========================
try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# =========================
# HERO
# =========================
st.markdown(
    """
    <div class="hero">
        <h1>Dashboard BMKG Jawa Timur 🌦️</h1>
        <p>Proyek visualisasi data cuaca interaktif berbasis Streamlit yang menampilkan informasi suhu, curah hujan, kelembapan, dan kondisi angin melalui grafik modern serta filter dinamis untuk mempermudah analisis pola cuaca di berbagai daerah di Jawa Timur.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# FILTER
# =========================
filtered_df = apply_filters(df)

# =========================
# QUICK INSIGHTS
# =========================
if filtered_df.empty:
    st.warning("Data kosong. Coba ubah filter yang dipilih.")
    st.stop()

min_tavg = safe_min(filtered_df["tavg"])
max_tavg = safe_max(filtered_df["tavg"])
avg_tavg = safe_mean(filtered_df["tavg"])
avg_tn = safe_mean(filtered_df["tn"])
avg_tx = safe_mean(filtered_df["tx"])

top_daerah = (
    filtered_df.groupby("daerah")["tavg"]
    .mean()
    .sort_values(ascending=False)
)

if not top_daerah.empty:
    daerah_terpanas = top_daerah.index[0]
    daerah_terdingin = top_daerah.index[-1]
else:
    daerah_terpanas = "-"
    daerah_terdingin = "-"

latest_date = filtered_df["tanggal"].max().date()
total_data = len(filtered_df)

st.markdown("### Ringkasan Cepat")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Jumlah Data", f"{total_data:,}", f"Update terakhir: {latest_date}")
with c2:
    render_metric_card("Rata-rata TAVG", fmt_num(avg_tavg, "°C"), f"Min: {fmt_num(min_tavg, '°C')} | Max: {fmt_num(max_tavg, '°C')}")
with c3:
    render_metric_card("Daerah Terpanas", daerah_terpanas, f"Rata-rata TAVG tertinggi")
with c4:
    render_metric_card("Daerah Terdingin", daerah_terdingin, f"Rata-rata TAVG terendah")

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# TABS
# =========================
tab_overview, tab_suhu, tab_angin, tab_dataset = st.tabs(
    ["📊 Overview", "🌡️ Suhu", "💨 Angin", "📁 Dataset"]
)

with tab_overview:
    st.markdown("### Overview BMKG")
    col_a, col_b = st.columns([1.6, 1])

    with col_a:
        st.plotly_chart(
            nice_line_chart(filtered_df),
            use_container_width=True,
            key="overview_line"
        )

    with col_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Insight Otomatis")
        st.write(f"• Data paling baru pada **{latest_date}**")
        st.write(f"• Rata-rata **TN**: **{fmt_num(avg_tn, '°C')}**")
        st.write(f"• Rata-rata **TX**: **{fmt_num(avg_tx, '°C')}**")
        st.write(f"• Rata-rata **TAVG**: **{fmt_num(avg_tavg, '°C')}**")
        st.write(f"• Daerah terpanas: **{daerah_terpanas}**")
        st.write(f"• Daerah terdingin: **{daerah_terdingin}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_c, col_d = st.columns([1, 1])
    with col_c:
        st.plotly_chart(
            bar_avg_chart(filtered_df),
            use_container_width=True,
            key="overview_bar"
        )
    with col_d:
        heatmap = heatmap_chart(filtered_df)
        st.plotly_chart(
            heatmap,
            use_container_width=True,
            key="overview_heatmap"
        )

with tab_suhu:
    st.markdown("### Visualisasi Suhu")
    col1, col2 = st.columns([1.35, 1])

    with col1:
        mode = st.selectbox(
            "Pilih gaya visual",
            ["Tren TAVG", "Distribusi TAVG", "Rata-rata TN/TX/TAVG"],
            index=0,
        )

        if mode == "Tren TAVG":
            st.plotly_chart(
                nice_line_chart(filtered_df),
                use_container_width=True,
                key="suhu_line"
            )
        elif mode == "Distribusi TAVG":
            st.plotly_chart(
                boxplot_chart(filtered_df),
                use_container_width=True,
                key="suhu_box"
            )
        else:
            st.plotly_chart(
                bar_avg_chart(filtered_df),
                use_container_width=True,
                key="suhu_bar"
            )

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Statistik Suhu")
        st.write(f"• TN terendah: **{fmt_num(safe_min(filtered_df['tn']), '°C')}**")
        st.write(f"• TN tertinggi: **{fmt_num(safe_max(filtered_df['tn']), '°C')}**")
        st.write(f"• TX terendah: **{fmt_num(safe_min(filtered_df['tx']), '°C')}**")
        st.write(f"• TX tertinggi: **{fmt_num(safe_max(filtered_df['tx']), '°C')}**")
        st.write(f"• TAVG terendah: **{fmt_num(safe_min(filtered_df['tavg']), '°C')}**")
        st.write(f"• TAVG tertinggi: **{fmt_num(safe_max(filtered_df['tavg']), '°C')}**")
        st.markdown("</div>", unsafe_allow_html=True)

with tab_angin:
    st.markdown("### Visualisasi Angin")
    col1, col2 = st.columns([1.25, 1])

    with col1:
        wind_fig = wind_chart(filtered_df)
        if wind_fig is not None:
            st.plotly_chart(
                wind_fig,
                use_container_width=True,
                key="wind_pie"
            )
        else:
            st.info("Data arah angin belum cukup untuk divisualisasikan.")

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Ringkasan Angin")
        st.write(f"• Rata-rata kecepatan angin maksimum: **{fmt_num(safe_mean(filtered_df['ff_x']), '')}**")
        st.write(f"• Rata-rata kecepatan angin: **{fmt_num(safe_mean(filtered_df['ff_avg']), '')}**")
        st.write(f"• Data arah dominan: **{filtered_df['ddd_car'].nunique() if 'ddd_car' in filtered_df.columns else 0}** kategori")
        if "ddd_x" in filtered_df.columns:
            st.write(f"• Derajat angin min: **{fmt_num(safe_min(filtered_df['ddd_x']), '')}**")
            st.write(f"• Derajat angin max: **{fmt_num(safe_max(filtered_df['ddd_x']), '')}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if "ff_x" in filtered_df.columns and "ff_avg" in filtered_df.columns:
        wind_speed = filtered_df.groupby("daerah", as_index=False)[["ff_x", "ff_avg"]].mean()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=wind_speed["daerah"],
            y=wind_speed["ff_x"],
            name="FF_X",
            marker_color="#00E5FF"
        ))
        fig.add_trace(go.Bar(
            x=wind_speed["daerah"],
            y=wind_speed["ff_avg"],
            name="FF_AVG",
            marker_color="#A855F7"
        ))
        fig.update_layout(
            barmode="group",
            template="plotly_dark",
            title="Kecepatan Angin per Daerah",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#E8ECFF"),
            margin=dict(l=10, r=10, t=50, b=10),
            height=420,
        )
        fig.update_xaxes(tickangle=-20, gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="wind_speed"
        )

with tab_dataset:
    st.markdown("### Dataset")
    search = st.text_input("Cari data", placeholder="Contoh: SURABAYA, 2026-06-03, 27.5")
    show_rows = st.selectbox("Jumlah baris yang ditampilkan", [10, 25, 50, 100], index=1)

    table_df = filtered_df.copy()

    if search.strip():
        q = search.strip().upper()
        mask = pd.Series(False, index=table_df.index)

        for col in table_df.columns:
            mask = mask | table_df[col].astype(str).str.upper().str.contains(q, na=False)

        table_df = table_df[mask]

    kolom_tampil = [
        "tanggal", "daerah", "tn", "tx", "tavg",
        "rh_avg", "rr", "ss", "ff_x", "ddd_x", "ff_avg", "ddd_car"
    ]
    kolom_tersedia = [c for c in kolom_tampil if c in table_df.columns]

    st.caption(f"Menampilkan {min(len(table_df), show_rows)} dari {len(table_df)} baris")
    st.dataframe(
        table_df[kolom_tersedia].head(show_rows),
        use_container_width=True,
        height=420
    )

    csv_data = table_df[kolom_tersedia].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV",
        data=csv_data,
        file_name="bmkg_jatim_filtered.csv",
        mime="text/csv",
    )