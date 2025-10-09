"""
DASHBOARD - Executive Overview
Consolidates Health Check, Business Impact, and PM Insights executive views
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.charts import COLORS, DARK_TEMPLATE, AXIS_STYLE
from utils.data_processor import auto_load_default_csv

st.set_page_config(page_title="DASHBOARD", page_icon="📊", layout="wide")


# ========================================
# Health Check Helper Functions
# ========================================

def create_volume_trend_chart(df, time_grouping='D'):
    """Create ticket volume trend line chart"""
    freq_map = {'D': 'D', 'W': 'W-MON', 'M': 'MS'}
    freq_label = {'D': 'Day', 'W': 'Week', 'M': 'Month'}

    df_grouped = df.groupby(pd.Grouper(key='created_at', freq=freq_map[time_grouping])).size().reset_index(name='count')

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_grouped['created_at'],
        y=df_grouped['count'],
        mode='lines+markers',
        name='Tickets',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['primary']),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Tickets: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title=f'Ticket Volume Trend (by {freq_label[time_grouping]})',
        xaxis_title='Date',
        yaxis_title='Number of Tickets',
        hovermode='x unified',
        **DARK_TEMPLATE['layout']
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_volume_bar_chart(df, time_grouping='D'):
    """Create ticket volume bar chart"""
    freq_map = {'D': 'D', 'W': 'W-MON', 'M': 'MS'}
    freq_label = {'D': 'Day', 'W': 'Week', 'M': 'Month'}

    df_grouped = df.groupby(pd.Grouper(key='created_at', freq=freq_map[time_grouping])).size().reset_index(name='count')

    # Filter out days with zero tickets
    df_grouped = df_grouped[df_grouped['count'] > 0]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_grouped['created_at'],
        y=df_grouped['count'],
        name='Tickets',
        marker=dict(color=COLORS['primary']),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Tickets: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title=f'Ticket Volume (Bar View - by {freq_label[time_grouping]})',
        xaxis_title='Date',
        yaxis_title='Number of Tickets',
        hovermode='x unified',
        **DARK_TEMPLATE['layout']
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def calculate_business_hours(start_time, end_time):
    """
    Calculate business hours between two timestamps.
    Business hours: Monday-Friday, 9:00-18:00
    """
    if pd.isna(start_time) or pd.isna(end_time):
        return 0

    if end_time <= start_time:
        return 0

    business_hours = 0
    current = start_time

    # Define business hours
    work_start_hour = 9
    work_end_hour = 18
    hours_per_day = work_end_hour - work_start_hour  # 9 hours

    while current < end_time:
        # Skip weekends (Saturday=5, Sunday=6)
        if current.weekday() < 5:  # Monday=0 to Friday=4
            # Calculate start of work for this day
            day_work_start = current.replace(hour=work_start_hour, minute=0, second=0, microsecond=0)
            day_work_end = current.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)

            # Adjust if current time is before work starts
            if current < day_work_start:
                current = day_work_start

            # Adjust if current time is after work ends
            if current >= day_work_end:
                current = current.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                continue

            # Calculate hours for this work day
            if end_time <= day_work_end:
                # End time is within this work day
                business_hours += (end_time - current).total_seconds() / 3600
                break
            else:
                # End time is beyond this work day
                business_hours += (day_work_end - current).total_seconds() / 3600
                current = day_work_end

        # Move to next day
        current = current.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

    return business_hours


def calculate_avg_resolution_time(df):
    """Calculate average time to resolution using business hours only"""
    closed_tickets = df[df['closed_at'].notna()].copy()

    if len(closed_tickets) == 0:
        return None, None, 0, None, 0

    # Calculate business hours for each ticket
    closed_tickets['resolution_hours'] = closed_tickets.apply(
        lambda row: calculate_business_hours(row['created_at'], row['closed_at']),
        axis=1
    )

    # Exclude outliers (> 30 days = 270 business hours)
    max_hours = 30 * 9  # 30 days * 9 hours/day = 270 hours
    tickets_before_filter = len(closed_tickets)
    closed_tickets = closed_tickets[closed_tickets['resolution_hours'] <= max_hours]
    tickets_excluded = tickets_before_filter - len(closed_tickets)

    if len(closed_tickets) == 0:
        return None, None, 0, None, tickets_excluded

    avg_hours = closed_tickets['resolution_hours'].mean()
    median_hours = closed_tickets['resolution_hours'].median()

    # Format average time
    days = int(avg_hours // 24)
    hours = int(avg_hours % 24)
    minutes = int((avg_hours * 60) % 60)

    if days > 0:
        avg_readable = f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        avg_readable = f"{hours}h {minutes}m"
    else:
        avg_readable = f"{minutes}m"

    # Format median time
    med_days = int(median_hours // 24)
    med_hours = int(median_hours % 24)
    med_minutes = int((median_hours * 60) % 60)

    if med_days > 0:
        median_readable = f"{med_days}d {med_hours}h {med_minutes}m"
    elif med_hours > 0:
        median_readable = f"{med_hours}h {med_minutes}m"
    else:
        median_readable = f"{med_minutes}m"

    # Calculate trend
    mid_date = closed_tickets['created_at'].min() + (closed_tickets['created_at'].max() - closed_tickets['created_at'].min()) / 2
    previous_period = closed_tickets[closed_tickets['created_at'] < mid_date]
    current_period = closed_tickets[closed_tickets['created_at'] >= mid_date]

    if len(previous_period) > 0 and len(current_period) > 0:
        prev_avg = previous_period['resolution_hours'].mean()
        curr_avg = current_period['resolution_hours'].mean()
        change_pct = ((curr_avg - prev_avg) / prev_avg) * 100
    else:
        change_pct = 0

    return avg_readable, median_readable, change_pct, len(closed_tickets), tickets_excluded


def create_sentiment_chart(df):
    """Create sentiment donut chart"""
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']

    color_map = {
        'pozitiv': COLORS['success'],
        'neutru': COLORS['warning'],
        'negativ': COLORS['danger']
    }

    colors = [color_map.get(s.lower(), COLORS['gray']) for s in sentiment_counts['sentiment']]

    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts['sentiment'],
        values=sentiment_counts['count'],
        hole=0.4,
        marker=dict(colors=colors),
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title='Customer Sentiment Distribution',
        showlegend=True,
        **DARK_TEMPLATE['layout']
    )

    return fig


def create_urgency_chart(df):
    """Create urgency breakdown bar chart"""
    urgency_counts = df['urgency'].value_counts().reset_index()
    urgency_counts.columns = ['urgency', 'count']

    urgency_order = ['blocker', 'mediu', 'scazut']
    urgency_counts['urgency'] = pd.Categorical(urgency_counts['urgency'], categories=urgency_order, ordered=True)
    urgency_counts = urgency_counts.sort_values('urgency')

    color_map = {
        'blocker': COLORS['danger'],
        'mediu': COLORS['warning'],
        'scazut': COLORS['info']
    }

    colors = [color_map.get(u.lower(), COLORS['gray']) for u in urgency_counts['urgency']]

    fig = go.Figure(data=[go.Bar(
        x=urgency_counts['urgency'],
        y=urgency_counts['count'],
        marker=dict(color=colors),
        text=urgency_counts['count'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title='Ticket Urgency Breakdown',
        xaxis_title='Urgency Level',
        yaxis_title='Number of Tickets',
        **DARK_TEMPLATE['layout']
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


# ========================================
# Business Impact Helper Functions
# ========================================

def create_gauge_chart(percentage, title, threshold_red=70, threshold_yellow=40):
    """Create a gauge chart showing percentage with color coding"""
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
            marker=dict(colors=px.colors.qualitative.Set2),
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

    display_columns = [
        'created_at', 'summary', 'area', 'platform', 'pain_point',
        'customer_email_extracted', 'ticket_url', 'closed_at'
    ]

    available_columns = [col for col in display_columns if col in critical_df.columns]
    critical_df = critical_df[available_columns]

    if 'created_at' in critical_df.columns:
        critical_df = critical_df.sort_values('created_at', ascending=False)

    return critical_df


# ========================================
# Main Function
# ========================================

def main():
    # Auto-load CSV if available
    auto_load_default_csv()

    # Check if data is loaded
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original.copy()

    # Page header
    st.title("📊 DASHBOARD")
    st.markdown("*Executive overview and high-level metrics for leadership*")

    # Global date range filter
    st.markdown("---")
    col1, col2 = st.columns([3, 1])

    with col1:
        if 'created_at' in df.columns:
            date_range = st.date_input(
                "📅 Filter Date Range",
                value=(df['created_at'].min().date(), df['created_at'].max().date()),
                key="strategic_dashboard_date_range"
            )

            if len(date_range) == 2:
                df = df[(df['created_at'].dt.date >= date_range[0]) & (df['created_at'].dt.date <= date_range[1])]

    st.markdown("---")

    # Tabbed interface
    tab1, tab2, tab3 = st.tabs([
        "❤️ Health Check",
        "💼 Business Impact",
        "📊 Executive Summary"
    ])

    with tab1:
        st.markdown("### ❤️ Support Health Check")

        # Component 1: Ticket Volume Trend
        st.markdown("#### 📈 Ticket Volume Trend")
        col1, col2 = st.columns([4, 1])

        with col2:
            time_grouping = st.selectbox(
                "Group by",
                options=['D', 'W', 'M'],
                format_func=lambda x: {'D': 'Day', 'W': 'Week', 'M': 'Month'}[x],
                key="volume_grouping"
            )

        with col1:
            if 'created_at' in df.columns:
                fig_volume = create_volume_trend_chart(df, time_grouping)
                st.plotly_chart(fig_volume, use_container_width=True)
            else:
                st.warning("Column 'created_at' not found")

        # Bar chart view
        if 'created_at' in df.columns:
            fig_bar = create_volume_bar_chart(df, time_grouping)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # Component 2: Average Time to Resolution
        st.markdown("#### ⏱️ Average Time to Resolution")

        if 'created_at' in df.columns and 'closed_at' in df.columns:
            avg_time, median_time, change_pct, closed_count, excluded_count = calculate_avg_resolution_time(df)

            if avg_time:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "⏱️ Median Resolution Time",
                        median_time,
                        help="Median time to resolution (business hours only: Mon-Fri, 9-18)"
                    )

                with col2:
                    st.metric(
                        "📊 Average Resolution Time",
                        avg_time,
                        delta=f"{change_pct:+.1f}% from previous period" if change_pct != 0 else None,
                        delta_color="inverse",
                        help="Average time to resolution (business hours only)"
                    )

                with col3:
                    st.metric("✅ Closed Tickets", f"{closed_count:,}")

                with col4:
                    open_count = len(df[df['closed_at'].isna()])
                    st.metric("🔓 Open Tickets", f"{open_count:,}")

                # Show info about filters
                if excluded_count > 0:
                    st.info(f"ℹ️ **Note:** {excluded_count} tickets excluded (resolution time > 30 days). Business hours: Mon-Fri, 9:00-18:00 only.")
                else:
                    st.info(f"ℹ️ **Note:** Resolution time calculated using business hours only (Mon-Fri, 9:00-18:00).")
            else:
                st.info("No closed tickets in the selected period")
        else:
            st.warning("Columns 'created_at' or 'closed_at' not found")

        st.markdown("---")

        # Components 3 & 4: Sentiment and Urgency (side by side)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 😊 Customer Sentiment")
            if 'sentiment' in df.columns:
                fig_sentiment = create_sentiment_chart(df)
                st.plotly_chart(fig_sentiment, use_container_width=True)
            else:
                st.warning("Column 'sentiment' not found")

        with col2:
            st.markdown("#### 🚨 Ticket Urgency Breakdown")
            if 'urgency' in df.columns:
                fig_urgency = create_urgency_chart(df)
                st.plotly_chart(fig_urgency, use_container_width=True)
            else:
                st.warning("Column 'urgency' not found")

        # Summary metrics at bottom
        st.markdown("---")
        st.markdown("#### 📊 Summary Metrics")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Tickets", f"{len(df):,}")

        with col2:
            if 'urgency' in df.columns:
                blocker_count = len(df[df['urgency'].str.lower() == 'blocker'])
                st.metric("🔴 Blockers", blocker_count)

        with col3:
            if 'affects_business_flow' in df.columns:
                business_impact = len(df[df['affects_business_flow'] == True])
                st.metric("💼 Business Impact", business_impact)

        with col4:
            if 'is_recurrent' in df.columns:
                recurrent = len(df[df['is_recurrent'] == True])
                st.metric("🔄 Recurrent", recurrent)

        with col5:
            if 'sentiment' in df.columns:
                negative = len(df[df['sentiment'].str.lower() == 'negativ'])
                st.metric("😟 Negative", negative)

    with tab2:
        st.markdown("### 💼 Business Impact Analysis")

        # Component 1: Business Flow Impact Gauge
        st.markdown("#### 💥 Business Flow Impact")

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
                st.markdown("##### Impact Summary")
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
        st.markdown("#### 🔄 Recurring Issues")

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
        st.markdown("#### 🏢 Problem Distribution by Platform")

        if 'platform' in df.columns:
            col1, col2 = st.columns([3, 1])

            with col2:
                chart_type = st.radio(
                    "Chart Type",
                    options=['pie', 'treemap'],
                    format_func=lambda x: 'Pie Chart' if x == 'pie' else 'Treemap',
                    key="platform_chart_type_biz"
                )

            with col1:
                fig_platform = create_platform_distribution_chart(df, chart_type)
                st.plotly_chart(fig_platform, use_container_width=True)

            # Platform breakdown table
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
        st.markdown("#### 🚨 Most Critical Open Issues")

        if 'urgency' in df.columns and 'affects_business_flow' in df.columns:
            critical_df = get_critical_open_issues(df)

            if len(critical_df) > 0:
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
                        max_date = df['created_at'].max()
                        days_old = (max_date - oldest_date).days
                        st.metric("Oldest Issue", f"{days_old} days")

                st.markdown("---")

                display_df = critical_df.copy()

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

    with tab3:
        st.markdown("### 📊 Executive Summary")
        st.markdown("*High-level metrics and trends for executive decision-making*")

        # Top-level KPIs
        st.markdown("#### 📊 Key Performance Indicators")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📊 Total Tickets", f"{len(df):,}")

        with col2:
            if 'urgency' in df.columns and 'affects_business_flow' in df.columns:
                critical_issues = len(df[(df['urgency'].str.lower() == 'blocker') & (df['affects_business_flow'] == True)])
                st.metric("🔴 Critical Issues", critical_issues)

        with col3:
            if 'affects_business_flow' in df.columns:
                business_impact_issues = len(df[df['affects_business_flow'] == True])
                st.metric("💼 Business Impact", business_impact_issues)

        with col4:
            if 'created_at' in df.columns:
                # Calculate 7-day trend using the data's max date
                max_date = df['created_at'].max()
                last_7_days = df[df['created_at'] >= (max_date - pd.Timedelta(days=7))]
                prev_7_days = df[(df['created_at'] >= (max_date - pd.Timedelta(days=14))) & (df['created_at'] < (max_date - pd.Timedelta(days=7)))]

                trend_pct = 0
                if len(prev_7_days) > 0:
                    trend_pct = ((len(last_7_days) - len(prev_7_days)) / len(prev_7_days)) * 100

                st.metric("📈 Trend (7d)", f"{trend_pct:+.1f}%", delta=f"{trend_pct:+.1f}%")

        st.markdown("---")

        # Two-column layout for insights
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 Top 5 Pain Points")

            if 'pain_point' in df.columns:
                pain_points = df['pain_point'].value_counts().head(5)

                for idx, (pain, count) in enumerate(pain_points.items(), 1):
                    st.markdown(f"{idx}. **{pain}** ({count} tickets)")
            else:
                st.info("Pain point data not available")

        with col2:
            st.markdown("#### 🏥 Health Metrics")

            # Resolution rate
            if 'closed_at' in df.columns:
                closed_count = len(df[df['closed_at'].notna()])
                total_count = len(df)
                resolution_rate = (closed_count / total_count * 100) if total_count > 0 else 0
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")

            # Sentiment score
            if 'sentiment' in df.columns:
                sentiment_counts = df['sentiment'].value_counts()
                total_sentiment = sentiment_counts.sum()
                if total_sentiment > 0:
                    positive = sentiment_counts.get('pozitiv', 0)
                    neutral = sentiment_counts.get('neutru', 0)
                    negative = sentiment_counts.get('negativ', 0)

                    # Calculate sentiment score (weighted: +1 for positive, 0 for neutral, -1 for negative)
                    sentiment_score = ((positive - negative) / total_sentiment) * 100
                    st.metric("Sentiment Score", f"{sentiment_score:+.1f}%")

            # Recurring issues percentage
            if 'is_recurrent' in df.columns:
                recurrent_count = len(df[df['is_recurrent'] == True])
                recurrent_pct = (recurrent_count / len(df) * 100) if len(df) > 0 else 0
                st.metric("Recurring Issues", f"{recurrent_pct:.1f}%", delta_color="inverse")

        st.markdown("---")

        # Platform distribution summary
        st.markdown("#### 🏢 Platform Overview")

        if 'platform' in df.columns:
            platform_counts = df['platform'].value_counts().head(5)

            cols = st.columns(len(platform_counts))
            for idx, (platform, count) in enumerate(platform_counts.items()):
                with cols[idx]:
                    pct = (count / len(df) * 100)
                    st.metric(platform, f"{count}", f"{pct:.1f}%")

        st.markdown("---")

        # Ticket volume trend
        if 'created_at' in df.columns:
            st.markdown("#### 📈 Ticket Volume Trend (Last 30 Days)")

            # Filter to last 30 days using the data's max date
            max_date = df['created_at'].max()
            thirty_days_ago = max_date - pd.Timedelta(days=30)
            df_recent = df[df['created_at'] >= thirty_days_ago]

            if len(df_recent) > 0:
                trend_data = df_recent.groupby(
                    pd.Grouper(key='created_at', freq='D')
                ).size().reset_index(name='count')

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend_data['created_at'],
                    y=trend_data['count'],
                    mode='lines+markers',
                    name='Tickets',
                    line=dict(color=COLORS['primary'], width=2),
                    marker=dict(size=6),
                    fill='tozeroy',
                    fillcolor=f'rgba(99, 102, 241, 0.1)',
                    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Tickets: %{y}<extra></extra>'
                ))

                fig.update_layout(
                    xaxis_title='Date',
                    yaxis_title='Number of Tickets',
                    hovermode='x unified',
                    **DARK_TEMPLATE['layout']
                )

                fig.update_xaxes(**AXIS_STYLE)
                fig.update_yaxes(**AXIS_STYLE)

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for the last 30 days")


if __name__ == "__main__":
    main()
