"""
Charts Module for SmartBill Support Analytics
Provides functions to create interactive Plotly charts
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List


# SmartBill brand colors
COLORS = {
    'primary': '#10B981',
    'primary_dark': '#059669',
    'secondary': '#6366F1',
    'accent': '#F59E0B',
    'danger': '#EF4444',
    'success': '#10B981',
    'warning': '#F59E0B',
    'info': '#3B82F6',
    'dark': '#111827',
    'gray': '#6B7280'
}

# Dark theme template
DARK_TEMPLATE = {
    'layout': {
        'paper_bgcolor': '#0E1117',
        'plot_bgcolor': '#262730',
        'font': {'color': '#FAFAFA'},
    }
}

# Axis styling to be applied separately
AXIS_STYLE = {
    'gridcolor': '#374151',
    'linecolor': '#374151'
}


def create_trend_chart(df: pd.DataFrame, date_col: str = 'created_date',
                       title: str = 'Tickets Over Time') -> go.Figure:
    """Create a bar chart showing ticket trends over time"""

    # Group by date
    trend_data = df.groupby(date_col).size().reset_index(name='count')
    trend_data = trend_data.sort_values(date_col)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=trend_data[date_col],
        y=trend_data['count'],
        marker_color=COLORS['primary'],
        hovertemplate='<b>%{x}</b><br>Tickets: %{y}<extra></extra>',
        name='Tickets'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Number of Tickets',
        **DARK_TEMPLATE['layout'],
        hovermode='x unified',
        showlegend=False
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_platform_distribution(df: pd.DataFrame,
                                 platform_col: str = 'platform') -> go.Figure:
    """Create a donut chart showing platform distribution"""

    platform_counts = df[platform_col].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=platform_counts.index,
        values=platform_counts.values,
        hole=0.4,
        marker=dict(
            colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent'],
                   COLORS['info'], COLORS['warning'], COLORS['danger']]
        ),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title='Distribution by Platform',
        **DARK_TEMPLATE['layout'],
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5)
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_heatmap(df: pd.DataFrame,
                   hour_col: str = 'created_hour',
                   day_col: str = 'created_day_of_week') -> go.Figure:
    """Create heatmap showing tickets by hour and day of week"""

    # Create pivot table
    heatmap_data = df.groupby([day_col, hour_col]).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index=day_col, columns=hour_col, values='count').fillna(0)

    # Reorder days
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex([day for day in days_order if day in heatmap_pivot.index])

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='Greens',
        hovertemplate='Day: %{y}<br>Hour: %{x}<br>Tickets: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title='Ticket Volume by Day and Hour',
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        **DARK_TEMPLATE['layout']
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_urgency_trend(df: pd.DataFrame,
                        date_col: str = 'created_date',
                        urgency_col: str = 'urgency') -> go.Figure:
    """Create stacked bar chart for urgency levels over time"""

    urgency_trend = df.groupby([date_col, urgency_col]).size().reset_index(name='count')

    fig = go.Figure()

    urgency_colors = {
        'blocker': COLORS['danger'],
        'mediu': COLORS['warning'],
        'scazut': COLORS['info']
    }

    for urgency in df[urgency_col].unique():
        data = urgency_trend[urgency_trend[urgency_col] == urgency]
        fig.add_trace(go.Bar(
            x=data[date_col],
            y=data['count'],
            name=urgency,
            marker_color=urgency_colors.get(urgency, COLORS['gray']),
            hovertemplate=f'<b>{urgency}</b><br>Date: %{{x}}<br>Count: %{{y}}<extra></extra>'
        ))

    fig.update_layout(
        title='Urgency Levels Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Tickets',
        barmode='stack',
        **DARK_TEMPLATE['layout']
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_sentiment_trend(df: pd.DataFrame,
                          date_col: str = 'created_date',
                          sentiment_col: str = 'sentiment') -> go.Figure:
    """Create line chart showing sentiment trends with moving average"""

    # Calculate daily sentiment scores (pozitiv=1, neutru=0, negativ=-1)
    sentiment_scores = {
        'pozitiv': 1,
        'neutru': 0,
        'negativ': -1
    }

    df_copy = df.copy()
    df_copy['sentiment_score'] = df_copy[sentiment_col].map(sentiment_scores)

    daily_sentiment = df_copy.groupby(date_col)['sentiment_score'].mean().reset_index()
    daily_sentiment = daily_sentiment.sort_values(date_col)

    # Calculate 7-day moving average
    daily_sentiment['ma_7'] = daily_sentiment['sentiment_score'].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_sentiment[date_col],
        y=daily_sentiment['sentiment_score'],
        mode='lines',
        name='Daily Sentiment',
        line=dict(color=COLORS['gray'], width=1),
        opacity=0.5
    ))

    fig.add_trace(go.Scatter(
        x=daily_sentiment[date_col],
        y=daily_sentiment['ma_7'],
        mode='lines',
        name='7-Day Average',
        line=dict(color=COLORS['primary'], width=3)
    ))

    fig.update_layout(
        title='Sentiment Trend (7-Day Moving Average)',
        xaxis_title='Date',
        yaxis_title='Sentiment Score',
        **DARK_TEMPLATE['layout']
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE, range=[-1.1, 1.1])

    return fig


def create_problem_type_chart(df: pd.DataFrame,
                              problem_col: str = 'problem_type') -> go.Figure:
    """Create donut chart for problem types"""

    problem_counts = df[problem_col].value_counts()

    fig = go.Figure(data=[go.Pie(
        labels=problem_counts.index,
        values=problem_counts.values,
        hole=0.5,
        marker=dict(
            colors=[COLORS['danger'], COLORS['warning'], COLORS['info'],
                   COLORS['secondary'], COLORS['primary'], COLORS['accent']]
        ),
        textposition='inside',
        textinfo='percent+label'
    )])

    fig.update_layout(
        title='Distribution by Problem Type',
        **DARK_TEMPLATE['layout'],
        showlegend=True
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_pareto_chart(df: pd.DataFrame,
                       category_col: str = 'area',
                       title: str = 'Pareto Analysis') -> go.Figure:
    """Create Pareto chart (80/20 analysis)"""

    category_counts = df[category_col].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    category_counts = category_counts.sort_values('count', ascending=False)

    category_counts['cumulative_pct'] = (category_counts['count'].cumsum() / category_counts['count'].sum()) * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=category_counts['category'],
            y=category_counts['count'],
            name='Count',
            marker_color=COLORS['primary']
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=category_counts['category'],
            y=category_counts['cumulative_pct'],
            name='Cumulative %',
            mode='lines+markers',
            line=dict(color=COLORS['danger'], width=2),
            marker=dict(size=8)
        ),
        secondary_y=True
    )

    # Add 80% line
    fig.add_hline(y=80, line_dash="dash", line_color=COLORS['warning'],
                  secondary_y=True, annotation_text="80%")

    fig.update_layout(
        title=title,
        xaxis_title='Category',
        **DARK_TEMPLATE['layout'],
        hovermode='x unified'
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(title_text="Count", secondary_y=False, **AXIS_STYLE)
    fig.update_yaxes(title_text="Cumulative %", secondary_y=True, range=[0, 105], **AXIS_STYLE)

    return fig


def create_sankey_diagram(df: pd.DataFrame,
                         source_col: str = 'platform',
                         target_col: str = 'area',
                         value_col: str = 'problem_type') -> go.Figure:
    """Create Sankey diagram showing flow between categories"""

    # Create relationships
    flow1 = df.groupby([source_col, target_col]).size().reset_index(name='count')

    # Get unique labels
    all_labels = list(pd.concat([flow1[source_col], flow1[target_col]]).unique())
    label_map = {label: idx for idx, label in enumerate(all_labels)}

    # Create links
    source_indices = [label_map[src] for src in flow1[source_col]]
    target_indices = [label_map[tgt] for tgt in flow1[target_col]]
    values = flow1['count'].tolist()

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_labels,
            color=COLORS['primary']
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color='rgba(16, 185, 129, 0.3)'
        )
    )])

    fig.update_layout(
        title='Flow: Platform → Area',
        font=dict(size=10, color='white'),
        **DARK_TEMPLATE['layout']
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_comparison_chart(df1: pd.DataFrame, df2: pd.DataFrame,
                           label1: str = 'Current Period',
                           label2: str = 'Previous Period',
                           metric: str = 'count') -> go.Figure:
    """Create comparison chart between two periods"""

    categories = ['Total Tickets', 'Blockers', 'Avg Resolution (hrs)', 'Satisfaction %']

    # Calculate metrics for both periods
    values1 = [
        len(df1),
        len(df1[df1['urgency'] == 'blocker']) if 'urgency' in df1.columns else 0,
        df1['resolution_time_hours'].mean() if 'resolution_time_hours' in df1.columns else 0,
        (len(df1[df1['sentiment'] == 'pozitiv']) / len(df1) * 100) if 'sentiment' in df1.columns and len(df1) > 0 else 0
    ]

    values2 = [
        len(df2),
        len(df2[df2['urgency'] == 'blocker']) if 'urgency' in df2.columns else 0,
        df2['resolution_time_hours'].mean() if 'resolution_time_hours' in df2.columns else 0,
        (len(df2[df2['sentiment'] == 'pozitiv']) / len(df2) * 100) if 'sentiment' in df2.columns and len(df2) > 0 else 0
    ]

    fig = go.Figure(data=[
        go.Bar(name=label1, x=categories, y=values1, marker_color=COLORS['primary']),
        go.Bar(name=label2, x=categories, y=values2, marker_color=COLORS['secondary'])
    ])

    fig.update_layout(
        title='Period Comparison',
        barmode='group',
        **DARK_TEMPLATE['layout'],
        yaxis_title='Value'
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_resolution_time_boxplot(df: pd.DataFrame,
                                   category_col: str = 'platform',
                                   time_col: str = 'resolution_time_hours') -> go.Figure:
    """Create box plot for resolution times by category"""

    fig = go.Figure()

    for category in df[category_col].unique():
        category_data = df[df[category_col] == category][time_col].dropna()

        fig.add_trace(go.Box(
            y=category_data,
            name=category,
            boxmean='sd',
            marker_color=COLORS['primary']
        ))

    fig.update_layout(
        title='Resolution Time Distribution by Platform',
        xaxis_title='Platform',
        yaxis_title='Resolution Time (hours)',
        **DARK_TEMPLATE['layout']
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_metric_card_html(title: str, value: str, delta: str = None,
                           delta_color: str = 'green', icon: str = '📊') -> str:
    """Generate HTML for a metric card"""

    delta_html = ''
    if delta:
        color = COLORS.get(delta_color, COLORS['gray'])
        delta_html = f'<div style="color: {color}; font-size: 14px; margin-top: 5px;">{delta}</div>'

    html = f"""
    <div style="background: #262730; padding: 20px; border-radius: 10px; border-left: 4px solid {COLORS['primary']};">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <span style="font-size: 24px;">{icon}</span>
            <span style="color: #9CA3AF; font-size: 14px; text-transform: uppercase;">{title}</span>
        </div>
        <div style="font-size: 32px; font-weight: bold; color: #FAFAFA;">{value}</div>
        {delta_html}
    </div>
    """

    return html
