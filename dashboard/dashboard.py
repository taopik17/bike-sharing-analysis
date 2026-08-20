from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================
DATA_PATH = Path(__file__).parent / "main_data.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["dteday"])
    return df


df = load_data()


# =========================================================
# HEADER
# =========================================================
st.title("🚲 Bike Sharing Analysis Dashboard")
st.caption(
    "Analysis of Capital Bikeshare usage in Washington D.C. during 2011–2012"
)

st.markdown(
    """
    Dashboard ini digunakan untuk menganalisis **pola waktu penggunaan sepeda**
    serta **pengaruh kondisi cuaca terhadap permintaan penyewaan sepeda**.
    """
)


# =========================================================
# SIDEBAR FILTER
# =========================================================
with st.sidebar:
    st.header("🔎 Filters")

    years = sorted(df["year"].unique().tolist())
    selected_years = st.multiselect(
        "Year",
        years,
        default=years
    )

    seasons = [
        season
        for season in ["Spring", "Summer", "Fall", "Winter"]
        if season in df["season_label"].unique()
    ]

    selected_seasons = st.multiselect(
        "Season",
        seasons,
        default=seasons
    )

    day_types = ["Working day", "Non-working day"]

    selected_day_types = st.multiselect(
        "Day Type",
        day_types,
        default=day_types
    )


# =========================================================
# FILTER DATA
# =========================================================
filtered = df[
    df["year"].isin(selected_years)
    & df["season_label"].isin(selected_seasons)
    & df["workingday_label"].isin(selected_day_types)
].copy()


if filtered.empty:
    st.warning(
        "Tidak ada data yang sesuai dengan kombinasi filter yang dipilih."
    )
    st.stop()


# =========================================================
# KPI
# =========================================================
peak_hour = int(
    filtered.groupby("hr")["cnt"]
    .mean()
    .idxmax()
)

registered_share = (
    filtered["registered"].sum()
    / filtered["cnt"].sum()
    * 100
)

st.subheader("📌 Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Rentals",
    f"{filtered['cnt'].sum():,.0f}"
)

c2.metric(
    "Avg Rentals / Hour",
    f"{filtered['cnt'].mean():,.1f}"
)

c3.metric(
    "Peak Hour",
    f"{peak_hour:02d}:00"
)

c4.metric(
    "Registered User Share",
    f"{registered_share:.1f}%"
)

st.divider()


# =========================================================
# BUSINESS QUESTION 1
# =========================================================
st.subheader(
    "❓ Business Question 1 — "
    "When do bike rentals reach their peak on working and non-working days?"
)

st.caption(
    "Tujuan analisis: mengidentifikasi jam dengan permintaan tertinggi "
    "agar operator dapat menentukan waktu yang tepat untuk melakukan "
    "bike rebalancing dan memastikan ketersediaan sepeda."
)


hourly = (
    filtered
    .groupby(
        ["workingday_label", "hr"],
        as_index=False
    )["cnt"]
    .mean()
)


fig1, ax1 = plt.subplots(figsize=(11, 5))

for label, grp in hourly.groupby("workingday_label"):
    ax1.plot(
        grp["hr"],
        grp["cnt"],
        marker="o",
        linewidth=2,
        label=label
    )

ax1.set_title(
    "Average Hourly Bike Rentals by Day Type",
    fontsize=14
)

ax1.set_xlabel("Hour of Day")
ax1.set_ylabel("Average Rentals per Hour")
ax1.set_xticks(range(24))
ax1.legend(title="Day Type")
ax1.grid(axis="y", alpha=0.3)

st.pyplot(fig1, width="stretch")

plt.close(fig1)


# Peak hour table
peak_table = hourly.loc[
    hourly
    .groupby("workingday_label")["cnt"]
    .idxmax()
].copy()

peak_table["avg_rentals"] = peak_table["cnt"].round(2)

peak_table = peak_table[
    ["workingday_label", "hr", "avg_rentals"]
]

peak_table.columns = [
    "Day Type",
    "Peak Hour",
    "Average Rentals"
]

