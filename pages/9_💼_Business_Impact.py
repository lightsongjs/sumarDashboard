"""
Business Impact Analysis Dashboard
Quantify the impact of support issues on customer operations and business resources
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.charts import COLORS, DARK_TEMPLATE, AXIS_STYLE

st.set_page_config(page_title="Business Impact", page_icon="💼", layout="wide")


def create_gauge_chart(percentage, title, threshold_red=70, threshold_yellow=40):
    """Create a gauge chart showing percentage with color coding"""
    # Determine color based on thresholds
    if percentage >= threshold_red:
        color = COLORS['danger']
    elif percentage >= threshold_yellow:
        color = COLORS['warning']
    else:
        color = COLORS['success']

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        number={'suffix': "%", 'font': {'size': 48}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': COLORS['gray']},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': COLORS['gray'],
            'steps': [
                {'range': [0, threshold_yellow], 'color': 'rgba(16, 185, 129, 0.2)'},
                {'range': [threshold_yellow, threshold_red], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [threshold_red, 100], 'color': 'rgba(239, 68, 68, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': percentage
            }
        }
    ))

    fig.update_layout(
        height=300,
        **DARK_TEMPLATE['layout']
    )

    return fig


def create_platform_distribution_chart(df, chart_type='pie'):
    """Create platform distribution chart (pie or treemap)"""
    platform_counts = df['platform'].value_counts().reset_index()
    platform_counts.columns = ['platform', 'count']

    if chart_type == 'pie':
        fig = go.Figure(data=[go.Pie(
            labels=platform_counts['platform'],
            values=platform_counts['count'],
            hole=0.3,
            marker=dict(
                colors=px.colors.qualitative.Set2
            ),
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Tickets: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            title='Problem Distribution by Platform',
            showlegend=True,
            **DARK_TEMPLATE['layout']
        )

    else:  # treemap
        fig = go.Figure(go.Treemap(
            labels=platform_counts['platform'],
            parents=[''] * len(platform_counts),
            values=platform_counts['count'],
            textposition='middle center',
            marker=dict(
                colors=platform_counts['count'],
                colorscale='Reds',
                showscale=False
            ),
            hovertemplate='<b>%{label}</b><br>Tickets: %{value}<extra></extra>'
        ))

        fig.update_layout(
            title='Problem Distribution by Platform (Treemap)',
            **DARK_TEMPLATE['layout']
        )

    return fig


def get_critical_open_issues(df):
    """Get critical open issues (blockers affecting business flow)"""
    critical_df = df[
        (df['urgency'].str.lower() == 'blocker') &
        (df['affects_business_flow'] == True)
    ].copy()

    # Select relevant columns
    display_columns = [
        'created_at', 'summary', 'area', 'platform', 'pain_point',
        'customer_email_extracted', 'ticket_url', 'closed_at'
    ]

    available_columns = [col for col in display_columns if col in critical_df.columns]
    critical_df = critical_df[available_columns]

    # Sort by created_at descending (most recent first)
    if 'created_at' in critical_df.columns:
        critical_df = critical_df.sort_values('created_at', ascending=False)

    return critical_df


def create_impact_trend_chart(df):
    """Create trend of business-impacting tickets over time"""
    # Group by date and business impact
    df_business = df[df['affects_business_flow'] == True].copy()

    if len(df_business) == 0:
        return None

    trend_data = df_business.groupby(
        pd.Grouper(key='created_at', freq='W-MON')
    ).size().reset_index(name='count')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend_data['created_at'],
        y=trend_data['count'],
        mode='lines+markers',
        name='Business Impact Tickets',
        line=dict(color=COLORS['danger'], width=3),
        marker=dict(size=8, color=COLORS['danger']),
        fill='tozeroy',
        fillcolor=f'rgba(239, 68, 68, 0.2)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Tickets: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title='Business-Impacting Tickets Trend (Weekly)',
        xaxis_title='Week',
        yaxis_title='Number of Tickets',
        hovermode='x unified',
        **DARK_TEMPLATE['layout']
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def main():
    # Check if data is loaded
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original.copy()

    # Page header
    st.title("💼 Business Impact Analysis")
    st.markdown("Quantify the impact of support issues on customer operations and business resources")

    st.markdown("---")

    # Component 1: Business Flow Impact Gauge
    st.markdown("### 💥 Business Flow Impact")

    if 'affects_business_flow' in df.columns:
        business_impact_count = len(df[df['affects_business_flow'] == True])
        total_count = len(df)
        business_impact_pct = (business_impact_count / total_count * 100) if total_count > 0 else 0

        col1, col2 = st.columns([2, 1])

        with col1:
            fig_gauge = create_gauge_chart(
                business_impact_pct,
                "Tickets Affecting Business Flow",
                threshold_red=50,
                threshold_yellow=30
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            st.markdown("#### Impact Summary")
            st.metric("Total Tickets", f"{total_count:,}")
            st.metric("Business Impact", f"{business_impact_count:,}")
            st.metric("Percentage", f"{business_impact_pct:.1f}%")

            st.markdown("---")

            st.caption(
                f"**{business_impact_count}** out of **{total_count}** tickets impact customer business flows. "
                f"This represents a {'critical' if business_impact_pct >= 50 else 'significant' if business_impact_pct >= 30 else 'moderate'} "
                f"level of business disruption."
            )
    else:
        st.warning("Column 'affects_business_flow' not found")

    st.markdown("---")

    # Component 2: Recurring Issues
    st.markdown("### 🔄 Recurring Issues")
    st.markdown("Tickets that have been reported multiple times - a sign of support inefficiency")

    if 'is_recurrent' in df.columns:
        recurrent_count = len(df[df['is_recurrent'] == True])
        total_count = len(df)
        recurrent_pct = (recurrent_count / total_count * 100) if total_count > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Recurring Issues",
                f"{recurrent_count:,}",
                delta=f"{recurrent_pct:.1f}% of total",
                delta_color="inverse"
            )

        with col2:
            if 'affects_business_flow' in df.columns:
                recurrent_business = len(df[(df['is_recurrent'] == True) & (df['affects_business_flow'] == True)])
                st.metric("Recurring + Business Impact", f"{recurrent_business:,}")

        with col3:
            if 'urgency' in df.columns:
                recurrent_blockers = len(df[(df['is_recurrent'] == True) & (df['urgency'].str.lower() == 'blocker')])
                st.metric("Recurring Blockers", f"{recurrent_blockers:,}")

        with col4:
            if 'problem_type' in df.columns:
                recurrent_bugs = len(df[(df['is_recurrent'] == True) & (df['problem_type'].str.lower() == 'bug')])
                st.metric("Recurring Bugs", f"{recurrent_bugs:,}")

        # Recommendation
        if recurrent_pct > 20:
            st.warning(
                f"⚠️ **{recurrent_pct:.1f}%** of tickets are recurring issues. "
                "This suggests a need for better documentation, permanent fixes, or product improvements."
            )
        elif recurrent_pct > 10:
            st.info(
                f"ℹ️ **{recurrent_pct:.1f}%** of tickets are recurring. "
                "Consider analyzing these patterns for potential improvements."
            )
        else:
            st.success(
                f"✅ Only **{recurrent_pct:.1f}%** of tickets are recurring. "
                "This indicates good support efficiency."
            )

    else:
        st.warning("Column 'is_recurrent' not found")

    st.markdown("---")

    # Component 3: Platform Distribution
    st.markdown("### 🏢 Problem Distribution by Platform")
    st.markdown("Identify if specific platforms are disproportionately contributing to support load")

    if 'platform' in df.columns:
        col1, col2 = st.columns([3, 1])

        with col2:
            chart_type = st.radio(
                "Chart Type",
                options=['pie', 'treemap'],
                format_func=lambda x: 'Pie Chart' if x == 'pie' else 'Treemap',
                key="platform_chart_type"
            )

        with col1:
            fig_platform = create_platform_distribution_chart(df, chart_type)
            st.plotly_chart(fig_platform, use_container_width=True)

        # Platform breakdown table
        st.markdown("#### Platform Breakdown")

        platform_stats = df.groupby('platform').agg({
            'platform': 'size',
            'affects_business_flow': lambda x: (x == True).sum() if 'affects_business_flow' in df.columns else 0,
            'is_recurrent': lambda x: (x == True).sum() if 'is_recurrent' in df.columns else 0
        }).rename(columns={
            'platform': 'total_tickets',
            'affects_business_flow': 'business_impact',
            'is_recurrent': 'recurrent'
        }).reset_index()

        platform_stats = platform_stats.sort_values('total_tickets', ascending=False)

        st.dataframe(
            platform_stats,
            use_container_width=True,
            column_config={
                "platform": st.column_config.TextColumn("Platform"),
                "total_tickets": st.column_config.NumberColumn("Total Tickets", format="%d"),
                "business_impact": st.column_config.NumberColumn("Business Impact", format="%d"),
                "recurrent": st.column_config.NumberColumn("Recurrent", format="%d")
            }
        )

    else:
        st.warning("Column 'platform' not found")

    st.markdown("---")

    # Component 4: Most Critical Open Issues
    st.markdown("### 🚨 Most Critical Open Issues")
    st.markdown("Priority list: Blockers that affect business flow")

    if 'urgency' in df.columns and 'affects_business_flow' in df.columns:
        critical_df = get_critical_open_issues(df)

        if len(critical_df) > 0:
            # Summary metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Critical Issues", len(critical_df))

            with col2:
                if 'closed_at' in critical_df.columns:
                    still_open = len(critical_df[critical_df['closed_at'].isna()])
                    st.metric("Still Open", still_open)

            with col3:
                if 'created_at' in critical_df.columns:
                    oldest_date = critical_df['created_at'].min()
                    days_old = (datetime.now() - oldest_date).days
                    st.metric("Oldest Issue", f"{days_old} days")

            st.markdown("---")

            # Display table
            display_df = critical_df.copy()

            # Format datetime columns
            for col in display_df.columns:
                if pd.api.types.is_datetime64_any_dtype(display_df[col]):
                    display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M')

            st.dataframe(
                display_df,
                use_container_width=True,
                height=400,
                column_config={
                    "ticket_url": st.column_config.LinkColumn("Ticket"),
                    "created_at": st.column_config.TextColumn("Created"),
                    "closed_at": st.column_config.TextColumn("Closed"),
                    "summary": st.column_config.TextColumn("Summary", width="large"),
                    "pain_point": st.column_config.TextColumn("Pain Point", width="large")
                }
            )

            # Export
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                csv = display_df.to_csv(index=False)
                st.download_button(
                    "📥 Export Critical Issues (CSV)",
                    csv,
                    "critical_issues.csv",
                    "text/csv",
                    use_container_width=True
                )

        else:
            st.success("✅ No critical open issues found! All blockers affecting business flow have been resolved.")

    else:
        st.warning("Columns 'urgency' or 'affects_business_flow' not found")

    # Optional: Business Impact Trend
    if 'created_at' in df.columns and 'affects_business_flow' in df.columns:
        st.markdown("---")
        st.markdown("### 📈 Business Impact Trend")

        fig_trend = create_impact_trend_chart(df)

        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No business-impacting tickets in the selected period")


if __name__ == "__main__":
    main()
