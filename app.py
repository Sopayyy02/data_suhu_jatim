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

    fig = px.box(
        filtered_df,
        x="daerah",
        y=parameter_col,
        color="daerah",
        template="plotly_dark",
        title=f"Distribusi {parameter_label}",
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
    fig.update_xaxes(tickangle=-20, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")
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
        years = st.multiselect(
            "Tahun",
            options=all_years,
            default=st.session_state[f"{prefix}_years"],
            key=f"{prefix}_years",
        )
        if not years:
            years = all_years

        date_range = st.date_input(
            "Rentang Tanggal",
            value=st.session_state[f"{prefix}_date_range"],
            min_value=min_date,
            max_value=max_date,
            key=f"{prefix}_date_range",
        )

        filtered = filtered[filtered["tahun"].isin(years)].copy()

        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date = pd.to_datetime(date_range[0])
            end_date = pd.to_datetime(date_range[1])
            filtered = filtered[
                (filtered["tanggal"] >= start_date) &
                (filtered["tanggal"] <= end_date)
            ].copy()

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

    return filtered, mode, active_params, main_param, selected_year_ref


def render_page_summary(df: pd.DataFrame):
    total_rows = len(df)
    total_daerah = df["daerah"].nunique()
    min_date_all = df["tanggal"].min().date()
    max_date_all = df["tanggal"].max().date()
    avg_tavg_all = safe_mean(get_series(df, "tavg"))

    st.markdown("### Ringkasan Dataset")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Jumlah Data", f"{total_rows:,}", f"Daerah: {total_daerah}")
    with c2:
        render_metric_card("Data Terlama", str(min_date_all), "Tanggal awal")
    with c3:
        render_metric_card("Data Terbaru", str(max_date_all), "Tanggal akhir")
    with c4:
        render_metric_card("Rata-rata TAVG", fmt_num(avg_tavg_all, "°C"), "Seluruh dataset")


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
# TABS
# =========================
tab_overview, tab_distribusi, tab_angin, tab_dataset = st.tabs(
    ["📊 Overview", "🌡️ Distribusi", "💨 Angin", "📁 Dataset"]
)

with tab_overview:
    st.markdown("### Overview BMKG")
    st.caption("Filter di bawah hanya mempengaruhi grafik pada tab ini.")

    ov_df, ov_mode, ov_params, ov_main_param, ov_year_ref = render_filter_box(
        df,
        prefix="overview",
        include_parameters=True
    )

    if ov_df.empty:
        st.warning("Data kosong. Coba ubah filter pada tab Overview.")
    else:
        ov_main_param_col = PARAMETER_OPTIONS[ov_main_param]
        ov_main_unit = PARAMETER_UNIT.get(ov_main_param_col, "")

        ov_avg_tn = safe_mean(get_series(ov_df, "tn"))
        ov_avg_tx = safe_mean(get_series(ov_df, "tx"))
        ov_avg_tavg = safe_mean(get_series(ov_df, "tavg"))

        top_daerah = (
            ov_df.groupby("daerah")["tavg"]
            .mean()
            .sort_values(ascending=False)
        )
        if not top_daerah.empty:
            daerah_terpanas = top_daerah.index[0]
            daerah_terdingin = top_daerah.index[-1]
        else:
            daerah_terpanas = "-"
            daerah_terdingin = "-"

        latest_date = ov_df["tanggal"].max().date()
        total_data = len(ov_df)
        avg_param = safe_mean(get_series(ov_df, ov_main_param_col))
        min_param = safe_min(get_series(ov_df, ov_main_param_col))
        max_param = safe_max(get_series(ov_df, ov_main_param_col))

        st.markdown("#### Ringkasan Cepat")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_metric_card("Jumlah Data", f"{total_data:,}", f"Update terakhir: {latest_date}")
        with c2:
            render_metric_card(
                f"Rata-rata {ov_main_param}",
                fmt_num(avg_param, ov_main_unit),
                f"Min: {fmt_num(min_param, ov_main_unit)} | Max: {fmt_num(max_param, ov_main_unit)}"
            )
        with c3:
            render_metric_card("Daerah Terpanas", daerah_terpanas, "Rata-rata TAVG tertinggi")
        with c4:
            render_metric_card("Daerah Terdingin", daerah_terdingin, "Rata-rata TAVG terendah")

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns([1.6, 1])
        with col_a:
            render_parameter_trends(
                filtered_df=ov_df,
                mode=ov_mode,
                selected_parameters=ov_params,
                selected_year_ref=ov_year_ref,
                section_key="overview_trend"
            )

        with col_b:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Insight Otomatis")
            st.write(f"• Mode aktif: **{ov_mode}**")
            st.write(f"• Parameter utama: **{ov_main_param}**")
            st.write(f"• Parameter lain: **{', '.join([p for p in ov_params if p != ov_main_param]) or '-'}**")
            st.write(f"• Data paling baru pada **{latest_date}**")
            st.write(f"• Rata-rata **TN**: **{fmt_num(ov_avg_tn, '°C')}**")
            st.write(f"• Rata-rata **TX**: **{fmt_num(ov_avg_tx, '°C')}**")
            st.write(f"• Rata-rata **TAVG**: **{fmt_num(ov_avg_tavg, '°C')}**")
            st.write(f"• Daerah terpanas: **{daerah_terpanas}**")
            st.write(f"• Daerah terdingin: **{daerah_terdingin}**")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_c, col_d = st.columns([1, 1])
        with col_c:
            comp_fig = district_comparison_chart(ov_df, ov_main_param_col, ov_main_param)
            if comp_fig is not None:
                st.plotly_chart(
                    comp_fig,
                    use_container_width=True,
                    key=f"overview_comparison_{ov_main_param_col}"
                )

        with col_d:
            heatmap_fig = heatmap_chart(ov_df, ov_main_param_col, ov_main_param)
            if heatmap_fig is not None:
                st.plotly_chart(
                    heatmap_fig,
                    use_container_width=True,
                    key=f"overview_heatmap_{ov_main_param_col}"
                )

with tab_distribusi:
    st.markdown("### Distribusi Data")
    st.caption("Filter di bawah hanya mempengaruhi grafik pada tab ini.")

    dist_df, dist_mode, dist_params, dist_main_param, dist_year_ref = render_filter_box(
        df,
        prefix="distribution",
        include_parameters=True
    )

    if dist_df.empty:
        st.warning("Data kosong. Coba ubah filter pada tab Distribusi.")
    else:
        dist_main_param_col = PARAMETER_OPTIONS[dist_main_param]
        dist_main_unit = PARAMETER_UNIT.get(dist_main_param_col, "")

        dist_avg = safe_mean(get_series(dist_df, dist_main_param_col))
        dist_min = safe_min(get_series(dist_df, dist_main_param_col))
        dist_max = safe_max(get_series(dist_df, dist_main_param_col))

        col1, col2 = st.columns([1.35, 1])

        with col1:
            render_parameter_distributions(
                filtered_df=dist_df,
                selected_parameters=dist_params,
                section_key="distribution_box"
            )

        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### Statistik Parameter")
            st.write(f"• Parameter utama: **{dist_main_param}**")
            st.write(f"• Mode aktif: **{dist_mode}**")
            st.write(f"• Rata-rata: **{fmt_num(dist_avg, dist_main_unit)}**")
            st.write(f"• Nilai minimum: **{fmt_num(dist_min, dist_main_unit)}**")
            st.write(f"• Nilai maksimum: **{fmt_num(dist_max, dist_main_unit)}**")
            st.write(f"• Jumlah daerah: **{dist_df['daerah'].nunique()}**")
            st.write(f"• Jumlah tahun: **{dist_df['tahun'].nunique()}**")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        dist_trend_fig = make_trend_chart(dist_df, dist_mode, dist_main_param_col, dist_main_param, dist_year_ref)
        if dist_trend_fig is not None:
            st.plotly_chart(
                dist_trend_fig,
                use_container_width=True,
                key=f"distribution_trend_{dist_main_param_col}"
            )

with tab_angin:
    st.markdown("### Visualisasi Angin")
    st.caption("Filter di bawah hanya mempengaruhi grafik pada tab ini.")

    wind_df, wind_mode, _, wind_main_param, wind_year_ref = render_filter_box(
        df,
        prefix="wind",
        include_parameters=False
    )

    if wind_df.empty:
        st.warning("Data kosong. Coba ubah filter pada tab Angin.")
    else:
        col1, col2 = st.columns([1.25, 1])

        with col1:
            wind_fig = wind_chart(wind_df)
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
            st.write(f"• Mode aktif: **{wind_mode}**")
            st.write(f"• Rata-rata kecepatan angin maksimum: **{fmt_num(safe_mean(get_series(wind_df, 'ff_x')))}**")
            st.write(f"• Rata-rata kecepatan angin: **{fmt_num(safe_mean(get_series(wind_df, 'ff_avg')))}**")
            st.write(f"• Kategori arah dominan: **{wind_df['ddd_car'].nunique() if 'ddd_car' in wind_df.columns else 0}**")
            if "ddd_x" in wind_df.columns:
                st.write(f"• Derajat angin minimum: **{fmt_num(safe_min(get_series(wind_df, 'ddd_x')))}**")
                st.write(f"• Derajat angin maksimum: **{fmt_num(safe_max(get_series(wind_df, 'ddd_x')))}**")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        wind_speed_fig = wind_speed_chart(wind_df)
        if wind_speed_fig is not None:
            st.plotly_chart(
                wind_speed_fig,
                use_container_width=True,
                key="wind_speed_bar"
            )

with tab_dataset:
    st.markdown("### Dataset")
    st.caption("Filter di bawah hanya mempengaruhi tabel pada tab ini.")

    data_df, data_mode, _, data_main_param, data_year_ref = render_filter_box(
        df,
        prefix="dataset",
        include_parameters=False
    )

    search = st.text_input(
        "Cari data",
        placeholder="Contoh: SURABAYA, 2026-06-03, 27.5",
        key="dataset_search"
    )
    show_rows = st.selectbox(
        "Jumlah baris yang ditampilkan",
        [10, 25, 50, 100],
        index=1,
        key="dataset_show_rows"
    )

    table_df = data_df.copy()

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

    table_show = table_df[kolom_tersedia].head(show_rows).copy()
    if "tanggal" in table_show.columns:
        table_show["tanggal"] = table_show["tanggal"].dt.strftime("%Y-%m-%d")

    st.caption(f"Menampilkan {min(len(table_df), show_rows)} dari {len(table_df)} baris")
    st.write(f"Mode filter tab ini: **{data_mode}**")
    if data_mode == "Bulanan":
        st.write(f"Tahun yang dipilih: **{data_year_ref}**")
    elif data_mode == "Tahunan":
        st.write(f"Tahun yang dipilih: **{data_year_ref}**")

    st.dataframe(
        table_show,
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