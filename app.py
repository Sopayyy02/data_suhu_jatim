import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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
# CONSTANTS
# =========================
DATA_PATH = Path("data/data_suhu_lama.xlsx")

MONTHS_ID = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
MONTH_TO_NUM = {name: i + 1 for i, name in enumerate(MONTHS_ID)}
NUM_TO_MONTH = {i + 1: name for i, name in enumerate(MONTHS_ID)}

PARAMETER_OPTIONS = {
    "TN (Suhu Minimum)": "tn",
    "TX (Suhu Maksimum)": "tx",
    "TAVG (Suhu Rata-rata)": "tavg",
    "RH_AVG (Kelembapan)": "rh_avg",
    "RR (Curah Hujan)": "rr",
    "SS (Lama Penyinaran)": "ss",
    "FF_X (Kecepatan Angin Maks)": "ff_x",
    "FF_AVG (Kecepatan Angin Rata-rata)": "ff_avg",
    "DDD_X (Derajat Angin)": "ddd_x",
}

PARAMETER_UNIT = {
    "tavg": "°C",
    "tn": "°C",
    "tx": "°C",
    "rh_avg": "%",
    "rr": "mm",
    "ss": "jam",
    "ff_x": "",
    "ff_avg": "",
    "ddd_x": "°",
}

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

DEFAULT_PARAMETER = "TAVG (Suhu Rata-rata)"

JATIM_COORDS = {
    "SURABAYA": (-7.2458, 112.7378),
    "MALANG": (-7.9797, 112.6304),
    "KEDIRI": (-7.8480, 112.0178),
    "JEMBER": (-8.1724, 113.7018),
    "BANYUWANGI": (-8.2191, 114.3691),
    "MADIUN": (-7.6298, 111.5258),
    "BOJONEGORO": (-7.1500, 111.8833),
    "PAMEKASAN": (-7.1569, 113.4721),
    "SUMENEP": (-6.9798, 113.8622),
    "PASURUAN": (-7.6454, 112.9079),
    "PROBOLINGGO": (-7.7543, 113.2159),
    "LUMAJANG": (-8.1298, 113.2226),
    "SITUBONDO": (-7.7057, 114.0082),
    "BONDOWOSO": (-7.9064, 113.8191),
    "NGAWI": (-7.4067, 111.4399),
    "LAMONGAN": (-7.1163, 112.4172),
    "GRESIK": (-7.1566, 112.6529),
    "SIDOARJO": (-7.4478, 112.7183),
    "MOJOKERTO": (-7.4722, 111.4325),
    "JOMBANG": (-7.5459, 111.8205),
    "BLITAR": (-8.0956, 112.1620),
    "TULUNGAGUNG": (-8.0655, 111.9024),
    "TRENGGALEK": (-8.0480, 111.7086),
    "PONOROGO": (-7.8672, 111.4627),
    "MAGETAN": (-7.6480, 111.3289),
    "NGANJUK": (-7.6040, 111.9054),
    "TUBAN": (-6.8972, 112.0497),
    "BANGKALAN": (-7.0327, 112.7296),
    "SAMPANG": (-7.1945, 113.2432),
    "PACITAN": (-8.1963, 111.1049),
    "BATU": (-7.8679, 112.5262),
    "NGANJUK": (-7.6040, 111.9054),
    "MOJOKERTO KOTA": (-7.4722, 111.4325),
    "BLITAR KOTA": (-8.0956, 112.1620),
    "MALANG KOTA": (-7.9797, 112.6304),
    "PASURUAN KOTA": (-7.6454, 112.9079),
    "PROBOLINGGO KOTA": (-7.7543, 113.2159),
    "MADIUN KOTA": (-7.6298, 111.5258),
    "KEDIRI KOTA": (-7.8480, 112.0178),
}

# =========================
# HELPERS
# =========================
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
    try:
        if float(val).is_integer():
            return f"{int(val)}{suffix}"
    except Exception:
        return f"{val}{suffix}"
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
        raise FileNotFoundError(f"File tidak ditemukan: {DATA_PATH.resolve()}")

    df = pd.read_excel(DATA_PATH)
    df.columns = df.columns.str.strip().str.upper()
    df = df.rename(columns=RENAME_MAP)

    if "tanggal" not in df.columns or "daerah" not in df.columns:
        raise ValueError("Kolom wajib tidak ditemukan. Pastikan ada TANGGAL dan DAERAH.")

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
    df["bulan"] = df["bulan_num"].map(NUM_TO_MONTH)
    df["bulan_tahun"] = df["tanggal"].dt.strftime("%Y-%m")
    df["hari"] = df["tanggal"].dt.day

    df = df.sort_values(["tanggal", "daerah"]).reset_index(drop=True)
    return df


def get_series(df: pd.DataFrame, col: str):
    if col in df.columns:
        return df[col].dropna()
    return pd.Series(dtype="float64")