st.dataframe(
    peak_table,
    hide_index=True,
    width="stretch"
)


# Dynamic insight
insight_q1 = []

for _, row in peak_table.iterrows():
    insight_q1.append(
        f"**{row['Day Type']}** mencapai puncak sekitar "
        f"**pukul {int(row['Peak Hour']):02d}:00** "
        f"dengan rata-rata **{row['Average Rentals']:.2f} penyewaan/jam**."
    )

st.info(
    "💡 **Insight:**  \n" +
    "  \n".join(insight_q1)
)

st.markdown(
    """
    **Interpretasi:**  
    Perbedaan pola antara hari kerja dan hari non-kerja menunjukkan bahwa
    kebutuhan sepeda dipengaruhi oleh tujuan perjalanan. Pada hari kerja,
    pola permintaan cenderung berkaitan dengan aktivitas komuter,
    sedangkan hari non-kerja lebih mencerminkan aktivitas rekreasi.
    """
)

st.divider()


# =========================================================
# BUSINESS QUESTION 2
# =========================================================
st.subheader(
    "❓ Business Question 2 — "
    "How does weather affect average hourly bike rental demand?"
)

st.caption(
    "Tujuan analisis: mengetahui perubahan tingkat permintaan berdasarkan "
    "kondisi cuaca sehingga operator dapat menyesuaikan kapasitas dan "
    "operasional layanan."
)


weather_order = [
    "Clear / Partly Cloudy",
    "Mist / Cloudy",
    "Light Rain / Snow",
    "Heavy Rain / Snow / Fog"
]


weather = (
    filtered
    .groupby(
        "weather_label",
        as_index=False
    )["cnt"]
    .mean()
)

weather["weather_label"] = pd.Categorical(
    weather["weather_label"],
    categories=weather_order,
    ordered=True
)

weather = weather.sort_values("weather_label")


fig2, ax2 = plt.subplots(figsize=(10, 5))

bars = ax2.bar(
    weather["weather_label"].astype(str),
    weather["cnt"]
)

ax2.set_title(
    "Average Hourly Bike Rentals by Weather Condition",
    fontsize=14
)

ax2.set_xlabel("Weather Condition")
ax2.set_ylabel("Average Rentals per Hour")
ax2.tick_params(axis="x", rotation=15)
ax2.grid(axis="y", alpha=0.3)


# Label nilai di atas bar
for bar in bars:
    height = bar.get_height()

    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.1f}",
        ha="center",
        va="bottom"
    )


st.pyplot(fig2, width="stretch")

plt.close(fig2)


# Dynamic weather insight
weather_valid = weather.dropna(subset=["cnt"]).copy()

if not weather_valid.empty:

    highest_weather = weather_valid.loc[
        weather_valid["cnt"].idxmax()
    ]

    lowest_weather = weather_valid.loc[
        weather_valid["cnt"].idxmin()
    ]

    reduction = (
        (highest_weather["cnt"] - lowest_weather["cnt"])
        / highest_weather["cnt"]
        * 100
    )

    st.info(
        f"💡 **Insight:** Permintaan tertinggi terjadi pada kondisi "
        f"**{highest_weather['weather_label']}** dengan rata-rata "
        f"**{highest_weather['cnt']:.2f} penyewaan/jam**. "
        f"Permintaan terendah terjadi pada kondisi "
        f"**{lowest_weather['weather_label']}** dengan rata-rata "
        f"**{lowest_weather['cnt']:.2f} penyewaan/jam**, "
        f"atau sekitar **{reduction:.1f}% lebih rendah**."
    )


st.markdown(
    """
    **Interpretasi:**  
    Kondisi cuaca memiliki hubungan yang jelas dengan tingkat penggunaan
    layanan bike sharing. Semakin tidak nyaman kondisi cuaca,
    permintaan cenderung semakin rendah.
    """
)

st.divider()


# =========================================================
# ADVANCED ANALYSIS
# =========================================================
st.subheader(
    "📊 Advanced Analysis — Operational Time Band Grouping"
)

