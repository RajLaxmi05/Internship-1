import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



# PAGE CONFIG
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="India Weather",
    page_icon="🌦️",
    # Make the content take up the width of the page:
    layout="wide",
)

st.markdown(
    """
    <h1 style='max-width:350px; font-size:40px;'>India Weather</h1>
    <p>Let's explore the 
    <a href='https://github.com/RajLaxmi05/Internship-1/tree/main/cleaned_data' target='_blank'>
    India Historical Weather dataset
    </a>!</p>
    """,
    unsafe_allow_html=True
)

""  # Add a little vertical space. 
""


# LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("final_dataset.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()


# SIDEBAR FILTERS
st.sidebar.header("🔍 Filters")

city = st.sidebar.selectbox(
    "Select City",
    sorted(df["city"].unique())
)

# Extract year and month
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

selected_year = st.sidebar.selectbox(
    "Select Year",
    sorted(df["year"].unique())
)


year_data = df[
    (df["year"] == selected_year) &
    (df["city"] == city)
].copy()


# --- Weather classification ---
def classify_weather(row):
    prcp = row["prcp"]
    tavg = row["tavg"]

    if prcp > 10:
        return "rain"
    elif prcp > 0:
        return "drizzle"
    else:
        if tavg <= 15:
            return "fog"
        else:
            return "sun"

year_data["weather"] = year_data.apply(classify_weather, axis=1)

weather_icons = {
    "sun": "☀️",
    "rain": "💧",
    "fog": "😶‍🌫️",
    "drizzle": "🌧️",
}

