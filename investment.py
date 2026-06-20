
# Imports
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px


# Streamlit Configuration
st.set_page_config(
    page_title="Startup Funding Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom Styling
st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(to right, #141e30, #243b55);
    color: white;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Title Styling */
h1 {
    color: #00ffd5;
    text-align: center;
    font-size: 45px !important;
    font-weight: bold;
    text-shadow: 2px 2px 10px rgba(0,255,213,0.5);
}

/* Subheader Styling */
h2, h3 {
    color: #ffffff;
}

/* Metric Card Styling */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    transition: 0.3s;
}

/* Hover Effect */
[data-testid="metric-container"]:hover {
    transform: scale(1.05);
    box-shadow: 0px 6px 20px rgba(0,255,213,0.4);
}

/* Dataframe Styling */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* Button Styling */
.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    transition: 0.3s;
}

/* Button Hover */
.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(90deg, #0072ff, #00c6ff);
}

/* Selectbox Styling */
div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.08);
    color: white;
    border-radius: 10px;
}

/* Chart Animation */
.element-container {
    animation: fadeIn 1s ease-in;
}

/* Fade Animation */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(15px);
    }

    to {
        opacity: 1;
        transform: translateY(0px);
    }
}

</style>
""", unsafe_allow_html=True)


# Data Loading & Cleaning
@st.cache_data
def load_data():

    df = pd.read_csv(
        'startup_funding.csv',
        encoding='latin1'
    )

    cols_to_drop = ['Sr No', 'Remarks']

    for col in cols_to_drop:
        if col in df.columns:
            df.drop(columns=col, inplace=True)

    df.rename(columns={
        'Date dd/mm/yyyy': 'date',
        'Startup Name': 'startup',
        'Industry Vertical': 'vertical',
        'SubVertical': 'subvertical',
        'City  Location': 'city',
        'Investors Name': 'investor',
        'InvestmentnType': 'round',
        'Amount in USD': 'amount'
    }, inplace=True)

    df['date'] = pd.to_datetime(
        df['date'],
        dayfirst=True,
        errors='coerce'
    )

    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()

    df['amount'] = (
        df['amount']
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('$', '', regex=False)
    )

    df['amount'] = pd.to_numeric(
        df['amount'],
        errors='coerce'
    )

    df['amount'] = df['amount'].fillna(0)

    df['investor'] = (
        df['investor']
        .astype(str)
        .str.lower()
        .str.replace(r'\(.*?\)', '', regex=True)
        .str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )

    df['startup'] = (
        df['startup']
        .astype(str)
        .str.lower()
        .str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )

    return df


df = load_data()


# Sidebar Navigation
st.sidebar.title("🚀 Startup Funding Dashboard")

option = st.sidebar.selectbox(
    "Choose Analysis",
    ['Overall Analysis', 'Startup', 'Investor']
)

startup_list = sorted(
    df['startup'].dropna().unique().tolist()
)

investor_list = sorted(
    df['investor'].dropna().unique().tolist()
)


# Overall Analysis
if option == 'Overall Analysis':

    st.title("📊 Overall Startup Funding Analysis")

    total_funding = round(df['amount'].sum())

    max_funding = round(
        df.groupby('startup')['amount']
        .sum()
        .max()
    )

    avg_funding = round(
        df.groupby('startup')['amount']
        .sum()
        .mean()
    )

    total_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Total Funding",
        f"${total_funding:,}"
    )

    col2.metric(
        "🏆 Highest Funding",
        f"${max_funding:,}"
    )

    col3.metric(
        "📈 Average Funding",
        f"${avg_funding:,}"
    )

    col4.metric(
        "🚀 Total Startups",
        total_startups
    )

    st.subheader("📅 Monthly Funding Trend")

    monthly = (
        df.groupby(['year', 'month'])['amount']
        .sum()
        .reset_index()
    )

    monthly['period'] = (
        monthly['month']
        + " "
        + monthly['year'].astype(str)
    )

    fig = px.line(
        monthly,
        x='period',
        y='amount',
        markers=True,
        template='plotly_dark'
    )

    fig.update_traces(
        line=dict(width=4)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥧 Funding Type Distribution")

    funding_type = (
        df['round']
        .value_counts()
        .head(10)
        .reset_index()
    )

    funding_type.columns = ['Type', 'Count']

    fig = px.pie(
        funding_type,
        names='Type',
        values='Count',
        hole=0.4,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🏙️ Top Cities")

    city = (
        df.groupby('city')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        city,
        x='city',
        y='amount',
        text_auto=True,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚀 Top Startups")

    startups = (
        df.groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        startups,
        x='amount',
        y='startup',
        orientation='h',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)


# Startup Analysis
elif option == 'Startup':

    selected_startup = st.sidebar.selectbox(
        "Select Startup",
        startup_list
    )

    startup_df = df[
        df['startup'] == selected_startup
    ]

    st.title(f"🚀 {selected_startup.upper()}")

    st.subheader("📌 Startup Details")

    st.write(
        "Industry:",
        startup_df['vertical'].iloc[0]
    )

    st.write(
        "Location:",
        startup_df['city'].iloc[0]
    )

    st.write(
        "Total Funding:",
        f"${startup_df['amount'].sum():,}"
    )

    st.subheader("📈 Yearly Funding Trend")

    yearly = (
        startup_df.groupby('year')['amount']
        .sum()
        .reset_index()
    )

    fig = px.area(
        yearly,
        x='year',
        y='amount',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥧 Investor Distribution")

    investor_data = (
        startup_df['investor']
        .value_counts()
        .head(10)
        .reset_index()
    )

    investor_data.columns = ['Investor', 'Count']

    fig = px.pie(
        investor_data,
        names='Investor',
        values='Count',
        hole=0.5,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)


# Investor Analysis
elif option == 'Investor':

    selected_investor = st.sidebar.selectbox(
        "Select Investor",
        investor_list
    )

    investor_df = df[
        df['investor'] == selected_investor
    ]

    st.title(f"💼 {selected_investor.upper()}")

    total = investor_df['amount'].sum()

    st.metric(
        "💰 Total Investment",
        f"${total:,}"
    )

    st.subheader("📋 Recent Investments")

    recent = investor_df.sort_values(
        by='date',
        ascending=False
    ).head(10)

    st.dataframe(
        recent[
            ['date', 'startup', 'round', 'amount']
        ]
    )

    st.subheader("🏆 Top Startups")

    top = (
        investor_df.groupby('startup')['amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top,
        x='startup',
        y='amount',
        text_auto=True,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥧 Sector Distribution")

    sector = (
        investor_df['vertical']
        .value_counts()
        .head(10)
        .reset_index()
    )

    sector.columns = ['Sector', 'Count']

    fig = px.pie(
        sector,
        names='Sector',
        values='Count',
        hole=0.4,
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Investment Trend")

    trend = (
        investor_df.groupby('year')['amount']
        .sum()
        .reset_index()
    )

    fig = px.line(
        trend,
        x='year',
        y='amount',
        markers=True,
        template='plotly_dark'
    )

    fig.update_traces(
        line=dict(width=4)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌍 City Distribution")

    city = (
        investor_df['city']
        .value_counts()
        .head(10)
        .reset_index()
    )

    city.columns = ['City', 'Count']

    fig = px.treemap(
        city,
        path=['City'],
        values='Count',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)