import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Tourism Data Visualization Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ---------- Load data ----------
@st.cache_data
def load_data():
    data = pd.read_csv("most-visited-countries-2024.csv")

    # Friendly column names for the dashboard
    rename_map = {
        "country": "Country",
        "MostVisited_NumOfArrivalsPredictive_Millions_2024": "Predicted Arrivals 2024 (millions)",
        "MostVisited_NumOfArrivals_Millions_2023": "Arrivals 2023 (millions)",
        "MostVisited_NumOfArrivals_Millions_2022": "Arrivals 2022 (millions)",
        "MostVisited_NumOfArrivals_WorldBank": "World Bank Arrivals (millions)",
        "MostVisited_DataYear_WorldBank": "World Bank Data Year",
    }
    data = data.rename(columns=rename_map)

    numeric_columns = [
        "Predicted Arrivals 2024 (millions)",
        "Arrivals 2023 (millions)",
        "Arrivals 2022 (millions)",
        "World Bank Arrivals (millions)",
        "World Bank Data Year",
    ]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    data["Country"] = data["Country"].astype(str).str.strip()
    data = data[data["Country"].ne("")].drop_duplicates(subset=["Country"])
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Dataset file not found. Put `most-visited-countries-2024.csv` "
        "in the same GitHub repository folder as `app.py`."
    )
    st.stop()

st.title("🌍 Tourism Data Visualization Dashboard")
st.write(
    "Explore international tourist arrivals by country. Use the sidebar filters; "
    "all charts and summary cards update from the same filtered data."
)

# Metrics that represent tourist arrivals (not the World Bank data year)
arrival_metrics = [
    "Predicted Arrivals 2024 (millions)",
    "Arrivals 2023 (millions)",
    "Arrivals 2022 (millions)",
    "World Bank Arrivals (millions)",
]
arrival_metrics = [c for c in arrival_metrics if c in df.columns]

# ---------- Sidebar filters ----------
st.sidebar.header("Dashboard Filters")

selected_countries = st.sidebar.multiselect(
    "Select countries",
    options=sorted(df["Country"].dropna().unique().tolist()),
    default=[],
    help="Leave empty to include all countries."
)

selected_metrics = st.sidebar.multiselect(
    "Select arrival metrics",
    options=arrival_metrics,
    default=[m for m in [
        "Predicted Arrivals 2024 (millions)",
        "Arrivals 2023 (millions)",
        "Arrivals 2022 (millions)",
    ] if m in arrival_metrics],
    help="The selected metrics are used across the charts."
)

top_n = st.sidebar.slider(
    "Number of countries to show in ranking",
    min_value=5,
    max_value=30,
    value=10,
    step=5
)

sort_metric = st.sidebar.selectbox(
    "Rank countries by",
    options=selected_metrics if selected_metrics else arrival_metrics,
    index=0 if (selected_metrics or arrival_metrics) else None
)

show_data_table = st.sidebar.checkbox("Show filtered data table", value=True)

# ---------- Apply filters once; all charts use this data ----------
filtered = df.copy()
if selected_countries:
    filtered = filtered[filtered["Country"].isin(selected_countries)]

if not selected_metrics:
    st.warning("Select at least one arrival metric in the sidebar to display charts.")
    st.stop()

# Exclude rows that do not have any selected metric values for charting
filtered_for_charts = filtered.dropna(subset=selected_metrics, how="all").copy()

if filtered_for_charts.empty:
    st.warning("No data is available for the selected filters.")
    st.stop()

# ---------- Summary cards ----------
total_countries = filtered["Country"].nunique()
valid_values = filtered_for_charts[selected_metrics].stack()
average_arrivals = valid_values.mean() if not valid_values.empty else 0
highest_country = "N/A"
highest_value = None
if sort_metric in filtered.columns:
    ranked = filtered.dropna(subset=[sort_metric]).sort_values(sort_metric, ascending=False)
    if not ranked.empty:
        highest_country = ranked.iloc[0]["Country"]
        highest_value = ranked.iloc[0][sort_metric]

c1, c2, c3 = st.columns(3)
c1.metric("Countries in current selection", f"{total_countries:,}")
c2.metric("Average selected arrival value", f"{average_arrivals:,.2f} million")
c3.metric(
    f"Top country by {sort_metric}",
    highest_country,
    f"{highest_value:,.2f} million" if pd.notna(highest_value) else None
)