def distribution_chart(filtered_df: pd.DataFrame, parameter_col: str, parameter_label: str):
    if filtered_df.empty or parameter_col not in filtered_df.columns:
        return None

    unit = PARAMETER_UNIT.get(parameter_col, "")
    stats = (
        filtered_df.groupby("daerah")[parameter_col]
        .agg(Min="min", Rata_rata="mean", Max="max")
        .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=stats["daerah"], y=stats["Min"],
        name="Minimum", marker_color="#38BDF8",
    ))
    fig.add_trace(go.Bar(
        x=stats["daerah"], y=stats["Rata_rata"],
        name="Rata-rata", marker_color="#A855F7",
    ))
    fig.add_trace(go.Bar(
        x=stats["daerah"], y=stats["Max"],
        name="Maksimum", marker_color="#F97316",
    ))
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        title=f"Perbandingan {parameter_label} per Daerah",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=60, b=10),
        height=420,
    )
    fig.update_xaxes(tickangle=-20, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", title=unit)
    return fig


def district_comparison_chart(filtered_df: pd.DataFrame, parameter_col: str, parameter_label: str):
    if filtered_df.empty or parameter_col not in filtered_df.columns:
        return None

    comp_df = (
        filtered_df
        .groupby("daerah", as_index=False)[parameter_col]
        .mean()
        .sort_values(parameter_col, ascending=False)
    )

    fig = px.bar(
        comp_df,
        x="daerah",
        y=parameter_col,
        template="plotly_dark",
        title=f"Perbandingan {parameter_label} per Daerah",
        color=parameter_col,
        color_continuous_scale=["#00E5FF", "#A855F7"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
        showlegend=False,
    )
    fig.update_xaxes(tickangle=-20, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig


def heatmap_chart(filtered_df: pd.DataFrame, parameter_col: str, parameter_label: str):
    if filtered_df.empty or parameter_col not in filtered_df.columns:
        return None

    pivot = filtered_df.pivot_table(
        values=parameter_col,
        index="daerah",
        columns="bulan_tahun",
        aggfunc="mean"
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=["#1f1d4a", "#2b7cff", "#00e5ff", "#a855f7"],
        template="plotly_dark",
        title=f"Heatmap {parameter_label} per Daerah"
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


def choropleth_map(filtered_df: pd.DataFrame, parameter_col: str, parameter_label: str):
    if filtered_df.empty or parameter_col not in filtered_df.columns:
        return None

    latest_date = filtered_df["tanggal"].max()
    map_df = (
        filtered_df[filtered_df["tanggal"] == latest_date]
        .groupby("daerah", as_index=False)[parameter_col]
        .mean()
    )

    map_df["lat"] = map_df["daerah"].map(lambda d: JATIM_COORDS.get(d, (None, None))[0])
    map_df["lon"] = map_df["daerah"].map(lambda d: JATIM_COORDS.get(d, (None, None))[1])
    map_df = map_df.dropna(subset=["lat", "lon"])

    if map_df.empty:
        return None

    unit = PARAMETER_UNIT.get(parameter_col, "")
    map_df["label"] = map_df[parameter_col].round(1).astype(str) + (f" {unit}" if unit else "")

    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        color=parameter_col,
        size=parameter_col,
        hover_name="daerah",
        hover_data={parameter_col: ":.1f", "label": False, "lat": False, "lon": False},
        text="label",
        color_continuous_scale=["#00E5FF", "#7C3AED", "#F97316"],
        size_max=40,
        zoom=7,
        center={"lat": -7.7, "lon": 112.5},
        mapbox_style="open-street-map",
        title=f"Peta {parameter_label} per Daerah ({latest_date.date()})",
    )
    fig.update_traces(textposition="top center", textfont=dict(size=11, color="white"))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        coloraxis_colorbar=dict(title=unit if unit else parameter_label),
        margin=dict(l=0, r=0, t=50, b=0),
        height=500,
    )
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
    wind_df = wind_df[(wind_df != "NAN") & (wind_df != "")]

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
        title="Distribusi Arah Angin Dominan",
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(
            colors=["#00E5FF", "#A855F7", "#6EE7FF", "#7C3AED", "#38BDF8", "#C084FC"]
        ),
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


def wind_speed_chart(filtered_df: pd.DataFrame):
    if not all(col in filtered_df.columns for col in ["ff_x", "ff_avg", "daerah"]):
        return None

    wind_speed = (
        filtered_df
        .groupby("daerah", as_index=False)[["ff_x", "ff_avg"]]
        .mean()
    )

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
    return fig


def make_trend_chart(filtered_df: pd.DataFrame, mode: str, parameter_col: str, parameter_label: str, selected_year_ref=None):
    if filtered_df.empty or parameter_col not in filtered_df.columns:
        return None

    unit = PARAMETER_UNIT.get(parameter_col, "")

    if mode == "Harian":
        chart_df = (
            filtered_df
            .groupby("tanggal", as_index=False)[parameter_col]
            .mean()
            .sort_values("tanggal")
        )

        fig = px.line(
            chart_df,
            x="tanggal",
            y=parameter_col,
            markers=True,
            line_shape="spline",
            template="plotly_dark",
            title=f"Tren Harian {parameter_label}",
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=7))
        fig.update_xaxes(title="Tanggal")
        fig.update_yaxes(title=f"{parameter_label} ({unit})" if unit else parameter_label)

    elif mode == "Bulanan":
        chart_df = (
            filtered_df
            .groupby(["bulan_num", "bulan"], as_index=False)[parameter_col]
            .mean()
            .sort_values("bulan_num")
        )

        fig = px.bar(
            chart_df,
            x="bulan",
            y=parameter_col,
            template="plotly_dark",
            title=f"Tren Bulanan {parameter_label} ({selected_year_ref})",
            color=parameter_col,
            color_continuous_scale=["#00E5FF", "#A855F7"],
        )
        fig.update_xaxes(categoryorder="array", categoryarray=MONTHS_ID, title="Bulan")
        fig.update_yaxes(title=f"{parameter_label} ({unit})" if unit else parameter_label)
        fig.update_layout(showlegend=False)

    else:
        chart_df = (
            filtered_df
            .groupby("tahun", as_index=False)[parameter_col]
            .mean()
            .sort_values("tahun")
        )

        fig = px.line(
            chart_df,
            x="tahun",
            y=parameter_col,
            markers=True,
            line_shape="spline",
            template="plotly_dark",
            title=f"Tren Tahunan {parameter_label}",
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_xaxes(title="Tahun")
        fig.update_yaxes(title=f"{parameter_label} ({unit})" if unit else parameter_label)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10),
        height=460,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
    return fig


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


def render_parameter_trends(filtered_df: pd.DataFrame, mode: str, selected_parameters: list, selected_year_ref=None, section_key="section"):
    if not selected_parameters:
        selected_parameters = [DEFAULT_PARAMETER]

    if len(selected_parameters) == 1:
        label = selected_parameters[0]
        col = PARAMETER_OPTIONS[label]
        fig = make_trend_chart(filtered_df, mode, col, label, selected_year_ref)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, key=f"{section_key}_{col}_{mode}")
        else:
            st.info("Tidak ada data yang bisa divisualisasikan.")
        return

    tabs = st.tabs(selected_parameters)
    for tab, label in zip(tabs, selected_parameters):
        with tab:
            col = PARAMETER_OPTIONS[label]
            fig = make_trend_chart(filtered_df, mode, col, label, selected_year_ref)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, key=f"{section_key}_{col}_{mode}")
            else:
                st.info("Tidak ada data yang bisa divisualisasikan.")


