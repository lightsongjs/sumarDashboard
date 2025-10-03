"""
Dashboard Page - Main analytics view with KPIs and visualizations
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor
from utils.filters import render_sidebar_filters, show_filter_summary, create_quick_filters_ui
from utils.charts import (
    create_trend_chart, create_platform_distribution, create_heatmap,
    create_urgency_trend, create_sentiment_trend, create_problem_type_chart
)

# Page config
st.set_page_config(
    page_title="Dashboard - SmartBill Analytics",
    page_icon="📊",
    layout="wide"
)


def calculate_kpis(df: pd.DataFrame, df_previous: pd.DataFrame = None):
    """Calculate KPI metrics"""

    kpis = {}

    # Total tickets
    kpis['total_tickets'] = len(df)

    # Delta calculation for total tickets
    if df_previous is not None and len(df_previous) > 0:
        kpis['total_delta'] = len(df) - len(df_previous)
        kpis['total_delta_pct'] = ((len(df) - len(df_previous)) / len(df_previous) * 100) if len(df_previous) > 0 else 0
    else:
        kpis['total_delta'] = 0
        kpis['total_delta_pct'] = 0

    # Blockers
    if 'urgency' in df.columns:
        kpis['blockers'] = len(df[df['urgency'] == 'blocker'])

        if df_previous is not None and 'urgency' in df_previous.columns:
            prev_blockers = len(df_previous[df_previous['urgency'] == 'blocker'])
            kpis['blockers_delta'] = kpis['blockers'] - prev_blockers
            kpis['blockers_delta_pct'] = ((kpis['blockers'] - prev_blockers) / prev_blockers * 100) if prev_blockers > 0 else 0
        else:
            kpis['blockers_delta'] = 0
            kpis['blockers_delta_pct'] = 0
    else:
        kpis['blockers'] = 0
        kpis['blockers_delta'] = 0

    # Average resolution time
    if 'resolution_time_hours' in df.columns:
        kpis['avg_resolution'] = df['resolution_time_hours'].mean()

        if df_previous is not None and 'resolution_time_hours' in df_previous.columns:
            prev_resolution = df_previous['resolution_time_hours'].mean()
            kpis['resolution_delta'] = kpis['avg_resolution'] - prev_resolution
            kpis['resolution_delta_pct'] = ((kpis['avg_resolution'] - prev_resolution) / prev_resolution * 100) if prev_resolution > 0 else 0
        else:
            kpis['resolution_delta'] = 0
            kpis['resolution_delta_pct'] = 0
    else:
        kpis['avg_resolution'] = 0
        kpis['resolution_delta'] = 0

    # Satisfaction (based on positive sentiment)
    if 'sentiment' in df.columns and len(df) > 0:
        positive_count = len(df[df['sentiment'] == 'pozitiv'])
        kpis['satisfaction'] = (positive_count / len(df)) * 100

        if df_previous is not None and 'sentiment' in df_previous.columns and len(df_previous) > 0:
            prev_positive = len(df_previous[df_previous['sentiment'] == 'pozitiv'])
            prev_satisfaction = (prev_positive / len(df_previous)) * 100
            kpis['satisfaction_delta'] = kpis['satisfaction'] - prev_satisfaction
        else:
            kpis['satisfaction_delta'] = 0
    else:
        kpis['satisfaction'] = 0
        kpis['satisfaction_delta'] = 0

    return kpis


def render_kpi_cards(kpis: dict):
    """Render KPI metric cards"""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_str = f"{kpis['total_delta']:+,} ({kpis['total_delta_pct']:+.1f}%)" if kpis['total_delta'] != 0 else None
        st.metric(
            label="🎫 Total Tickets",
            value=f"{kpis['total_tickets']:,}",
            delta=delta_str
        )

    with col2:
        blocker_color = "🔴" if kpis['blockers'] > 20 else "🟡" if kpis['blockers'] > 10 else "🟢"
        delta_str = f"{kpis['blockers_delta']:+,}" if kpis['blockers_delta'] != 0 else None
        st.metric(
            label=f"{blocker_color} Blockers",
            value=f"{kpis['blockers']:,}",
            delta=delta_str,
            delta_color="inverse"  # More blockers = bad
        )

    with col3:
        if kpis['avg_resolution'] > 0:
            delta_str = f"{kpis['resolution_delta']:+.1f}h" if kpis['resolution_delta'] != 0 else None
            st.metric(
                label="⏱️ Rezolvare Medie",
                value=f"{kpis['avg_resolution']:.1f}h",
                delta=delta_str,
                delta_color="inverse"  # More time = bad
            )
        else:
            st.metric(
                label="⏱️ Rezolvare Medie",
                value="N/A"
            )

    with col4:
        delta_str = f"{kpis['satisfaction_delta']:+.1f}%" if kpis['satisfaction_delta'] != 0 else None
        satisfaction_emoji = "😊" if kpis['satisfaction'] >= 80 else "😐" if kpis['satisfaction'] >= 60 else "😞"
        st.metric(
            label=f"{satisfaction_emoji} Satisfacție",
            value=f"{kpis['satisfaction']:.1f}%",
            delta=delta_str
        )


def render_additional_stats(df: pd.DataFrame):
    """Render additional statistics cards"""

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if 'is_recurrent' in df.columns:
            recurrent = len(df[df['is_recurrent'] == True])
            recurrent_pct = (recurrent / len(df) * 100) if len(df) > 0 else 0
            st.metric(
                label="🔁 Probleme Recurente",
                value=f"{recurrent:,}",
                delta=f"{recurrent_pct:.1f}%"
            )

    with col2:
        if 'affects_business_flow' in df.columns:
            business_impact = len(df[df['affects_business_flow'] == True])
            business_pct = (business_impact / len(df) * 100) if len(df) > 0 else 0
            st.metric(
                label="💼 Impact Business",
                value=f"{business_impact:,}",
                delta=f"{business_pct:.1f}%"
            )

    with col3:
        if 'platform' in df.columns:
            platforms = df['platform'].nunique()
            st.metric(
                label="🏢 Platforme Active",
                value=f"{platforms:,}"
            )

    with col4:
        if 'area' in df.columns:
            areas = df['area'].nunique()
            st.metric(
                label="📍 Arii Distincte",
                value=f"{areas:,}"
            )

    with col5:
        if 'is_closed' in df.columns:
            closed = len(df[df['is_closed'] == True])
            closed_pct = (closed / len(df) * 100) if len(df) > 0 else 0
            st.metric(
                label="✅ Tickets Închise",
                value=f"{closed:,}",
                delta=f"{closed_pct:.1f}%"
            )


def main():
    """Main dashboard function"""

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
    st.title("📊 Dashboard Principal")

    # Show current date and data source
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Data și ora:** {datetime.now().strftime('%d %B %Y, %H:%M')}")
    with col2:
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()

    st.markdown("---")

    # Show filter summary
    show_filter_summary(df_original, df_filtered)

    st.markdown("---")

    # Quick filters
    create_quick_filters_ui(df_original)

    st.markdown("---")

    # Calculate previous period for comparison
    df_previous = None
    if 'created_at' in df_filtered.columns and len(df_filtered) > 0:
        # Get the date range of current filtered data
        current_start = df_filtered['created_at'].min()
        current_end = df_filtered['created_at'].max()
        period_days = (current_end - current_start).days

        # Calculate previous period
        previous_start = current_start - timedelta(days=period_days + 1)
        previous_end = current_start - timedelta(days=1)

        # Filter previous period data
        df_previous = df_original[
            (df_original['created_at'] >= previous_start) &
            (df_original['created_at'] <= previous_end)
        ]

    # KPIs
    st.subheader("📈 Indicatori Cheie (KPIs)")
    kpis = calculate_kpis(df_filtered, df_previous)
    render_kpi_cards(kpis)

    st.markdown("---")

    # Additional stats
    st.subheader("📊 Statistici Suplimentare")
    render_additional_stats(df_filtered)

    st.markdown("---")

    # Visualizations
    st.subheader("📉 Vizualizări")

    # Check if we have enough data
    if len(df_filtered) == 0:
        st.warning("⚠️ Nu există date pentru filtrele selectate. Vă rugăm să ajustați filtrele.")
        return

    # Row 1: Trend and Platform Distribution
    col1, col2 = st.columns(2)

    with col1:
        if 'created_date' in df_filtered.columns:
            fig_trend = create_trend_chart(df_filtered, date_col='created_date', title='Tickets pe Zile')
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Graficul de trend necesită coloana 'created_date'")

    with col2:
        if 'platform' in df_filtered.columns:
            fig_platform = create_platform_distribution(df_filtered, platform_col='platform')
            st.plotly_chart(fig_platform, use_container_width=True)
        else:
            st.info("Graficul de platforme necesită coloana 'platform'")

    # Row 2: Heatmap
    if 'created_hour' in df_filtered.columns and 'created_day_of_week' in df_filtered.columns:
        st.subheader("🔥 Heatmap: Volume Tickets pe Zi și Oră")
        fig_heatmap = create_heatmap(df_filtered, hour_col='created_hour', day_col='created_day_of_week')
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # Row 3: Urgency and Sentiment Trends
    col1, col2 = st.columns(2)

    with col1:
        if 'urgency' in df_filtered.columns and 'created_date' in df_filtered.columns:
            fig_urgency = create_urgency_trend(df_filtered, date_col='created_date', urgency_col='urgency')
            st.plotly_chart(fig_urgency, use_container_width=True)
        else:
            st.info("Graficul de urgență necesită coloanele 'urgency' și 'created_date'")

    with col2:
        if 'sentiment' in df_filtered.columns and 'created_date' in df_filtered.columns:
            fig_sentiment = create_sentiment_trend(df_filtered, date_col='created_date', sentiment_col='sentiment')
            st.plotly_chart(fig_sentiment, use_container_width=True)
        else:
            st.info("Graficul de sentiment necesită coloanele 'sentiment' și 'created_date'")

    # Row 4: Problem Types
    if 'problem_type' in df_filtered.columns:
        st.subheader("🔍 Distribuție Tipuri Probleme")
        fig_problems = create_problem_type_chart(df_filtered, problem_col='problem_type')
        st.plotly_chart(fig_problems, use_container_width=True)

    st.markdown("---")

    # Recent critical issues
    st.subheader("🚨 Ultimele Probleme Critice")

    if 'urgency' in df_filtered.columns:
        critical_df = df_filtered[df_filtered['urgency'] == 'blocker'].copy()

        if len(critical_df) > 0:
            # Sort by created_at descending
            if 'created_at' in critical_df.columns:
                critical_df = critical_df.sort_values('created_at', ascending=False)

            # Show top 5
            display_columns = []
            if 'created_at' in critical_df.columns:
                display_columns.append('created_at')
            if 'platform' in critical_df.columns:
                display_columns.append('platform')
            if 'area' in critical_df.columns:
                display_columns.append('area')
            if 'summary' in critical_df.columns:
                display_columns.append('summary')
            if 'pain_point' in critical_df.columns:
                display_columns.append('pain_point')

            if display_columns:
                st.dataframe(
                    critical_df[display_columns].head(5),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.success("✅ Nu există blockers în perioada selectată!")
    else:
        st.info("Coloana 'urgency' nu este disponibilă")

    st.markdown("---")

    # Export section
    st.subheader("📤 Export Date")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Export CSV Filtrat", use_container_width=True):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"smartbill_tickets_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("📋 Export Excel", use_container_width=True):
            st.info("Funcționalitatea de export Excel va fi disponibilă în pagina Reports")

    with col3:
        if st.button("📄 Generează PDF", use_container_width=True):
            st.info("Funcționalitatea de export PDF va fi disponibilă în pagina Reports")


if __name__ == "__main__":
    main()
