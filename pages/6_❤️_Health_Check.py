"""
Support Health Check Dashboard
High-level overview of customer support health and efficiency
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

st.set_page_config(page_title="Health Check", page_icon="❤️", layout="wide")


def create_volume_trend_chart(df, time_grouping='D'):
    """Create ticket volume trend line chart"""
    # Map time grouping to pandas frequency
    freq_map = {'D': 'D', 'W': 'W-MON', 'M': 'MS'}
    freq_label = {'D': 'Day', 'W': 'Week', 'M': 'Month'}

    # Group by time period
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


def calculate_avg_resolution_time(df):
    """Calculate average time to resolution"""
    # Filter only closed tickets
    closed_tickets = df[df['closed_at'].notna()].copy()

    if len(closed_tickets) == 0:
        return None, None, 0

    # Calculate resolution time in hours
    closed_tickets['resolution_hours'] = (closed_tickets['closed_at'] - closed_tickets['created_at']).dt.total_seconds() / 3600

    avg_hours = closed_tickets['resolution_hours'].mean()

    # Convert to human-readable format
    days = int(avg_hours // 24)
    hours = int(avg_hours % 24)
    minutes = int((avg_hours * 60) % 60)

    if days > 0:
        readable = f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        readable = f"{hours}h {minutes}m"
    else:
        readable = f"{minutes}m"

    # Calculate change from previous period
    # Split data in half by date
    mid_date = closed_tickets['created_at'].min() + (closed_tickets['created_at'].max() - closed_tickets['created_at'].min()) / 2
    previous_period = closed_tickets[closed_tickets['created_at'] < mid_date]
    current_period = closed_tickets[closed_tickets['created_at'] >= mid_date]

    if len(previous_period) > 0 and len(current_period) > 0:
        prev_avg = previous_period['resolution_hours'].mean()
        curr_avg = current_period['resolution_hours'].mean()
        change_pct = ((curr_avg - prev_avg) / prev_avg) * 100
    else:
        change_pct = 0

    return readable, change_pct, len(closed_tickets)


def create_sentiment_chart(df):
    """Create sentiment donut chart"""
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']

    # Color mapping
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

    # Sort by severity
    urgency_order = ['blocker', 'mediu', 'scazut']
    urgency_counts['urgency'] = pd.Categorical(urgency_counts['urgency'], categories=urgency_order, ordered=True)
    urgency_counts = urgency_counts.sort_values('urgency')

    # Color mapping
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


def main():
    # Check if data is loaded
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original.copy()

    # Page header
    st.title("❤️ Support Health Check")
    st.markdown("High-level overview of customer support health and efficiency")

    # Date range filter
    st.markdown("---")
    col1, col2 = st.columns([3, 1])

    with col1:
        if 'created_at' in df.columns:
            date_range = st.date_input(
                "📅 Filter Date Range",
                value=(df['created_at'].min().date(), df['created_at'].max().date()),
                key="health_check_date_range"
            )

            if len(date_range) == 2:
                df = df[(df['created_at'].dt.date >= date_range[0]) & (df['created_at'].dt.date <= date_range[1])]

    st.markdown("---")

    # Component 1: Ticket Volume Trend
    st.markdown("### 📈 Ticket Volume Trend")

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

    st.markdown("---")

    # Component 2: Average Time to Resolution
    st.markdown("### ⏱️ Average Time to Resolution")

    if 'created_at' in df.columns and 'closed_at' in df.columns:
        readable_time, change_pct, closed_count = calculate_avg_resolution_time(df)

        if readable_time:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Average Resolution Time",
                    readable_time,
                    delta=f"{change_pct:+.1f}% from previous period" if change_pct != 0 else None,
                    delta_color="inverse"  # Lower is better
                )

            with col2:
                st.metric("Closed Tickets", f"{closed_count:,}")

            with col3:
                open_count = len(df[df['closed_at'].isna()])
                st.metric("Open Tickets", f"{open_count:,}")
        else:
            st.info("No closed tickets in the selected period")
    else:
        st.warning("Columns 'created_at' or 'closed_at' not found")

    st.markdown("---")

    # Component 3 & 4: Sentiment and Urgency (side by side)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 😊 Customer Sentiment")
        if 'sentiment' in df.columns:
            fig_sentiment = create_sentiment_chart(df)
            st.plotly_chart(fig_sentiment, use_container_width=True)
        else:
            st.warning("Column 'sentiment' not found")

    with col2:
        st.markdown("### 🚨 Ticket Urgency Breakdown")
        if 'urgency' in df.columns:
            fig_urgency = create_urgency_chart(df)
            st.plotly_chart(fig_urgency, use_container_width=True)
        else:
            st.warning("Column 'urgency' not found")

    # Summary metrics at bottom
    st.markdown("---")
    st.markdown("### 📊 Summary Metrics")

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


if __name__ == "__main__":
    main()