def render_parameter_distributions(filtered_df: pd.DataFrame, selected_parameters: list, section_key="dist"):
    if not selected_parameters:
        selected_parameters = [DEFAULT_PARAMETER]

    if len(selected_parameters) == 1:
        label = selected_parameters[0]
        col = PARAMETER_OPTIONS[label]
        fig = distribution_chart(filtered_df, col, label)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, key=f"{section_key}_{col}")
        else:
            st.info("Distribusi belum bisa ditampilkan.")
        return

    tabs = st.tabs(selected_parameters)
    for tab, label in zip(tabs, selected_parameters):
        with tab:
            col = PARAMETER_OPTIONS[label]
            fig = distribution_chart(filtered_df, col, label)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, key=f"{section_key}_{col}")
            else:
                st.info("Distribusi belum bisa ditampilkan.")


def render_filter_box(df: pd.DataFrame, prefix: str, include_parameters: bool = True):
    all_daerah = sorted(df["daerah"].dropna().unique().tolist())
    all_years = sorted(df["tahun"].dropna().unique().tolist())
    min_date = df["tanggal"].min().date()
    max_date = df["tanggal"].max().date()

    if f"{prefix}_mode" not in st.session_state:
        st.session_state[f"{prefix}_mode"] = "Harian"
    if f"{prefix}_daerah" not in st.session_state:
        st.session_state[f"{prefix}_daerah"] = all_daerah
    if f"{prefix}_years" not in st.session_state:
        st.session_state[f"{prefix}_years"] = all_years
    if f"{prefix}_year_single" not in st.session_state:
        st.session_state[f"{prefix}_year_single"] = max(all_years)
    if f"{prefix}_months" not in st.session_state:
        st.session_state[f"{prefix}_months"] = MONTHS_ID
    if f"{prefix}_date_range" not in st.session_state:
        st.session_state[f"{prefix}_date_range"] = [min_date, max_date]
    if f"{prefix}_main_param" not in st.session_state:
        st.session_state[f"{prefix}_main_param"] = DEFAULT_PARAMETER
    if f"{prefix}_extra_params" not in st.session_state:
        st.session_state[f"{prefix}_extra_params"] = []

    mode = st.radio(
        "Mode Waktu",
        ["Harian", "Bulanan", "Tahunan"],
        key=f"{prefix}_mode",
        horizontal=True,
    )

    daerah = st.multiselect(
        "Daerah",
        options=all_daerah,
        default=st.session_state[f"{prefix}_daerah"],
        key=f"{prefix}_daerah",
    )
    if not daerah:
        daerah = all_daerah

    main_param = DEFAULT_PARAMETER
    extra_params = []
    if include_parameters:
        main_param = st.selectbox(
            "Parameter Utama",
            options=list(PARAMETER_OPTIONS.keys()),
            index=list(PARAMETER_OPTIONS.keys()).index(st.session_state[f"{prefix}_main_param"])
            if st.session_state[f"{prefix}_main_param"] in PARAMETER_OPTIONS
            else list(PARAMETER_OPTIONS.keys()).index(DEFAULT_PARAMETER),
            key=f"{prefix}_main_param",
        )

        extra_params = st.multiselect(
            "Parameter Tambahan",
            options=[p for p in PARAMETER_OPTIONS.keys() if p != main_param],
            default=[p for p in st.session_state[f"{prefix}_extra_params"] if p != main_param],
            key=f"{prefix}_extra_params",
        )

    active_params = [main_param] if include_parameters else [DEFAULT_PARAMETER]
    if include_parameters:
        active_params = [main_param] + [p for p in extra_params if p != main_param]

    filtered = df[df["daerah"].isin(daerah)].copy()
    selected_year_ref = None

    if mode == "Harian":
        date_range = st.date_input(
            "Rentang Tanggal",
            value=st.session_state[f"{prefix}_date_range"],
            min_value=min_date,
            max_value=max_date,
            key=f"{prefix}_date_range",
        )

        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])
            filtered = filtered[
                (filtered["tanggal"] >= start_date) &
                (filtered["tanggal"] <= end_date)
            ].copy()
        elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
            st.warning("Pilih tanggal akhir untuk menerapkan filter rentang tanggal.")

    elif mode == "Bulanan":
        year = st.selectbox(
            "Tahun",
            options=all_years,
            index=len(all_years) - 1,
            key=f"{prefix}_year_single",
        )

        months = st.multiselect(
            "Bulan",
            options=MONTHS_ID,
            default=st.session_state[f"{prefix}_months"],
            key=f"{prefix}_months",
        )
        if not months:
            months = MONTHS_ID

        month_nums = [MONTH_TO_NUM[m] for m in months]
        filtered = filtered[
            (filtered["tahun"] == year) &
            (filtered["bulan_num"].isin(month_nums))
        ].copy()
        selected_year_ref = year

    else:
        years = st.multiselect(
            "Tahun",
            options=all_years,
            default=st.session_state[f"{prefix}_years"],
            key=f"{prefix}_years",
        )
        if not years:
            years = all_years

        filtered = filtered[filtered["tahun"].isin(years)].copy()
        selected_year_ref = years

    total_all = len(df[df["daerah"].isin(daerah)])
    if filtered.empty:
        st.error("Tidak ada data untuk filter yang dipilih. Coba ubah rentang tanggal atau daerah.")
    else:
        st.caption(f"Data aktif: **{len(filtered):,}** baris dari {total_all:,} (daerah terpilih)")

    return filtered, mode, active_params, main_param, selected_year_ref


