"""
Product Manager Insights Dashboard
10 rapoarte comprehensive pentru PM decision making
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from utils.pm_analytics import PMAnalytics
from utils.pm_charts import (
    create_feature_gap_chart, create_sentiment_pie, create_platform_health_chart,
    create_resolution_time_chart, create_trend_chart, create_gauge_chart, create_heatmap
)

st.set_page_config(page_title="PM Insights", page_icon="📊", layout="wide")


def main():
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original

    st.title("📊 Product Manager Insights Dashboard")
    st.markdown("10 rapoarte comprehensive pentru decision making")

    # Date range filter
    col1, col2 = st.columns([3, 1])
    with col1:
        date_range = st.date_input(
            "📅 Filtrează perioada",
            value=(df['created_at'].min().date() if 'created_at' in df.columns else datetime.now().date(),
                   df['created_at'].max().date() if 'created_at' in df.columns else datetime.now().date()),
            key="pm_date_range"
        )

    if len(date_range) == 2:
        df = df[(df['created_at'].dt.date >= date_range[0]) & (df['created_at'].dt.date <= date_range[1])]

    st.markdown("---")

    # Create tabs
    tabs = st.tabs([
        "🎯 Roadmap", "🐛 Bugs", "😊 Satisfaction", "💼 Business Impact", "🔄 Recurring",
        "📊 Platform Health", "⏱️ Ops Efficiency", "🎯 User Journey", "🔌 Integrations", "📈 Executive"
    ])

    # Tab 1: Product Roadmap Intelligence
    with tabs[0]:
        st.markdown("## 🎯 Product Roadmap Intelligence")
        st.markdown("Top feature gaps și cerințe noi")

        feature_gaps = PMAnalytics.get_feature_gaps(df)

        if not feature_gaps.empty:
            col1, col2 = st.columns([2, 1])

            with col1:
                fig = create_feature_gap_chart(feature_gaps)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.metric("Total Feature Gaps", len(feature_gaps))
                st.metric("Highest Priority Score", int(feature_gaps['priority_score'].max()))

            st.markdown("### 📋 Detalii Feature Gaps")
            st.dataframe(feature_gaps, use_container_width=True, height=400)

            if st.button("📥 Export Feature Gaps CSV"):
                csv = feature_gaps.to_csv(index=False)
                st.download_button("Download CSV", csv, "feature_gaps.csv", "text/csv")
        else:
            st.info("Nu există feature gaps înregistrate")

    # Tab 2: Critical Bugs & Quality
    with tabs[1]:
        st.markdown("## 🐛 Critical Bugs & Quality Report")

        bugs = PMAnalytics.get_critical_bugs(df)

        if not bugs.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 Total Blockers", len(bugs[bugs['urgency'] == 'blocker']))
            with col2:
                st.metric("🔄 Recurente", len(bugs[bugs['is_recurrent'] == True]))
            with col3:
                st.metric("💼 Business Impact", len(bugs[bugs['affects_business_flow'] == True]))

            st.markdown("### 📋 Critical Bugs List")
            st.dataframe(bugs, use_container_width=True, height=500)
        else:
            st.success("✅ Nu există bugs critice active")

    # Tab 3: Customer Satisfaction & Sentiment
    with tabs[2]:
        st.markdown("## 😊 Customer Satisfaction & Sentiment")

        nps = PMAnalytics.calculate_nps_score(df)
        sentiment = PMAnalytics.calculate_sentiment_score(df)

        col1, col2 = st.columns(2)

        with col1:
            fig_nps = create_gauge_chart(nps, "NPS Score", max_value=100)
            st.plotly_chart(fig_nps, use_container_width=True)

        with col2:
            if sentiment:
                fig_sent = create_sentiment_pie(sentiment)
                st.plotly_chart(fig_sent, use_container_width=True)

        if sentiment:
            st.markdown("### 📊 Sentiment Breakdown")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("😊 Pozitiv", f"{sentiment['pozitiv']} ({sentiment['pozitiv_pct']}%)")
            with col2:
                st.metric("😐 Neutru", f"{sentiment['neutru']} ({sentiment['neutru_pct']}%)")
            with col3:
                st.metric("😠 Negativ", f"{sentiment['negativ']} ({sentiment['negativ_pct']}%)")

    # Tab 4: Business Impact & Risk
    with tabs[3]:
        st.markdown("## 💼 Business Impact & Risk Report")

        business_impact = PMAnalytics.get_business_impact_issues(df)

        if not business_impact.empty:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### 🎯 Top Business Impact Issues")
                st.dataframe(business_impact.head(15), use_container_width=True, height=400)

            with col2:
                st.metric("Total Issues", len(business_impact))
                st.metric("Highest Risk Score", int(business_impact['risk_score'].max()))
                st.metric("Avg Risk Score", round(business_impact['risk_score'].mean(), 2))

        else:
            st.success("✅ Nu există issues care afectează business flow")

    # Tab 5: Recurring Issues & Patterns
    with tabs[4]:
        st.markdown("## 🔄 Recurring Issues & Patterns")

        recurring = PMAnalytics.get_recurring_patterns(df)

        if not recurring.empty:
            st.markdown("### 📊 Top Recurring Problems")
            st.dataframe(recurring, use_container_width=True, height=500)

            st.metric("Total Recurring Issues", len(df[df['is_recurrent'] == True]))
        else:
            st.info("Nu există probleme recurente")

    # Tab 6: Platform & Feature Health
    with tabs[5]:
        st.markdown("## 📊 Platform & Feature Health Dashboard")

        platform_health = PMAnalytics.get_platform_health(df)

        if not platform_health.empty:
            fig_health = create_platform_health_chart(platform_health)
            st.plotly_chart(fig_health, use_container_width=True)

            st.markdown("### 📋 Platform Scorecard")
            st.dataframe(platform_health, use_container_width=True, height=400)

            # Heatmap
            if 'platform' in df.columns and 'problem_type' in df.columns:
                st.markdown("### 🗺️ Platform vs Problem Type Heatmap")
                fig_heat = create_heatmap(df, 'problem_type', 'platform')
                st.plotly_chart(fig_heat, use_container_width=True)

    # Tab 7: Operational Efficiency
    with tabs[6]:
        st.markdown("## ⏱️ Operational Efficiency Report")

        metrics = PMAnalytics.calculate_operational_metrics(df)

        if metrics:
            col1, col2, col3 = st.columns(3)

            with col1:
                if 'agent_intervention_rate' in metrics:
                    st.metric("🔧 Agent Intervention Rate", f"{metrics['agent_intervention_rate']}%")

            with col2:
                if 'sla_compliance' in metrics:
                    st.metric("✅ SLA Compliance", f"{metrics['sla_compliance']}%")

            with col3:
                if 'avg_resolution_blocker' in metrics:
                    st.metric("⏱️ Avg Blocker Resolution", f"{metrics['avg_resolution_blocker']}h")

            if any(k.startswith('avg_resolution_') for k in metrics.keys()):
                fig_res = create_resolution_time_chart(metrics)
                st.plotly_chart(fig_res, use_container_width=True)

    # Tab 8: User Goals vs Pain Points
    with tabs[7]:
        st.markdown("## 🎯 User Goals vs Pain Points Analysis")

        journey_gaps = PMAnalytics.get_user_journey_gaps(df)

        if not journey_gaps.empty:
            st.markdown("### 📋 Where User Goals Fail")
            st.dataframe(journey_gaps, use_container_width=True, height=500)

            st.metric("Total Failing Journeys", len(journey_gaps))
        else:
            st.info("Nu există date despre user goals și pain points")

    # Tab 9: Integration & Third-Party Issues
    with tabs[8]:
        st.markdown("## 🔌 Integration & Third-Party Issues Report")

        integration_health = PMAnalytics.get_integration_health(df)

        if not integration_health.empty:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.dataframe(integration_health, use_container_width=True, height=400)

            with col2:
                for idx, row in integration_health.iterrows():
                    fig_gauge = create_gauge_chart(
                        row['reliability_score'],
                        f"{row['integration']} Reliability",
                        max_value=100
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    if idx >= 2:  # Limit to 3 gauges
                        break
        else:
            st.info("Nu există date despre integrări")

    # Tab 10: Executive Summary
    with tabs[9]:
        st.markdown("## 📈 Executive Summary")

        summary = PMAnalytics.generate_executive_summary(df)

        # Top metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📊 Total Tickets", summary.get('total_tickets', 0))

        with col2:
            st.metric("🔴 Critical Issues", summary.get('critical_issues', 0))

        with col3:
            st.metric("💼 Business Impact", summary.get('business_impact_issues', 0))

        with col4:
            trend = summary.get('trend_pct', 0)
            st.metric("📈 Trend (7d)", f"{trend:+.1f}%", delta=f"{trend:+.1f}%")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🎯 Top 3 Pain Points")
            for idx, pain in enumerate(summary.get('top_pain_points', []), 1):
                st.markdown(f"{idx}. {pain}")

        with col2:
            st.markdown("### 📊 Health Metrics")
            st.metric("NPS Score", summary.get('nps_score', 0))
            st.metric("Sentiment Score", summary.get('sentiment_score', 0))

        # Trend chart
        if 'created_at' in df.columns:
            st.markdown("### 📈 Ticket Volume Trend")
            fig_trend = create_trend_chart(df)
            st.plotly_chart(fig_trend, use_container_width=True)


if __name__ == "__main__":
    main()