st.divider()

# ---------- Chart 1: Country ranking ----------
st.subheader("1. Country-wise Tourist Arrivals")
ranked = filtered_for_charts.dropna(subset=[sort_metric]).sort_values(
    sort_metric, ascending=False
).head(top_n)

if not ranked.empty:
    fig1 = px.bar(
        ranked.sort_values(sort_metric, ascending=True),
        x=sort_metric,
        y="Country",
        orientation="h",
        title=f"Top {min(top_n, len(ranked))} Countries — {sort_metric}",
        labels={sort_metric: "Arrivals (millions)", "Country": "Country"},
        hover_data=selected_metrics
    )
    fig1.update_layout(height=500, yaxis_title="", xaxis_title="Tourist arrivals (millions)")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info(f"No values are available for {sort_metric} in this selection.")

# ---------- Chart 2: Compare selected metrics ----------
st.subheader("2. Compare Arrival Metrics")
long_df = filtered_for_charts.melt(
    id_vars=["Country"],
    value_vars=selected_metrics,
    var_name="Metric",
    value_name="Arrivals (millions)"
).dropna(subset=["Arrivals (millions)"])

if not long_df.empty:
    # Keep the selected countries if explicitly chosen; otherwise show the top countries
    # based on the ranking metric to keep the chart readable.
    if not selected_countries:
        top_countries = ranked["Country"].tolist()
        long_df = long_df[long_df["Country"].isin(top_countries)]
    fig2 = px.bar(
        long_df,
        x="Country",
        y="Arrivals (millions)",
        color="Metric",
        barmode="group",
        title="Tourist Arrivals by Country and Selected Metric",
        hover_data={"Arrivals (millions)": ":.2f"}
    )
    fig2.update_layout(height=500, xaxis_title="", yaxis_title="Arrivals (millions)")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Chart 3: Relationship between two selected metrics ----------
st.subheader("3. Compare Countries Across Two Metrics")
if len(selected_metrics) >= 2:
    x_metric = st.selectbox("X-axis metric", selected_metrics, index=0, key="x_metric")
    y_metric = st.selectbox(
        "Y-axis metric",
        selected_metrics,
        index=1 if len(selected_metrics) > 1 else 0,
        key="y_metric"
    )
    scatter_df = filtered_for_charts.dropna(subset=[x_metric, y_metric])
    if not scatter_df.empty:
        fig3 = px.scatter(
            scatter_df,
            x=x_metric,
            y=y_metric,
            hover_name="Country",
            size=(scatter_df[x_metric].clip(lower=0) + 0.1),
            title=f"{y_metric} vs {x_metric}",
            labels={
                x_metric: "Arrivals (millions)",
                y_metric: "Arrivals (millions)"
            }
        )
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("There are not enough rows with values for both selected metrics.")
else:
    st.info("Select at least two arrival metrics to display the comparison scatter plot.")

# ---------- Chart 4: Distribution ----------
st.subheader("4. Distribution of Tourist Arrivals")
distribution_metric = st.selectbox(
    "Metric for distribution chart",
    selected_metrics,
    index=0,
    key="distribution_metric"
)
distribution_df = filtered_for_charts.dropna(subset=[distribution_metric])
if not distribution_df.empty:
    fig4 = px.histogram(
        distribution_df,
        x=distribution_metric,
        nbins=20,
        title=f"Distribution of {distribution_metric}",
        labels={distribution_metric: "Arrivals (millions)"}
    )
    fig4.update_layout(height=400, yaxis_title="Number of countries")
    st.plotly_chart(fig4, use_container_width=True)

# ---------- Data table ----------
if show_data_table:
    st.subheader("Filtered Dataset")
    display_cols = ["Country"] + selected_metrics
    if "World Bank Data Year" in filtered.columns:
        display_cols.append("World Bank Data Year")
    st.dataframe(
        filtered[display_cols].sort_values("Country"),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Note: The 2024 arrivals field is predictive, while 2022 and 2023 are reported figures. "
    "World Bank arrival values may refer to different years by country; see the World Bank Data Year column."
)
