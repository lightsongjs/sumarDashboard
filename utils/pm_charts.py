"""
PM Charts Module
Chart generators pentru Product Manager insights
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict


COLORS = {
    'primary': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'info': '#3B82F6',
    'secondary': '#6366F1'
}

DARK_THEME = {
    'paper_bgcolor': '#0E1117',
    'plot_bgcolor': '#262730',
    'font': {'color': '#FAFAFA'}
}


def create_feature_gap_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart pentru top feature gaps"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['priority_score'],
        y=df['pain_point'],
        orientation='h',
        marker_color=COLORS['primary'],
        text=df['count'],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Priority Score: %{x}<br>Tickets: %{text}<extra></extra>'
    ))

    fig.update_layout(
        title='Top Feature Gaps (by Priority Score)',
        xaxis_title='Priority Score',
        yaxis_title='',
        **DARK_THEME,
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    return fig


def create_sentiment_pie(sentiment_data: Dict) -> go.Figure:
    """Pie chart pentru sentiment distribution"""
    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=['Pozitiv', 'Neutru', 'Negativ'],
        values=[sentiment_data.get('pozitiv', 0), sentiment_data.get('neutru', 0), sentiment_data.get('negativ', 0)],
        marker_colors=[COLORS['primary'], COLORS['warning'], COLORS['danger']],
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>%{value} tickete<br>%{percent}<extra></extra>'
    ))

    fig.update_layout(
        title='Sentiment Distribution',
        **DARK_THEME,
        height=400
    )

    return fig


def create_platform_health_chart(df: pd.DataFrame) -> go.Figure:
    """Radar chart pentru platform health"""
    if df.empty:
        return go.Figure()

    fig = go.Figure()

    for idx, row in df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row['health_score'], 100 - (row['bugs'] / row['total_tickets'] * 100),
               100 - (row['blockers'] / row['total_tickets'] * 100),
               100 - (row['negative_sentiment'] / row['total_tickets'] * 100)],
            theta=['Health Score', 'Bug Rate', 'Blocker Rate', 'Sentiment'],
            fill='toself',
            name=row['platform'].title()
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        **DARK_THEME,
        title='Platform Health Comparison',
        height=500
    )

    return fig


def create_resolution_time_chart(metrics: Dict) -> go.Figure:
    """Bar chart pentru resolution time per urgency"""
    urgencies = []
    times = []

    for key, value in metrics.items():
        if key.startswith('avg_resolution_'):
            urgency = key.replace('avg_resolution_', '')
            urgencies.append(urgency.title())
            times.append(value)

    colors = [COLORS['danger'] if u == 'Blocker' else COLORS['warning'] if u == 'Mediu' else COLORS['primary'] for u in urgencies]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=urgencies,
        y=times,
        marker_color=colors,
        text=[f"{t:.1f}h" for t in times],
        textposition='auto'
    ))

    fig.update_layout(
        title='Average Resolution Time by Urgency',
        xaxis_title='Urgency Level',
        yaxis_title='Hours',
        **DARK_THEME,
        height=400
    )

    return fig


def create_trend_chart(df: pd.DataFrame, date_col: str = 'created_at') -> go.Figure:
    """Line chart pentru ticket trends"""
    if date_col not in df.columns:
        return go.Figure()

    df_copy = df.copy()
    df_copy['date'] = df_copy[date_col].dt.date
    trend = df_copy.groupby('date').size().reset_index(name='count')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend['date'],
        y=trend['count'],
        mode='lines+markers',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))

    fig.update_layout(
        title='Ticket Volume Trend',
        xaxis_title='Date',
        yaxis_title='Number of Tickets',
        **DARK_THEME,
        height=400
    )

    return fig


def create_gauge_chart(value: float, title: str, max_value: float = 100) -> go.Figure:
    """Gauge chart pentru metrics"""
    color = COLORS['primary'] if value >= 70 else COLORS['warning'] if value >= 40 else COLORS['danger']

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [40, 70], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [70, max_value], 'color': 'rgba(16, 185, 129, 0.2)'}
            ],
            'threshold': {
                'line': {'color': 'white', 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(
        **DARK_THEME,
        height=300
    )

    return fig


def create_heatmap(df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
    """Heatmap pentru platform x problem_type"""
    if x_col not in df.columns or y_col not in df.columns:
        return go.Figure()

    pivot = df.groupby([y_col, x_col]).size().unstack(fill_value=0)

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Greens',
        text=pivot.values,
        texttemplate='%{text}',
        textfont={"size": 12}
    ))

    fig.update_layout(
        title=f'{y_col.title()} vs {x_col.title()} Distribution',
        **DARK_THEME,
        height=500
    )

    return fig