st.caption(
    "Teknik analisis lanjutan menggunakan **manual grouping/binning** "
    "untuk mengelompokkan jam menjadi beberapa periode operasional. "
    "Tujuannya adalah mempermudah operator menentukan prioritas kapasitas "
    "berdasarkan kelompok waktu."
)


time_order = [
    "Early morning (00-05)",
    "Morning (06-09)",
    "Midday (10-15)",
    "Evening peak (16-19)",
    "Night (20-23)"
]


time_band = (
    filtered
    .groupby(
        ["time_band", "workingday_label"],
        as_index=False,
        observed=True
    )["cnt"]
    .mean()
)


time_band["time_band"] = pd.Categorical(
    time_band["time_band"],
    categories=time_order,
    ordered=True
)

time_band = time_band.sort_values("time_band")


pivot_time = time_band.pivot(
    index="time_band",
    columns="workingday_label",
    values="cnt"
)


fig3, ax3 = plt.subplots(figsize=(11, 5))

pivot_time.plot(
    kind="bar",
    ax=ax3
)

ax3.set_title(
    "Average Rentals by Operational Time Band",
    fontsize=14
)

ax3.set_xlabel("Operational Time Band")
ax3.set_ylabel("Average Rentals per Hour")
ax3.tick_params(axis="x", rotation=15)
ax3.legend(title="Day Type")
ax3.grid(axis="y", alpha=0.3)

st.pyplot(fig3, width="stretch")

plt.close(fig3)


# Advanced analysis insight
if not time_band.empty:

    top_band = time_band.loc[
        time_band["cnt"].idxmax()
    ]

    st.success(
        f"📌 **Advanced Analysis Insight:** Kombinasi periode dengan "
        f"rata-rata permintaan tertinggi adalah "
        f"**{top_band['time_band']} — {top_band['workingday_label']}**, "
        f"dengan sekitar **{top_band['cnt']:.2f} penyewaan/jam**."
    )


st.divider()


# =========================================================
# CONCLUSION & RECOMMENDATION
# =========================================================
st.subheader("🎯 Conclusion & Recommendation")


with st.expander(
    "Lihat Kesimpulan dan Rekomendasi",
    expanded=True
):

    st.markdown(
        """
        ### Kesimpulan

        **1. Pola waktu penggunaan**

        Pola penyewaan sepeda berbeda antara hari kerja dan hari
        non-kerja. Hari kerja memperlihatkan pola yang berkaitan erat
        dengan aktivitas komuter, sementara hari non-kerja memiliki
        pola penggunaan yang lebih terkonsentrasi pada aktivitas siang
        hingga sore hari.

        **2. Pengaruh kondisi cuaca**

        Kondisi cuaca memiliki hubungan yang kuat dengan tingkat
        permintaan. Cuaca cerah atau relatif baik menghasilkan jumlah
        penyewaan yang lebih tinggi dibandingkan kondisi hujan atau
        salju.

        ### Action Items

        - **Bike rebalancing:** lakukan redistribusi sepeda sebelum
          periode dengan permintaan tertinggi.

        - **Working day:** prioritaskan kesiapan sepeda menjelang
          periode perjalanan komuter.

        - **Non-working day:** tingkatkan ketersediaan sepeda pada
          periode siang hingga sore.

        - **Weather-based operation:** gunakan informasi prakiraan cuaca
          sebagai salah satu dasar untuk menyesuaikan kapasitas layanan.

        - **Low-demand weather:** pada kondisi hujan atau salju,
          kapasitas operasional dapat dikurangi secara proporsional
          dengan tetap menjaga minimum service availability.
        """
    )


# =========================================================
# DATA PREVIEW
# =========================================================
with st.expander("📄 View Filtered Data"):
    st.dataframe(
        filtered,
        hide_index=True,
        width="stretch"
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "Dataset: Bike Sharing Dataset — Capital Bikeshare, Washington D.C. "
    "| Period: 2011–2012"
)