def render_page_summary(df: pd.DataFrame):
    min_date_all = df["tanggal"].min().date()
    max_date_all = df["tanggal"].max().date()

    # Suhu terpanas dan terdingin berdasarkan tanggal terbaru di dataset
    today_df = df[df["tanggal"].dt.date == max_date_all]

    daerah_terpanas, suhu_terpanas = "-", None
    if not today_df.empty and "tx" in today_df.columns:
        tx_today = today_df.dropna(subset=["tx"])
        if not tx_today.empty:
            idx_max = tx_today["tx"].idxmax()
            daerah_terpanas = tx_today.loc[idx_max, "daerah"]
            suhu_terpanas = round(float(tx_today["tx"].max()), 2)

    daerah_terdingin, suhu_terdingin = "-", None
    if not today_df.empty and "tn" in today_df.columns:
        tn_today = today_df.dropna(subset=["tn"])
        if not tn_today.empty:
            idx_min = tn_today["tn"].idxmin()
            daerah_terdingin = tn_today.loc[idx_min, "daerah"]
            suhu_terdingin = round(float(tn_today["tn"].min()), 2)

    st.markdown("### Ringkasan Dataset")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Suhu Terpanas Hari Ini", fmt_num(suhu_terpanas, "°C"), daerah_terpanas)
    with c2:
        render_metric_card("Suhu Terdingin Hari Ini", fmt_num(suhu_terdingin, "°C"), daerah_terdingin)
    with c3:
        render_metric_card("Data Terlama", str(min_date_all), "Tanggal awal")
    with c4:
        render_metric_card("Data Terbaru", str(max_date_all), "Tanggal akhir")

    st.markdown("<br>", unsafe_allow_html=True)
    if "tavg" in df.columns and "bulan_num" in df.columns:
        current_month_num = df["tanggal"].max().month
        modus_items = []
        for m_num in range(1, 13):
            series = df[df["bulan_num"] == m_num]["tavg"].dropna().round(1)
            mode_val = round(float(series.mode().iloc[0]), 1) if not series.empty else None
            modus_items.append((NUM_TO_MONTH[m_num], mode_val, m_num == current_month_num))

        month_tags = ""
        for bulan, val, is_current in modus_items:
            color = "#00E5FF" if is_current else "rgba(232,236,255,0.85)"
            bg = "rgba(0,229,255,0.14)" if is_current else "rgba(255,255,255,0.05)"
            border = "1px solid rgba(0,229,255,0.5)" if is_current else "1px solid rgba(255,255,255,0.08)"
            val_str = f"{val}°C" if val is not None else "-"
            month_tags += (
                f'<div style="display:inline-block;text-align:center;padding:7px 11px;margin:3px 2px;'
                f'background:{bg};border:{border};border-radius:12px;">'
                f'<div style="font-size:0.72rem;color:rgba(232,236,255,0.55);">{bulan[:3]}</div>'
                f'<div style="font-size:1.05rem;font-weight:700;color:{color};">{val_str}</div>'
                f'</div>'
            )

        current_bulan_name = NUM_TO_MONTH.get(current_month_num, "")
        current_modus = next((v for _, v, ic in modus_items if ic), None)
        current_str = f"{current_modus}°C" if current_modus is not None else "-"

        st.markdown(
            f"""
            <div class="glass-card">
                <div style="font-size:0.85rem;color:rgba(232,236,255,0.65);margin-bottom:4px;">
                    Modus Suhu Rata-rata per Bulan
                </div>
                <div style="font-size:1.3rem;font-weight:700;color:#00E5FF;margin-bottom:12px;">
                    Bulan terkini ({current_bulan_name}): {current_str}
                </div>
                <div style="line-height:1.4;">{month_tags}</div>
                <div style="font-size:0.74rem;color:rgba(232,236,255,0.4);margin-top:8px;">
                    ✦ Highlight biru = bulan terkini dalam dataset
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================
# ANIMATED CHARTS
# =========================
_ARAH_ARROW = {
    "N": "↑", "NNE": "↑", "NE": "↗", "ENE": "→",
    "E": "→", "ESE": "→", "SE": "↘", "SSE": "↓",
    "S": "↓", "SSW": "↓", "SW": "↙", "WSW": "←",
    "W": "←", "WNW": "←", "NW": "↖", "NNW": "↑",
    "CALM": "•", "VAR": "~",
}


def animated_wind_map(filtered_df: pd.DataFrame):
    if "ff_avg" not in filtered_df.columns:
        return None

    map_df = filtered_df.copy()
    map_df["tanggal_str"] = map_df["tanggal"].dt.strftime("%Y-%m-%d")
    map_df["lat"] = map_df["daerah"].map(lambda d: JATIM_COORDS.get(d, (None, None))[0])
    map_df["lon"] = map_df["daerah"].map(lambda d: JATIM_COORDS.get(d, (None, None))[1])
    map_df = map_df.dropna(subset=["lat", "lon", "ff_avg"])

    if map_df.empty:
        return None

    map_df["arah"] = (
        map_df.get("ddd_car", pd.Series("•", index=map_df.index))
        .astype(str).str.strip().str.upper()
        .map(lambda x: _ARAH_ARROW.get(x, "•"))
    )

    daily = (
        map_df.groupby(["tanggal_str", "daerah", "lat", "lon"])
        .agg(
            ff_avg=("ff_avg", "mean"),
            arah=("arah", lambda x: x.mode().iloc[0] if not x.empty else "•"),
        )
        .reset_index()
        .sort_values("tanggal_str")
    )

    if daily.empty:
        return None

    # Batasi maks 60 frame agar tidak lambat
    unique_dates = sorted(daily["tanggal_str"].unique())
    if len(unique_dates) > 60:
        step = max(1, len(unique_dates) // 60)
        unique_dates = unique_dates[::step]
        daily = daily[daily["tanggal_str"].isin(unique_dates)]

    if daily["tanggal_str"].nunique() < 2:
        return None

    fig = px.scatter_mapbox(
        daily,
        lat="lat", lon="lon",
        color="ff_avg",
        size="ff_avg",
        text="arah",
        hover_name="daerah",
        hover_data={"ff_avg": ":.1f", "tanggal_str": True, "lat": False, "lon": False},
        animation_frame="tanggal_str",
        color_continuous_scale=["#38BDF8", "#00E5FF", "#A855F7"],
        size_max=42,
        zoom=7,
        center={"lat": -7.7, "lon": 112.5},
        mapbox_style="open-street-map",
        title="Animasi Pergerakan Angin per Daerah",
    )
    fig.update_traces(textfont=dict(size=18, color="white"), textposition="middle center")

    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"] = {"duration": 200}

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8ECFF"),
        title_font=dict(size=18),
        coloraxis_colorbar=dict(title="km/h"),
        margin=dict(l=0, r=0, t=50, b=0),
        height=520,
    )
    return fig


def animated_rain_chart(filtered_df: pd.DataFrame):
    if "rr" not in filtered_df.columns:
        return None

    rr_by_daerah = (
        filtered_df.groupby("daerah")["rr"]
        .mean()
        .reset_index()
        .sort_values("rr", ascending=False)
    )
    rr_by_daerah = rr_by_daerah[rr_by_daerah["rr"] > 0]

    if rr_by_daerah.empty:
        return None

    daerah_list = rr_by_daerah["daerah"].tolist()
    rr_values = rr_by_daerah["rr"].tolist()
    rr_max = max(rr_values)
    n_daerah = len(daerah_list)

    n_frames = 40
    max_drops = 28
    np.random.seed(42)

    drops = []
    for i, rr in enumerate(rr_values):
        n = max(3, int(rr / rr_max * max_drops))
        x_off = np.random.uniform(-0.38, 0.38, n)
        y_start = np.random.uniform(0, 100, n)
        drops.append((i, n, x_off, y_start, rr))

    wave_x = np.linspace(-0.7, n_daerah - 0.3, 200)

    def make_wave(f):
        t = f * 0.28
        y = (10 + 2.2 * np.sin(wave_x * 3.5 + t)
             + 1.3 * np.sin(wave_x * 6.0 - t * 1.4)
             + 0.7 * np.cos(wave_x * 1.8 + t * 0.6))
        return wave_x.tolist(), y.tolist()

    frames = []
    for f in range(n_frames):
        x_all, y_all, color_all = [], [], []
        for i, n, x_off, y_start, rr in drops:
            y_pos = (y_start - f * 3.2) % 100
            x_all.extend((i + x_off).tolist())
            y_all.extend(y_pos.tolist())
            color_all.extend([rr] * n)

        wx, wy = make_wave(f)
        frames.append(go.Frame(
            data=[
                go.Scatter(
                    x=x_all, y=y_all,
                    mode="markers",
                    marker=dict(
                        size=7,
                        color=color_all,
                        colorscale=[[0, "#BAE6FD"], [0.5, "#2563EB"], [1, "#1E3A8A"]],
                        opacity=0.82,
                        symbol="line-ns-open",
                        line=dict(width=2.2),
                        cmin=0, cmax=rr_max,
                        showscale=False,
                    ),
                    showlegend=False,
                ),
                go.Scatter(
                    x=wx, y=wy,
                    mode="lines",
                    line=dict(color="rgba(56,189,248,0.9)", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(30,64,175,0.45)",
                    showlegend=False,
                ),
            ],
            name=str(f),
        ))

    annotations = [
        dict(
            x=i, y=-9,
            text=f"<b>{d[:11]}</b><br>{rr_values[i]:.1f} mm",
            showarrow=False,
            font=dict(size=10, color="#BAE6FD"),
            xanchor="center",
        )
        for i, d in enumerate(daerah_list)
    ]

    wx0, wy0 = make_wave(0)
    x0, y0, c0 = [], [], []
    for i, n, x_off, y_start, rr in drops:
        x0.extend((i + x_off).tolist())
        y0.extend(y_start.tolist())
        c0.extend([rr] * n)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=x0, y=y0,
                mode="markers",
                marker=dict(
                    size=7,
                    color=c0,
                    colorscale=[[0, "#BAE6FD"], [0.5, "#2563EB"], [1, "#1E3A8A"]],
                    opacity=0.82,
                    symbol="line-ns-open",
                    line=dict(width=2.2),
                    cmin=0, cmax=rr_max,
                    showscale=False,
                ),
                showlegend=False,
            ),
            go.Scatter(
                x=wx0, y=wy0,
                mode="lines",
                line=dict(color="rgba(56,189,248,0.9)", width=3),
                fill="tozeroy",
                fillcolor="rgba(30,64,175,0.45)",
                showlegend=False,
            ),
        ],
        frames=frames,
        layout=go.Layout(
            title="Animasi Curah Hujan per Daerah (rata-rata periode)",
            xaxis=dict(range=[-0.7, n_daerah - 0.3], showticklabels=False,
                       gridcolor="rgba(255,255,255,0.04)", zeroline=False),
            yaxis=dict(range=[-18, 100], showticklabels=False,
                       gridcolor="rgba(255,255,255,0.04)", zeroline=False),
            annotations=annotations,
            plot_bgcolor="rgba(0, 8, 30, 0.94)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8ECFF"),
            title_font=dict(size=18),
            height=480,
            updatemenus=[dict(
                type="buttons", showactive=False,
                x=0.05, y=1.10, xanchor="left",
                buttons=[
                    dict(label="▶ Play", method="animate",
                         args=[None, {"frame": {"duration": 60, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 0}}]),
                    dict(label="⏸ Pause", method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]),
                ],
            )],
            margin=dict(l=10, r=10, t=65, b=85),
        ),
    )
    return fig


def animated_rain_map(filtered_df: pd.DataFrame):
    if "rr" not in filtered_df.columns:
        return None

    map_df = (
        filtered_df.groupby("daerah")["rr"]
        .mean()
        .reset_index()
    )
    map_df["lat"] = map_df["daerah"].map(lambda d: JATIM_COORDS.get(d, (None, None))[0])
    map_df["lon"] = map_df["daerah"].map(lambda d: JATIM_COORDS.get(d, (None, None))[1])
    map_df = map_df.dropna(subset=["lat", "lon"])
    map_df = map_df[map_df["rr"] > 0]

    if map_df.empty:
        return None

    rr_max = map_df["rr"].max()
    map_df["size_base"] = (map_df["rr"] / rr_max * 32 + 10).round(1)
    map_df["label"] = map_df["rr"].round(1).astype(str) + " mm"

    lats = map_df["lat"].tolist()
    lons = map_df["lon"].tolist()
    rr_vals = map_df["rr"].tolist()
    labels = map_df["label"].tolist()
    daerah_names = map_df["daerah"].tolist()
    sizes_base = map_df["size_base"].tolist()

    n_frames = 32
    frames = []
    for f in range(n_frames):
        t = f / n_frames * 2 * np.pi
        pulse = 1 + 0.45 * np.sin(t)
        sizes = [round(s * pulse, 1) for s in sizes_base]
        opacity = float(0.62 + 0.28 * abs(np.sin(t)))

        frames.append(go.Frame(
            data=[go.Scattermapbox(
                lat=lats, lon=lons,
                mode="markers+text",
                marker=go.scattermapbox.Marker(
                    size=sizes,
                    color=rr_vals,
                    colorscale=[[0, "#BAE6FD"], [0.45, "#2563EB"], [1, "#1E3A8A"]],
                    cmin=0, cmax=rr_max,
                    opacity=opacity,
                    showscale=False,
                ),
                text=labels,
                hovertext=daerah_names,
                textposition="top center",
                textfont=dict(size=9, color="white"),
                showlegend=False,
            )],
            name=str(f),
        ))

    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=go.Layout(
            title="Peta Animasi Curah Hujan per Daerah 💧 (tekan ▶ Play)",
            mapbox=dict(
                style="open-street-map",
                zoom=7,
                center={"lat": -7.7, "lon": 112.5},
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E8ECFF"),
            title_font=dict(size=18),
            height=500,
            margin=dict(l=0, r=0, t=55, b=0),
            updatemenus=[dict(
                type="buttons", showactive=False,
                x=0.05, y=1.08, xanchor="left",
                buttons=[
                    dict(label="▶ Play", method="animate",
                         args=[None, {"frame": {"duration": 80, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 0}}]),
                    dict(label="⏸ Pause", method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]),
                ],
            )],
        ),
    )
    return fig


# =========================
# PAGE RENDERERS
# =========================
def render_cuaca_page(filtered_df: pd.DataFrame, mode: str, year_ref):
    st.markdown("### Cuaca — Suhu & Kelembapan")
    if filtered_df.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return

    latest_date = filtered_df["tanggal"].max().date()
    latest_df = filtered_df[filtered_df["tanggal"].dt.date == latest_date]

    suhu = safe_mean(get_series(latest_df, "tavg"))
    if suhu is not None:
        if suhu >= 34:   suhu_label = "Sangat Panas — hindari aktivitas luar"
        elif suhu >= 30: suhu_label = "Panas — tetap terhidrasi"
        elif suhu >= 25: suhu_label = "Hangat — cuaca nyaman"
        else:            suhu_label = "Sejuk — cocok aktivitas luar"
    else:
        suhu_label = "-"

    rh = safe_mean(get_series(latest_df, "rh_avg"))
    if rh is not None:
        if rh >= 80:   rh_label = "Sangat Lembap — waspadai pernapasan"
        elif rh >= 60: rh_label = "Lembap — cukup normal"
        else:          rh_label = "Normal — udara kering"
    else:
        rh_label = "-"

    tx_today = latest_df.dropna(subset=["tx"])
    if not tx_today.empty:
        daerah_panas = tx_today.loc[tx_today["tx"].idxmax(), "daerah"]
        suhu_max = round(float(tx_today["tx"].max()), 1)
    else:
        daerah_panas, suhu_max = "-", None

    tn_today = latest_df.dropna(subset=["tn"])
    if not tn_today.empty:
        daerah_dingin = tn_today.loc[tn_today["tn"].idxmin(), "daerah"]
        suhu_min = round(float(tn_today["tn"].min()), 1)
    else:
        daerah_dingin, suhu_min = "-", None

    st.markdown(f"#### Kondisi Terkini — {latest_date}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Suhu Udara", fmt_num(suhu, "°C"), suhu_label)
    with c2: render_metric_card("Kelembapan", fmt_num(rh, "%"), rh_label)
    with c3: render_metric_card("Daerah Terpanas", fmt_num(suhu_max, "°C"), daerah_panas)
    with c4: render_metric_card("Daerah Terdingin", fmt_num(suhu_min, "°C"), daerah_dingin)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1.6, 1])
    with col_a:
        fig = make_trend_chart(filtered_df, mode, "tavg", "TAVG (Suhu Rata-rata)", year_ref)
        if fig: st.plotly_chart(fig, use_container_width=True, key="cuaca_trend")
    with col_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Insight Cuaca")
        st.write(f"• Rata-rata TN: **{fmt_num(safe_mean(get_series(filtered_df, 'tn')), '°C')}**")
        st.write(f"• Rata-rata TX: **{fmt_num(safe_mean(get_series(filtered_df, 'tx')), '°C')}**")
        st.write(f"• Rata-rata TAVG: **{fmt_num(safe_mean(get_series(filtered_df, 'tavg')), '°C')}**")
        st.write(f"• Daerah terpanas: **{daerah_panas}**")
        st.write(f"• Daerah terdingin: **{daerah_dingin}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_c, col_d = st.columns([1, 1])
    with col_c:
        comp = district_comparison_chart(filtered_df, "tavg", "TAVG (Suhu Rata-rata)")
        if comp: st.plotly_chart(comp, use_container_width=True, key="cuaca_comp")
    with col_d:
        choro = choropleth_map(filtered_df, "tavg", "TAVG (Suhu Rata-rata)")
        if choro: st.plotly_chart(choro, use_container_width=True, key="cuaca_choro")
        else: st.info("Koordinat daerah tidak tersedia untuk peta.")


def render_hujan_page(filtered_df: pd.DataFrame, mode: str, year_ref):
    st.markdown("### Curah Hujan & Penyinaran")
    if filtered_df.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return

    latest_date = filtered_df["tanggal"].max().date()
    latest_df = filtered_df[filtered_df["tanggal"].dt.date == latest_date]

    rr = safe_mean(get_series(latest_df, "rr"))
    if rr is not None:
        if rr >= 50:  rr_label = "Hujan Lebat — jangan keluar rumah"
        elif rr >= 10: rr_label = "Hujan Sedang — bawa payung"
        elif rr > 0:  rr_label = "Gerimis — siapkan jas hujan"
        else:         rr_label = "Tidak Hujan — langit cerah"
    else:
        rr_label = "-"

    ss = safe_mean(get_series(latest_df, "ss"))
    if ss is not None:
        if ss >= 8:   ss_label = "Cerah sekali"
        elif ss >= 5: ss_label = "Cukup cerah"
        elif ss >= 2: ss_label = "Berawan"
        else:         ss_label = "Mendung"
    else:
        ss_label = "-"

    rr_today = latest_df.dropna(subset=["rr"])
    if not rr_today.empty and rr_today["rr"].max() > 0:
        daerah_hujan = rr_today.loc[rr_today["rr"].idxmax(), "daerah"]
        rr_max = round(float(rr_today["rr"].max()), 1)
    else:
        daerah_hujan, rr_max = "Tidak ada hujan", None

    if "rr" in filtered_df.columns:
        hari_hujan = int((filtered_df.groupby("tanggal")["rr"].mean() > 0).sum())
        total_hari = filtered_df["tanggal"].nunique()
    else:
        hari_hujan, total_hari = 0, 0

    st.markdown(f"#### Kondisi Terkini — {latest_date}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Curah Hujan", fmt_num(rr, " mm"), rr_label)
    with c2: render_metric_card("Lama Penyinaran", fmt_num(ss, " jam"), ss_label)
    with c3: render_metric_card("Daerah Hujan Terbanyak", fmt_num(rr_max, " mm"), daerah_hujan)
    with c4: render_metric_card("Hari Hujan", f"{hari_hujan} hari", f"dari {total_hari} hari total")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1.6, 1])
    with col_a:
        fig = make_trend_chart(filtered_df, mode, "rr", "RR (Curah Hujan)", year_ref)
        if fig: st.plotly_chart(fig, use_container_width=True, key="hujan_trend")
    with col_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Insight Hujan")
        st.write(f"• Rata-rata curah hujan: **{fmt_num(safe_mean(get_series(filtered_df, 'rr')), ' mm')}**")
        st.write(f"• Curah hujan tertinggi: **{fmt_num(safe_max(get_series(filtered_df, 'rr')), ' mm')}**")
        st.write(f"• Rata-rata penyinaran: **{fmt_num(safe_mean(get_series(filtered_df, 'ss')), ' jam')}**")
        st.write(f"• Hari hujan: **{hari_hujan}** dari **{total_hari}** hari")
        st.write(f"• Daerah hujan terbanyak: **{daerah_hujan}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_c, col_d = st.columns([1, 1])
    with col_c:
        comp = district_comparison_chart(filtered_df, "rr", "RR (Curah Hujan)")
        if comp: st.plotly_chart(comp, use_container_width=True, key="hujan_comp")
    with col_d:
        rain_map = animated_rain_map(filtered_df)
        if rain_map: st.plotly_chart(rain_map, use_container_width=True, key="hujan_choro")
        else: st.info("Koordinat daerah tidak tersedia untuk peta.")

    st.markdown("<br>", unsafe_allow_html=True)
    rain_anim = animated_rain_chart(filtered_df)
    if rain_anim:
        st.markdown("#### Animasi Hujan per Daerah (tekan ▶ Play)")
        st.plotly_chart(rain_anim, use_container_width=True, key="hujan_anim")
    else:
        st.info("Tidak ada data hujan pada periode yang dipilih.")


def render_angin_page(filtered_df: pd.DataFrame, mode: str, year_ref):
    st.markdown("### Angin")
    if filtered_df.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return

    latest_date = filtered_df["tanggal"].max().date()
    latest_df = filtered_df[filtered_df["tanggal"].dt.date == latest_date]

    ff_avg = safe_mean(get_series(latest_df, "ff_avg"))
    if ff_avg is not None:
        if ff_avg >= 30:   angin_label = "Angin Kencang — hati-hati di luar"
        elif ff_avg >= 15: angin_label = "Angin Sedang — cukup sejuk"
        else:              angin_label = "Angin Lemah — tenang"
    else:
        angin_label = "-"

    ff_x = safe_mean(get_series(latest_df, "ff_x"))
    ffx_label = "Sangat kencang" if ff_x and ff_x >= 45 else ("Kencang" if ff_x and ff_x >= 30 else "Normal")

    if "ddd_car" in latest_df.columns:
        arah = latest_df["ddd_car"].dropna().astype(str).str.strip().str.upper()
        arah = arah[arah != "NAN"]
        arah_dominan = arah.mode().iloc[0] if not arah.empty else "-"
    else:
        arah_dominan = "-"

    ddd_x = safe_mean(get_series(latest_df, "ddd_x"))

    st.markdown(f"#### Kondisi Terkini — {latest_date}")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_metric_card("Kecepatan Rata-rata", fmt_num(ff_avg, " km/h"), angin_label)
    with c2: render_metric_card("Kecepatan Maksimum", fmt_num(ff_x, " km/h"), ffx_label)
    with c3: render_metric_card("Arah Angin Dominan", arah_dominan, "Arah angin hari ini")
    with c4: render_metric_card("Derajat Angin", fmt_num(ddd_x, "°"), "Rata-rata hari ini")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1.25, 1])
    with col_a:
        wind_fig = wind_chart(filtered_df)
        if wind_fig: st.plotly_chart(wind_fig, use_container_width=True, key="angin_pie")
        else: st.info("Data arah angin tidak cukup untuk divisualisasikan.")
    with col_b:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Insight Angin")
        st.write(f"• Rata-rata kecepatan angin: **{fmt_num(safe_mean(get_series(filtered_df, 'ff_avg')), ' km/h')}**")
        st.write(f"• Rata-rata kecepatan maks: **{fmt_num(safe_mean(get_series(filtered_df, 'ff_x')), ' km/h')}**")
        st.write(f"• Arah dominan terkini: **{arah_dominan}**")
        if "ddd_car" in filtered_df.columns:
            n_arah = filtered_df["ddd_car"].dropna().nunique()
            st.write(f"• Jumlah arah berbeda: **{n_arah}**")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    anim_wind = animated_wind_map(filtered_df)
    if anim_wind:
        st.markdown("#### Animasi Pergerakan Angin (tekan ▶ Play)")
        st.plotly_chart(anim_wind, use_container_width=True, key="angin_anim")
    else:
        speed_fig = wind_speed_chart(filtered_df)
        if speed_fig: st.plotly_chart(speed_fig, use_container_width=True, key="angin_speed")


def render_dataset_page(filtered_df: pd.DataFrame):
    st.markdown("### Dataset")
    search = st.text_input("Cari data", placeholder="Contoh: SURABAYA, 2025-06-01, 27.5", key="dataset_search")
    show_rows = st.selectbox("Jumlah baris", [10, 25, 50, 100], index=1, key="dataset_show_rows")

    table_df = filtered_df.copy()
    if search.strip():
        q = search.strip().upper()
        mask = pd.Series(False, index=table_df.index)
        for col in table_df.columns:
            mask = mask | table_df[col].astype(str).str.upper().str.contains(q, na=False)
        table_df = table_df[mask]

    kolom_tampil = ["tanggal", "daerah", "tn", "tx", "tavg", "rh_avg", "rr", "ss", "ff_x", "ddd_x", "ff_avg", "ddd_car"]
    kolom_tersedia = [c for c in kolom_tampil if c in table_df.columns]
    table_show = table_df[kolom_tersedia].head(show_rows).copy()
    if "tanggal" in table_show.columns:
        table_show["tanggal"] = table_show["tanggal"].dt.strftime("%Y-%m-%d")

    st.caption(f"Menampilkan {min(len(table_df), show_rows)} dari {len(table_df)} baris")
    st.dataframe(table_show, use_container_width=True, height=420)
    csv_data = table_df[kolom_tersedia].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv_data, file_name="bmkg_jatim_filtered.csv", mime="text/csv")


# =========================
# LOAD DATA
# =========================
try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## Dashboard BMKG")
st.sidebar.info("BY KELOMPOK 7:\n- Falissa Advisherlailillah Putri Esa \n- Ima Dwi Rahmania \n- Shofie Fadliya Rahma ")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
halaman = st.sidebar.radio(
    "Navigasi",
    ["Cuaca", "Curah Hujan", "Angin", "Dataset"],
    key="halaman",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Filter")

all_daerah_sb = sorted(df["daerah"].dropna().unique().tolist())
all_years_sb   = sorted(df["tahun"].dropna().unique().tolist())
min_date_sb    = df["tanggal"].min().date()
max_date_sb    = df["tanggal"].max().date()

daerah_filter = st.sidebar.multiselect(
    "Daerah", options=all_daerah_sb, default=all_daerah_sb, key="sb_daerah"
)
if not daerah_filter:
    daerah_filter = all_daerah_sb

mode_sb = st.sidebar.radio("Mode Waktu", ["Harian", "Bulanan", "Tahunan"], key="sb_mode")

filtered_df = df[df["daerah"].isin(daerah_filter)].copy()
year_ref_sb = None

if mode_sb == "Harian":
    date_range_sb = st.sidebar.date_input(
        "Rentang Tanggal",
        value=[min_date_sb, max_date_sb],
        min_value=min_date_sb,
        max_value=max_date_sb,
        key="sb_date_range",
    )
    if isinstance(date_range_sb, (list, tuple)) and len(date_range_sb) == 2:
        filtered_df = filtered_df[
            (filtered_df["tanggal"] >= pd.to_datetime(date_range_sb[0])) &
            (filtered_df["tanggal"] <= pd.to_datetime(date_range_sb[1]))
        ].copy()
    elif isinstance(date_range_sb, (list, tuple)) and len(date_range_sb) == 1:
        st.sidebar.warning("Pilih tanggal akhir untuk menerapkan filter.")

elif mode_sb == "Bulanan":
    year_sb = st.sidebar.selectbox("Tahun", options=all_years_sb, index=len(all_years_sb)-1, key="sb_year")
    months_sb = st.sidebar.multiselect("Bulan", options=MONTHS_ID, default=MONTHS_ID, key="sb_months")
    if not months_sb:
        months_sb = MONTHS_ID
    month_nums_sb = [MONTH_TO_NUM[m] for m in months_sb]
    filtered_df = filtered_df[
        (filtered_df["tahun"] == year_sb) &
        (filtered_df["bulan_num"].isin(month_nums_sb))
    ].copy()
    year_ref_sb = year_sb

else:
    years_sb = st.sidebar.multiselect("Tahun", options=all_years_sb, default=all_years_sb, key="sb_years")
    if not years_sb:
        years_sb = all_years_sb
    filtered_df = filtered_df[filtered_df["tahun"].isin(years_sb)].copy()
    year_ref_sb = years_sb

if filtered_df.empty:
    st.sidebar.error("Tidak ada data. Coba ubah filter.")
else:
    st.sidebar.caption(f"Data aktif: **{len(filtered_df):,}** baris")

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
# SUMMARY UMUM
# =========================
render_page_summary(df)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# PAGE ROUTING
# =========================
if halaman == "Cuaca":
    render_cuaca_page(filtered_df, mode_sb, year_ref_sb)
elif halaman == "Curah Hujan":
    render_hujan_page(filtered_df, mode_sb, year_ref_sb)
elif halaman == "Angin":
    render_angin_page(filtered_df, mode_sb, year_ref_sb)
else:
    render_dataset_page(filtered_df)