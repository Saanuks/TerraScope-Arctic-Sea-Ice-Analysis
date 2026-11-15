
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress

# CONFIGURATION
st.set_page_config(
    page_title="TerraScope | Earth Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PROFESSIONAL DESIGN
st.markdown("""
<style>

.stApp {
    background-color: #071426;
    color: #EAF4FF;
}

[data-testid="stSidebar"] {
    background-color: #10243D;
}

h1 {
    color: #43D9E8 !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}

h2 {
    color: #43D9E8 !important;
    font-size: 27px !important;
}

h3 {
    color: #FFFFFF !important;
}

[data-testid="stMetric"] {
    background: #132D49;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #234B6B;
}

[data-testid="stMetricValue"] {
    color: #43D9E8;
    font-size: 30px;
}

.stButton button {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# DATA SOURCE
URL = (
    "https://noaadata.apps.nsidc.org/"
    "NOAA/G02135/north/monthly/data/"
    "N_09_extent_v4.0.csv"
)


@st.cache_data(ttl=3600)
def load_data():

    data = pd.read_csv(URL, comment="#")

    data.columns = data.columns.str.strip().str.lower()

    data["year"] = pd.to_numeric(
        data["year"], errors="coerce"
    )

    data["mo"] = pd.to_numeric(
        data["mo"], errors="coerce"
    )

    data["extent"] = pd.to_numeric(
        data["extent"], errors="coerce"
    )

    data = data[data["mo"] == 9]

    data = data.dropna(
        subset=["year", "extent"]
    )

    return data.sort_values("year")


# LOAD DATA
try:

    df = load_data()

except Exception as error:

    st.error(f"Unable to retrieve NSIDC data: {error}")
    st.stop()


# SIDEBAR
st.sidebar.title("🌍 TERRASCOPE")

st.sidebar.caption("EARTH SYSTEM INTELLIGENCE")

st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Trend Explorer",
        "Year Comparison",
        "Statistical Lab",
        "Data Explorer",
        "About"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Display Settings")

show_trend = st.sidebar.toggle(
    "Show trend line",
    value=True
)

show_markers = st.sidebar.toggle(
    "Show data markers",
    value=True
)

show_grid = st.sidebar.toggle(
    "Show chart grid",
    value=True
)

st.sidebar.caption(
    "Data: NSIDC Sea Ice Index Version 4.0"
)


# ANALYSIS
years = df["year"].to_numpy()

extent = df["extent"].to_numpy()

slope, intercept, r, p, stderr = linregress(
    years, extent
)

trend = slope * years + intercept

min_index = np.argmin(extent)

max_index = np.argmax(extent)

# GLOBAL HEADER
st.title("TERRASCOPE")

st.markdown(
    "### Earth System Trend Detective"
)

st.caption(
    "Satellite-based Arctic Sea Ice Monitoring and Analysis"
)

st.divider()


# COMMON CHART FUNCTION
def create_chart(data):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["year"],
            y=data["extent"],
            mode="lines+markers" if show_markers else "lines",
            name="Observed extent",
            line=dict(width=3, color="#43D9E8")
        )
    )

    if show_trend:

        x = data["year"].to_numpy()

        y = data["extent"].to_numpy()

        m, b, _, _, _ = linregress(x, y)

        fig.add_trace(
            go.Scatter(
                x=x,
                y=m*x+b,
                mode="lines",
                name="Linear trend",
                line=dict(
                    color="#FFB454",
                    width=3,
                    dash="dash"
                )
            )
        )

    fig.update_layout(
        template="plotly_dark",
        height=480,
        paper_bgcolor="#071426",
        plot_bgcolor="#10243D",
        xaxis_title="Year",
        yaxis_title="Extent (million km²)",
        font=dict(size=14),
        margin=dict(l=30, r=30, t=30, b=30)
    )

    fig.update_xaxes(showgrid=show_grid)
    fig.update_yaxes(showgrid=show_grid)

    return fig


# PAGE 1: OVERVIEW
if page == "Overview":

    st.subheader("Arctic Sea Ice Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Observation years",
        f"{len(df)}"
    )

    c2.metric(
    "Annual trend",
    f"{slope:.4f} million km²/year"
)

    c3.metric(
        "Highest extent",
        f"{extent[max_index]:.2f}",
        f"{int(years[max_index])}"
    )

    c4.metric(
        "Lowest extent",
        f"{extent[min_index]:.2f}",
        f"{int(years[min_index])}"
    )

    st.divider()

    st.subheader("Historical Arctic Sea Ice Trend")

    st.plotly_chart(
        create_chart(df),
        use_container_width=True
    )

    st.subheader("Scientific Highlights")

    a, b = st.columns(2)

    with a:

        st.info(
            f"Decadal linear change: "
            f"{slope*10:.4f} million km²"
        )

    with b:

        st.info(
            f"Regression R²: {r**2:.4f}"
        )

    st.caption(
        "Source: NSIDC Sea Ice Index Version 4.0"
    )


# PAGE 2: TREND EXPLORER
elif page == "Trend Explorer":

    st.subheader("Interactive Trend Explorer")

    start = st.selectbox(
        "Starting year",
        years.astype(int).tolist(),
        index=0
    )

    end = st.selectbox(
        "Ending year",
        years.astype(int).tolist(),
        index=len(years)-1
    )

    if start >= end:

        st.warning("Select an ending year after the starting year.")

    else:

        filtered = df[
            (df["year"] >= start) &
            (df["year"] <= end)
        ]

        st.plotly_chart(
            create_chart(filtered),
            use_container_width=True
        )

        st.write(
            f"Observations in selected period: {len(filtered)}"
        )


# PAGE 3: YEAR COMPARISON
elif page == "Year Comparison":

    st.subheader("Compare Selected Years")

    selected_years = st.multiselect(
        "Choose years to compare",
        years.astype(int).tolist(),
        default=[
            int(years[0]),
            int(years[len(years)//2]),
            int(years[-1])
        ]
    )

    comparison = df[
        df["year"].isin(selected_years)
    ]

    if not comparison.empty:

        fig = px.bar(
            comparison,
            x="year",
            y="extent",
            text="extent",
            title="September Sea Ice Extent Comparison"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#071426",
            plot_bgcolor="#10243D",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            comparison[
                ["year", "extent"]
            ],
            use_container_width=True,
            hide_index=True
        )


# PAGE 4: STATISTICAL LAB
elif page == "Statistical Lab":

    st.subheader("Statistical Analysis Laboratory")

    st.write(
        "Linear regression of September Arctic sea-ice extent."
    )

    a, b, c = st.columns(3)

    a.metric("Slope", f"{slope:.5f}")

    b.metric("R-squared", f"{r**2:.4f}")

    c.metric("P-value", f"{p:.6g}")

    st.divider()

    st.subheader("Statistical Interpretation")

    if p < 0.05:

        st.success(
            "The linear trend is statistically significant "
            "at the 0.05 level."
        )

    else:

        st.warning(
            "The linear trend is not statistically significant "
            "at the 0.05 level."
        )

    st.write(
        f"Estimated decadal change: {slope*10:.4f} "
        "million km² per decade."
    )

    st.write(
        f"Standard error of slope: {stderr:.6f}"
    )

    st.write(
        "The regression describes a linear trend. "
        "It does not establish causation."
    )


# PAGE 5: DATA EXPLORER
elif page == "Data Explorer":

    st.subheader("September Observation Database")

    search_year = st.text_input(
        "Search year"
    )

    display_df = df.copy()

    if search_year.isdigit():

        display_df = display_df[
            display_df["year"] == int(search_year)
        ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    csv = display_df.to_csv(index=False)

    st.download_button(
        "Download CSV Dataset",
        csv,
        "terrascope_arctic_data.csv",
        "text/csv"
    )


# PAGE 6: ABOUT
elif page == "About":

    st.subheader("About TerraScope")

    st.write("""
    TerraScope is an Earth observation data analysis project
    investigating long-term changes in Arctic September
    sea-ice extent.

    The project uses historical satellite-derived observations
    to investigate climate trends.
    """)

    st.markdown("### Research Question")

    st.write(
        "How has September Arctic sea-ice extent changed "
        "during the satellite observation era?"
    )

    st.markdown("### Scientific Methodology")

    st.write("""
    1. Retrieve September observations.
    2. Clean and organize the time series.
    3. Visualize historical changes.
    4. Estimate a linear trend.
    5. Evaluate statistical significance.
    """)

    st.markdown("### Data Source")

    st.write(
        "NSIDC Sea Ice Index Version 4.0"
    )

    st.link_button(
        "Visit NSIDC Data Archive",
        "https://nsidc.org/data/g02135/versions/4"
    )

    st.markdown("### Project Team")

    st.write("TERRASCOPE | CELL NO. 118")

    st.caption(
        "NASA Space Apps Challenge"
    )


st.sidebar.divider()

st.sidebar.caption(
    "TERRASCOPE v2.0 | CELL 118"
)