# KPI ROW
st.markdown(
    f"<div style='font-size:27px; font-weight:300;'>{selected_year} Summary</div>",
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Max temperature (°C)", f"{year_data['tmax'].max():.1f}°C")
col2.metric("Min temperature (°C)", f"{year_data['tmin'].min():.1f}°C")
col3.metric("Max precipitation (mm)", f"{year_data['prcp'].max():.1f}mm")
col4.metric("Min precipitation (mm)", f"{year_data['prcp'].min():.1f}mm")

weather_counts = year_data["weather"].value_counts()

most_common = weather_counts.idxmax()
least_common = weather_counts.tail(1).index[0]

col5.metric(
    "Most common weather",
    f"{weather_icons[most_common]} {most_common.upper()}"
)

col6.metric(
    "Least common weather",
    f"{weather_icons[least_common]} {least_common.upper()}"
)


""  # Add a little vertical space. Same as st.write("").
""


# charts


# Temperature Trends Across Years
cols = st.columns([3, 1])


with cols[0].container(border=True, height="stretch"):
    st.markdown(
    f"<div style='font-size:22px; font-weight:300;'>Temperature Trends Across Years — {city}</div>",
    unsafe_allow_html=True
    )

    # Filter selected city
    city_data = df[df["city"] == city].copy()

    # Create day-of-year column (aligns Jan–Dec)
    city_data["day_of_year"] = city_data["date"].dt.dayofyear
    city_data["year"] = city_data["date"].dt.year
    city_data["month_day"] = city_data["date"].dt.strftime("%b %d")

    # Plot
    fig = px.line(
    city_data,
    x="day_of_year",
    y="tavg",
    color="year",
    labels={
        "day_of_year": "Date",
        "tavg": "Temperature (°C)",
        "year": "Year"
    },
    hover_data={
        "day_of_year": False,  # hides 172
        "month_day": True,     # shows Jun 21
        "tavg": ":.1f",
        "year": True
    }
    )

    fig.update_traces(line=dict(width=1))

    fig.update_layout(
        height=350,
        margin=dict(l=40, r=20, t=20, b=40),
        legend=dict(
        font=dict(color="grey"),
        title_font=dict(color="grey")
    ),
        legend_title_text="Year",
        xaxis=dict(
            tickmode="array",
            tickvals=[1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335],
            ticktext=[
                "Jan 01", "Feb 01", "Mar 01", "Apr 01", "May 01", "Jun 01",
                "Jul 01", "Aug 01", "Sep 01", "Oct 01", "Nov 01", "Dec 01"
            ],
            title_font=dict(color="grey"),
            tickfont=dict(color="grey")
        ),
        yaxis=dict(
        title_font=dict(color="grey"),
        tickfont=dict(color="grey")
        )
    )

    st.plotly_chart(fig, use_container_width=True)


# Weather Stations Map
with cols[1].container(border=True, height="stretch"):

    st.markdown(
    f"<div style='font-size:22px; font-weight:300;'>Weather Stations Map - {selected_year}</div>",
    unsafe_allow_html=True
    )

    # Load station geolocation data
    geo_df = pd.read_csv("cleaned_data/station_geolocation.csv")
   
    merged_df = df.merge(
        geo_df,
        left_on="city",
        right_on="location_name",
        how="left"
    )

    # Filter by year
    year_df = merged_df[merged_df["date"].dt.year == selected_year]

    # Aggregate rainfall by city
    map_df = (
        year_df
        .groupby(["city", "latitude", "longitude"], as_index=False)
        .agg(avg_prcp=("prcp", "mean"))
    )

    # Plot map
    fig = px.scatter_mapbox(
        map_df,
        lat="latitude",
        lon="longitude",
        size="avg_prcp",
        color="city",
        hover_name="city",
        hover_data={"avg_prcp": ":.2f"},   
        zoom=4,
        height=350,
        labels={"avg_prcp": "Avg Prcp(mm)"}
    )

    fig.update_traces(marker=dict(size=12))

    fig.update_layout(
        mapbox_style="open-street-map",
        showlegend=False,   
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)


cols = st.columns(2)


# Average Temperature per City
with cols[0].container(border=True, height="stretch"):

    st.markdown(
        f"<div style='font-size:22px; font-weight:300;'>"
        f"Average Temperature per City — {selected_year}"
        f"</div>",
        unsafe_allow_html=True
    )

    avg_temp_city = (
        year_df
        .groupby("city", as_index=False)["tavg"]
        .mean()
        .sort_values("tavg", ascending=False)
    )

    fig = px.bar(
        avg_temp_city,
        x="city",
        y="tavg",
        color="city",
        labels={
            "city": "City",
            "tavg": "Average Temperature (°C)"
        },
        hover_data={
            "tavg": ":.2f"
        }
    )

    fig.update_layout(
        height=350,
        xaxis_tickangle=0,
        showlegend=False, 
        xaxis_title_font=dict(color="grey"),
        yaxis_title_font=dict(color="grey"),
        xaxis_tickfont=dict(color="grey"),
        yaxis_tickfont=dict(color="grey"),
        margin=dict(l=40, r=20, t=20, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)


# Monthly Precipitation Distribution 
with cols[1].container(border=True, height="stretch"):
    
    st.markdown(
    f"<div style='font-size:22px; font-weight:300;'>Monthly Precipitation Distribution — {city}</div>",
    unsafe_allow_html=True
    )

    # Filter city
    year_data = df[df["city"] == city].copy()

    # Extract year & month
    year_data["year"] = year_data["date"].dt.year.astype(str)
    year_data["month_name"] = year_data["date"].dt.strftime("%b")
    year_data["month_num"] = year_data["date"].dt.month

    # Aggregate precipitation
    monthly_prcp = (
        year_data
        .groupby(["year", "month_name", "month_num"], as_index=False)["prcp"]
        .sum()
        .sort_values(["month_num", "year"])
    )

    # Stacked bar chart
    fig = px.bar(
        monthly_prcp,
        x="month_name",
        y="prcp",
        color="year",                 # legend = year
        barmode="stack",
        category_orders={
        "year": sorted(monthly_prcp["year"].unique())  # ascending legend
        },
        labels={
            "month_name": "Month",
            "prcp": "Precipitation (mm)",
            "year": "Year"
        }
    )

    # Styling
    fig.update_layout(
        height=350,
        xaxis_title_font=dict(color="grey"),
        yaxis_title_font=dict(color="grey"),
        xaxis_tickfont=dict(color="grey"),
        yaxis_tickfont=dict(color="grey"),
        legend_title_font=dict(color="grey"),
        legend_font=dict(color="grey"),
        margin=dict(l=40, r=20, t=20, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)


cols = st.columns(2)


# Monthly Average Temperature & Precipitation
with cols[0].container(border=True, height="stretch"):

    st.markdown(
        f"<div style='font-size:22px; font-weight:300;'>"
        f"Monthly Average Temperature & Precipitation — {city} ({selected_year})"
        f"</div>",
        unsafe_allow_html=True
    )

    filtered_df = df[
        (df["city"] == city) &
        (df["date"].dt.year == selected_year)
        ].copy()

    filtered_df["date"] = pd.to_datetime(filtered_df["date"])

    monthly_df = (
        filtered_df
        .assign(
            month=filtered_df["date"].dt.strftime("%b"),
            month_num=filtered_df["date"].dt.month
        )
        .groupby(["month", "month_num"], as_index=False)
        .agg(
            avg_temp=("tavg", "mean"),
            total_prcp=("prcp", "sum")
        )
        .sort_values("month_num")
    )

    fig = go.Figure()

    # Bars → Precipitation (Right Axis)
    fig.add_bar(
        x=monthly_df["month"],
        y=monthly_df["total_prcp"],
        name="Precipitation (mm)",
        yaxis="y2",
        marker_color="#6EC6CA",
        opacity=0.85,
        hovertemplate="Precipitation (mm): %{y:.0f}<extra></extra>"
    )

    # Line → Temperature (Left Axis)
    fig.add_scatter(
        x=monthly_df["month"],
        y=monthly_df["avg_temp"],
        name="Temperature (°C)",
        mode="lines+markers",
        line=dict(color="#1F3C88", width=2),
        marker=dict(size=7),
        hovertemplate="Temperature (°C): %{y:.1f}<extra></extra>"
    )

    fig.update_layout(
        xaxis=dict(
            title="Month",
            showspikes=False 
        ),

        # Primary Y-axis (Temperature)
        yaxis=dict(
            title="Temperature (°C)",
            showgrid=True,              
            gridcolor="rgba(0,0,0,0.1)",
            tickfont=dict(color="#1F3C88")
        ),

        # Secondary Y-axis (Precipitation) 
        yaxis2=dict(
            title="Precipitation (mm)",
            overlaying="y",
            side="right",
            showgrid=False,           
            tickfont=dict(color="#6EC6CA")
        ),

        # ---- Unified Hover ----
        hovermode="x unified",

        legend=dict(
            orientation="h",
            y=-0.25,
            x=0.5,
            xanchor="center"
        ),

        height=350,
        margin=dict(l=40, r=20, t=20, b=40),
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)


# Monthly Weather Breakdown 
with cols[1].container(border=True, height="stretch"):

    st.markdown(
        f"<div style='font-size:22px; font-weight:300;'>"
        f"Monthly Weather Breakdown — {city} ({selected_year})"
        f"</div>",
        unsafe_allow_html=True
    )

    df["month_name"] = df["date"].dt.strftime("%b")


    city_year_df = df[(df["city"] == city) & (df["year"] == selected_year)].copy()

    city_year_df["weather"] = city_year_df.apply(classify_weather, axis=1)

    # Monthly count of weather types
    monthly_weather = (
        city_year_df
        .groupby(["month", "month_name", "weather"], as_index=False)
        .size()
        .rename(columns={"size": "days"})
    )

    # Month order
    month_order = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]
    monthly_weather["month_name"] = pd.Categorical(
        monthly_weather["month_name"],
        categories=month_order,
        ordered=True
    )
    monthly_weather = monthly_weather.sort_values("month")

    # Stacked bar chart
    fig = px.bar(
        monthly_weather,
        x="month_name",
        y="days",
        color="weather",
        barmode="stack",
        color_discrete_map={
            "sun": "#FB2D2D",
            "fog": "#BDBDBD",
            "drizzle": "#81D4FA",
            "rain": "#1E88E5"
        }
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Days",
        legend_title="Weather Type",
        height=350,
        legend_font=dict(color="grey"),
        margin=dict(l=40, r=20, t=20, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

