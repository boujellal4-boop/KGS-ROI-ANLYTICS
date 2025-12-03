import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import calculate_kpis, generate_required_charts

st.set_page_config(page_title="KGS Marketing Analytics – ROI Report Tool", layout="wide")
st.title("KGS Marketing Analytics – ROI Report Tool")

# Sidebar Inputs (Monthly, EUR)
st.sidebar.header("Monthly Marketing Data (EUR)")
marketing_expenses = st.sidebar.number_input("Marketing Expenses (€)", min_value=0.0, step=100.0)
estimated_annual_revenue = st.sidebar.number_input("Estimated Annual Revenue from This Month's Leads (€)", min_value=0.0, step=100.0)
money_saved = st.sidebar.number_input("Money Saved by Internal Resources (€)", min_value=0.0, step=100.0)

st.sidebar.subheader("Performance by Source (Monthly)")
# LinkedIn
linkedin_impressions = st.sidebar.number_input("LinkedIn Impressions", min_value=0, step=100)
linkedin_clicks = st.sidebar.number_input("LinkedIn Clicks", min_value=0, step=10)
linkedin_views = st.sidebar.number_input("LinkedIn Views", min_value=0, step=10)
# Google Ads (incl. YouTube views)
gads_impressions = st.sidebar.number_input("Google Ads Impressions", min_value=0, step=100)
gads_clicks = st.sidebar.number_input("Google Ads Clicks", min_value=0, step=10)
gads_views = st.sidebar.number_input("Google Ads Views (YouTube)", min_value=0, step=10)
# Website Platforms
website_impressions = st.sidebar.number_input("Website Impressions", min_value=0, step=100)
website_clicks = st.sidebar.number_input("Website Clicks", min_value=0, step=10)

# Generate Report
if st.button("Generate Report"):
    with st.spinner("Generating dashboard…"):
        df_sources = pd.DataFrame([
            {"Source": "LinkedIn", "Impressions": linkedin_impressions, "Clicks": linkedin_clicks, "Views": linkedin_views},
            {"Source": "Google Ads", "Impressions": gads_impressions, "Clicks": gads_clicks, "Views": gads_views},
            {"Source": "Website", "Impressions": website_impressions, "Clicks": website_clicks, "Views": 0},
        ])

        kpis = calculate_kpis(
            df_sources=df_sources,
            marketing_expenses=marketing_expenses,
            estimated_annual_revenue=estimated_annual_revenue,
            money_saved=money_saved,
        )

        # KPI cards (monthly) with hover info via st.metric(help=...)
        st.subheader("Key Performance Indicators (Monthly)")
        cols = st.columns(4)
        cols[0].metric(
            label="ROI (%)",
            value=f"{kpis['roi']:.2f}",
            help="Return per euro of marketing spend for this month, using Estimated Annual Revenue vs. Marketing Expenses."
        )
        cols[1].metric(
            label="Monetized Engagement (€)",
            value=f"{kpis['monetized_engagement_eur']:,.2f}",
            help="Euro value from impressions/clicks/views via source-specific multipliers tailored to B2B fire detection in EMEA."
        )
        cols[2].metric(
            label="Marketing Expenses (€)",
            value=f"{marketing_expenses:,.2f}",
            help="Total monthly cost of marketing activities across channels."
        )
        cols[3].metric(
            label="Money Saved (€)",
            value=f"{money_saved:,.2f}",
            help="Savings achieved by using internal resources instead of outsourcing during this month."
        )

        # Visualizations (only the required set)
        st.subheader("Dashboard Visualizations")
        figs = generate_required_charts(df_sources, kpis, marketing_expenses, money_saved)
        for fig in figs:
            st.plotly_chart(fig, use_container_width=True)
