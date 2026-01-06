import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Monetization & EMEA weighting model
BASE_MULTIPLIERS = {
    "LinkedIn": {"impression": 0.06, "click": 2.20, "view": 1.20, "source_weight": 1.10},
    "Google Ads": {"impression": 0.03, "click": 2.60, "view": 1.40, "source_weight": 1.00},
    "Website": {"impression": 0.02, "click": 1.30, "view": 0.00, "source_weight": 0.95},
}
REGION_FACTORS = {"Western Europe": 1.00, "Nordics": 0.92, "Central & Eastern Europe": 0.88, "Middle East": 0.90, "Africa": 0.78}
REGION_DEFAULT_MIX = {"Western Europe": 0.35, "Nordics": 0.15, "Central & Eastern Europe": 0.20, "Middle East": 0.20, "Africa": 0.10}
AGG_REGION_FACTOR = sum(REGION_DEFAULT_MIX[r] * REGION_FACTORS[r] for r in REGION_FACTORS)


def calculate_kpis(df_sources, marketing_expenses, estimated_month_revenue, money_saved):
    # Monetized engagement per source
    monetized_per_source = []
    for _, row in df_sources.iterrows():
        s = row['Source']
        mp = BASE_MULTIPLIERS[s]
        monetized = (row['Impressions']*mp['impression'] + row['Clicks']*mp['click'] + row.get('Views',0)*mp['view']) * mp['source_weight'] * AGG_REGION_FACTOR
        monetized_per_source.append({'Source': s, 'Monetized (€)': monetized})
    df_monetized = pd.DataFrame(monetized_per_source)
    monetized_engagement_eur = float(df_monetized['Monetized (€)'].sum())

    # Total ROI includes Estimated Monthly Revenue + Monetized Engagement + Money Saved
    roi_total = 0.0
    if marketing_expenses > 0:
        total_value = (estimated_month_revenue or 0) + monetized_engagement_eur + (money_saved or 0)
        roi_total = ((total_value - marketing_expenses) / marketing_expenses) * 100.0

    return {
        'roi_total': roi_total,
        'monetized_engagement_eur': monetized_engagement_eur,
        'df_monetized': df_monetized,
    }


def generate_required_charts(df_sources, kpis, marketing_expenses, money_saved):
    figs = []
    color_map = {"LinkedIn": "#1F77B4", "Google Ads": "#FF7F0E", "Website": "#2CA02C"}

    # 1) Total ROI Gauge
    roi_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kpis['roi_total'],
        title={'text':"Total ROI (%)"},
        gauge={'axis':{'range':[None,300]}, 'bar':{'color':'#1F77B4'}}
    ))
    figs.append(roi_gauge)

    # 2) Monetized engagement by source (Bar)
    monetized_bar = px.bar(kpis['df_monetized'], x='Source', y='Monetized (€)', color='Source', color_discrete_map=color_map, title='Monetized Engagement by Source (€)')
    figs.append(monetized_bar)

    # 3) Money saved vs Marketing Expenses (Bar)
    comp_df = pd.DataFrame({'Category':['Money Saved','Marketing Expenses'],'Amount (€)':[money_saved,marketing_expenses]})
    comp_bar = px.bar(comp_df, x='Category', y='Amount (€)', color='Category', title='Money Saved vs Marketing Expenses (€)', color_discrete_sequence=['#2CA02C','#FF7F0E'])
    figs.append(comp_bar)

    # 4) Monetized engagement by source (Pie)
    monetized_pie = px.pie(kpis['df_monetized'], names='Source', values='Monetized (€)', title='Monetized Engagement Share by Source')
    figs.append(monetized_pie)

    return figs
