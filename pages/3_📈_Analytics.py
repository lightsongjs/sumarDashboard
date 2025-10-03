"""
Advanced Analytics Page - Statistical analysis, forecasting, and comparisons
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor
from utils.filters import render_sidebar_filters, show_filter_summary
from utils.charts import (
    create_pareto_chart, create_comparison_chart,
    create_resolution_time_boxplot, COLORS
)

import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Analytics - SmartBill Analytics",
    page_icon="📈",
    layout="wide"
)


def create_forecast_chart(df: pd.DataFrame, forecast_days: int = 7):
    """Simple linear forecast for ticket volume"""

    if 'created_date' in df.columns and len(df) > 0:
        # Daily counts
        daily_counts = df.groupby('created_date').size().reset_index(name='count')
        daily_counts = daily_counts.sort_values('created_date')

        # Create time series index
        daily_counts['day_index'] = range(len(daily_counts))

        # Simple linear regression
        x = daily_counts['day_index'].values
        y = daily_counts['count'].values

        # Fit polynomial (degree 1 = linear)
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)

        # Forecast
        future_indices = range(len(daily_counts), len(daily_counts) + forecast_days)
        forecast_values = [p(i) for i in future_indices]

        # Create future dates
        last_date = daily_counts['created_date'].max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

        # Plot
        fig = go.Figure()

        # Historical data
        fig.add_trace(go.Scatter(
            x=daily_counts['created_date'],
            y=daily_counts['count'],
            mode='lines+markers',
            name='Date Istorice',
            line=dict(color=COLORS['primary'], width=2),
            marker=dict(size=6)
        ))

        # Trend line
        fig.add_trace(go.Scatter(
            x=daily_counts['created_date'],
            y=[p(i) for i in x],
            mode='lines',
            name='Trend',
            line=dict(color=COLORS['secondary'], dash='dash', width=2)
        ))

        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_values,
            mode='lines+markers',
            name=f'Forecast ({forecast_days} zile)',
            line=dict(color=COLORS['danger'], dash='dot', width=2),
            marker=dict(size=8, symbol='diamond')
        ))

        fig.update_layout(
            title=f'Forecast Volume Tickets - Următoarele {forecast_days} Zile',
            xaxis_title='Data',
            yaxis_title='Număr Tickets',
            paper_bgcolor='#0E1117',
            plot_bgcolor='#262730',
            font={'color': '#FAFAFA'},
            hovermode='x unified',
            height=500
        )

        return fig

    return None


def create_correlation_matrix(df: pd.DataFrame):
    """Create correlation matrix for categorical variables"""

    # Select categorical columns
    cat_columns = []
    for col in ['platform', 'area', 'urgency', 'sentiment', 'problem_type']:
        if col in df.columns:
            cat_columns.append(col)

    if len(cat_columns) < 2:
        return None

    # Create dummy variables
    df_encoded = pd.get_dummies(df[cat_columns], prefix_sep='_')

    # Calculate correlation
    corr_matrix = df_encoded.corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu_r',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 8},
        hovertemplate='%{x}<br>%{y}<br>Correlation: %{z:.3f}<extra></extra>'
    ))

    fig.update_layout(
        title='Matrice Corelații între Categorii',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=800,
        xaxis={'tickangle': -45}
    )

    return fig


def create_cohort_analysis(df: pd.DataFrame):
    """Create cohort analysis by week"""

    if 'created_at' not in df.columns or 'created_week' not in df.columns:
        return None

    # Group by week and platform
    if 'platform' in df.columns:
        cohort = df.groupby(['created_week', 'platform']).size().reset_index(name='count')
        cohort_pivot = cohort.pivot(index='created_week', columns='platform', values='count').fillna(0)

        fig = go.Figure()

        for platform in cohort_pivot.columns:
            fig.add_trace(go.Scatter(
                x=cohort_pivot.index,
                y=cohort_pivot[platform],
                mode='lines+markers',
                name=platform,
                stackgroup='one'
            ))

        fig.update_layout(
            title='Analiza Cohort - Evoluția Tickets pe Platforme (Săptămânal)',
            xaxis_title='Săptămână',
            yaxis_title='Număr Tickets',
            paper_bgcolor='#0E1117',
            plot_bgcolor='#262730',
            font={'color': '#FAFAFA'},
            height=500
        )

        return fig

    return None


def generate_insights(df: pd.DataFrame):
    """Generate automated insights from data"""

    insights = []

    # Peak hour analysis
    if 'created_hour' in df.columns:
        hour_counts = df['created_hour'].value_counts()
        peak_hour = hour_counts.idxmax()
        peak_count = hour_counts.max()
        insights.append(f"📊 **Ora de vârf:** {peak_hour}:00 - {peak_count} tickets")

    # Peak day analysis
    if 'created_day_of_week' in df.columns:
        day_counts = df['created_day_of_week'].value_counts()
        peak_day = day_counts.idxmax()
        insights.append(f"📅 **Ziua cu cele mai multe tickets:** {peak_day}")

    # Blocker analysis
    if 'urgency' in df.columns:
        blocker_count = len(df[df['urgency'] == 'blocker'])
        blocker_pct = (blocker_count / len(df) * 100) if len(df) > 0 else 0
        if blocker_pct > 20:
            insights.append(f"⚠️ **Alert:** {blocker_pct:.1f}% din tickets sunt Blockers (>{20}%)")
        else:
            insights.append(f"✅ **Blocker rate:** {blocker_pct:.1f}% (sub pragul de 20%)")

    # Recurrence analysis
    if 'is_recurrent' in df.columns:
        recurrent_count = len(df[df['is_recurrent'] == True])
        recurrent_pct = (recurrent_count / len(df) * 100) if len(df) > 0 else 0
        insights.append(f"🔁 **Probleme recurente:** {recurrent_pct:.1f}% ({recurrent_count} tickets)")

    # Sentiment analysis
    if 'sentiment' in df.columns:
        negative = len(df[df['sentiment'] == 'negativ'])
        negative_pct = (negative / len(df) * 100) if len(df) > 0 else 0
        if negative_pct > 30:
            insights.append(f"😞 **Atenție:** {negative_pct:.1f}% sentiment negativ")
        else:
            insights.append(f"😊 **Sentiment negativ:** {negative_pct:.1f}%")

    # Resolution time
    if 'resolution_time_hours' in df.columns:
        avg_resolution = df['resolution_time_hours'].mean()
        if avg_resolution > 48:
            insights.append(f"⏱️ **Timp rezolvare peste medie:** {avg_resolution:.1f}h (>48h)")
        else:
            insights.append(f"⏱️ **Timp mediu rezolvare:** {avg_resolution:.1f}h")

    # Top platform
    if 'platform' in df.columns:
        top_platform = df['platform'].value_counts().idxmax()
        top_count = df['platform'].value_counts().max()
        insights.append(f"🏢 **Platforma cu cele mai multe tickets:** {top_platform} ({top_count})")

    # Top area
    if 'area' in df.columns:
        top_area = df['area'].value_counts().idxmax()
        insights.append(f"📍 **Area cu cele mai multe probleme:** {top_area}")

    return insights


def main():
    """Main analytics function"""

    # Check if data is loaded
    if 'df_original' not in st.session_state or st.session_state.df_original is None:
        st.warning("⚠️ Nu există date încărcate. Vă rugăm să încărcați un fișier CSV mai întâi.")
        if st.button("↩️ Înapoi la pagina principală"):
            st.switch_page("app.py")
        return

    # Get original data
    df_original = st.session_state.df_original

    # Render sidebar filters
    filters = render_sidebar_filters(df_original)

    # Apply filters
    df_filtered = CSVProcessor.apply_filters(
        df_original,
        date_range=filters['date_range'],
        platforms=filters['platforms'] if filters['platforms'] else None,
        areas=filters['areas'] if filters['areas'] else None,
        urgency_levels=filters['urgency_levels'] if filters['urgency_levels'] else None,
        sentiment=filters['sentiment'],
        only_recurrent=filters['only_recurrent'],
        affects_business=filters['affects_business'],
        search_text=filters['search_text'] if filters['search_text'] else None
    )

    # Header
    st.title("📈 Analytics Avansate")
    st.markdown("### Analiză statistică, forecast și comparații")

    st.markdown("---")

    # Show filter summary
    show_filter_summary(df_original, df_filtered)

    st.markdown("---")

    # Check if we have data
    if len(df_filtered) == 0:
        st.warning("⚠️ Nu există date pentru filtrele selectate.")
        return

    # AI Insights
    st.subheader("🤖 AI Insights - Detectare Automată Patterns")

    insights = generate_insights(df_filtered)

    if insights:
        for insight in insights:
            st.markdown(f"• {insight}")
    else:
        st.info("Nu s-au putut genera insights pentru datele curente")

    st.markdown("---")

    # Pareto Analysis
    st.subheader("📊 Analiza Pareto (80/20)")

    pareto_col = st.selectbox(
        "Selectează categoria pentru analiza Pareto:",
        options=['area', 'platform', 'problem_type'],
        format_func=lambda x: {'area': 'Arii', 'platform': 'Platforme', 'problem_type': 'Tipuri Probleme'}[x]
    )

    if pareto_col in df_filtered.columns:
        fig_pareto = create_pareto_chart(df_filtered, category_col=pareto_col,
                                        title=f'Analiza Pareto - {pareto_col.title()}')
        st.plotly_chart(fig_pareto, use_container_width=True)
    else:
        st.warning(f"Coloana '{pareto_col}' nu este disponibilă")

    st.markdown("---")

    # Forecast
    st.subheader("🔮 Forecast Volume Tickets")

    forecast_days = st.slider("Număr zile pentru forecast:", min_value=3, max_value=14, value=7)

    fig_forecast = create_forecast_chart(df_filtered, forecast_days=forecast_days)
    if fig_forecast:
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.warning("Nu există suficiente date pentru forecast")

    st.markdown("---")

    # Period Comparison
    st.subheader("📊 Comparație Perioade")

    if 'created_at' in df_filtered.columns and len(df_filtered) > 0:
        col1, col2 = st.columns(2)

        # Current period
        current_start = df_filtered['created_at'].min()
        current_end = df_filtered['created_at'].max()
        period_days = (current_end - current_start).days

        # Previous period
        previous_start = current_start - timedelta(days=period_days + 1)
        previous_end = current_start - timedelta(days=1)

        df_previous = df_original[
            (df_original['created_at'] >= previous_start) &
            (df_original['created_at'] <= previous_end)
        ]

        if len(df_previous) > 0:
            fig_comparison = create_comparison_chart(
                df_filtered, df_previous,
                label1=f'Current ({current_start.date()} - {current_end.date()})',
                label2=f'Previous ({previous_start.date()} - {previous_end.date()})'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("Nu există date pentru perioada anterioară pentru comparație")
    else:
        st.warning("Nu există date de timestamp pentru comparație")

    st.markdown("---")

    # Resolution Time Box Plots
    st.subheader("📦 Distribuție Timp Rezolvare per Platformă")

    if 'resolution_time_hours' in df_filtered.columns and 'platform' in df_filtered.columns:
        # Filter out outliers for better visualization
        df_resolution = df_filtered[df_filtered['resolution_time_hours'] < 200].copy()

        if len(df_resolution) > 0:
            fig_boxplot = create_resolution_time_boxplot(
                df_resolution,
                category_col='platform',
                time_col='resolution_time_hours'
            )
            st.plotly_chart(fig_boxplot, use_container_width=True)
        else:
            st.info("Nu există date de rezolvare disponibile")
    else:
        st.warning("Datele pentru timp rezolvare nu sunt disponibile")

    st.markdown("---")

    # Cohort Analysis
    st.subheader("📅 Analiza Cohort")

    fig_cohort = create_cohort_analysis(df_filtered)
    if fig_cohort:
        st.plotly_chart(fig_cohort, use_container_width=True)
    else:
        st.info("Nu există suficiente date pentru analiza cohort")

    st.markdown("---")

    # Statistical Summary
    st.subheader("📊 Sumar Statistic")

    # Create tabs for different stats
    tab1, tab2, tab3 = st.tabs(["📈 Generale", "⏱️ Timp Rezolvare", "📍 Distribuții"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Metrici Generale:**")
            st.metric("Total Tickets", f"{len(df_filtered):,}")

            if 'created_at' in df_filtered.columns:
                date_range = (df_filtered['created_at'].max() - df_filtered['created_at'].min()).days
                st.metric("Perioada (zile)", f"{date_range:,}")

            if 'platform' in df_filtered.columns:
                st.metric("Platforme Unice", df_filtered['platform'].nunique())

        with col2:
            st.markdown("**Urgență:**")
            if 'urgency' in df_filtered.columns:
                for urgency in ['blocker', 'mediu', 'scazut']:
                    count = len(df_filtered[df_filtered['urgency'] == urgency])
                    pct = (count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
                    st.metric(urgency, f"{count:,}", f"{pct:.1f}%")

    with tab2:
        if 'resolution_time_hours' in df_filtered.columns:
            stats = df_filtered['resolution_time_hours'].describe()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Medie", f"{stats['mean']:.2f}h")
                st.metric("Median", f"{stats['50%']:.2f}h")

            with col2:
                st.metric("Min", f"{stats['min']:.2f}h")
                st.metric("Max", f"{stats['max']:.2f}h")

            with col3:
                st.metric("Std Dev", f"{stats['std']:.2f}h")
                st.metric("Q3 (75%)", f"{stats['75%']:.2f}h")
        else:
            st.info("Datele pentru timp rezolvare nu sunt disponibile")

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            if 'platform' in df_filtered.columns:
                st.markdown("**Distribuție Platforme:**")
                platform_dist = df_filtered['platform'].value_counts()
                for platform, count in platform_dist.items():
                    pct = (count / len(df_filtered) * 100)
                    st.markdown(f"- **{platform}**: {count:,} ({pct:.1f}%)")

        with col2:
            if 'sentiment' in df_filtered.columns:
                st.markdown("**Distribuție Sentiment:**")
                sentiment_dist = df_filtered['sentiment'].value_counts()
                for sentiment, count in sentiment_dist.items():
                    pct = (count / len(df_filtered) * 100)
                    st.markdown(f"- **{sentiment}**: {count:,} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
