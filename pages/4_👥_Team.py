"""
Team Performance Page - Agent performance metrics and analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor
from utils.filters import render_sidebar_filters, show_filter_summary
from utils.charts import COLORS

import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Team Performance - SmartBill Analytics",
    page_icon="👥",
    layout="wide"
)


def extract_agent_names(conversation_text: str):
    """Extract agent names from conversation field"""
    if pd.isna(conversation_text):
        return []

    # Simple pattern matching for common agent name patterns
    # This is a placeholder - adjust based on actual data format
    agents = []

    # Try to find patterns like "Agent: Name" or "Name replied"
    patterns = [
        r'Agent[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)',
        r'([A-Z][a-z]+\s[A-Z][a-z]+)\s+replied',
        r'Assignee[:\s]+([A-Z][a-z]+\s[A-Z][a-z]+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, str(conversation_text))
        agents.extend(matches)

    return list(set(agents))  # Return unique names


def create_agent_dataframe(df: pd.DataFrame):
    """Create agent performance dataframe"""

    # Extract agents from conversation field
    if 'conversation' not in df.columns:
        return None

    agent_data = []

    # For simplicity, we'll create mock agent assignments
    # In real scenario, this should be extracted from actual conversation data
    mock_agents = ['Agent A', 'Agent B', 'Agent C', 'Agent D', 'Agent E']

    for agent in mock_agents:
        # Randomly assign tickets to agents for demo
        # In production, extract from conversation field
        agent_tickets = df.sample(frac=0.2)  # Each agent handles ~20% of tickets

        if len(agent_tickets) == 0:
            continue

        metrics = {
            'Agent': agent,
            'Total Tickets': len(agent_tickets),
            'Avg Resolution Time (h)': agent_tickets['resolution_time_hours'].mean() if 'resolution_time_hours' in agent_tickets.columns else 0,
            'Blockers': len(agent_tickets[agent_tickets['urgency'] == 'blocker']) if 'urgency' in agent_tickets.columns else 0,
            'Positive Sentiment': len(agent_tickets[agent_tickets['sentiment'] == 'pozitiv']) if 'sentiment' in agent_tickets.columns else 0,
            'Satisfaction %': (len(agent_tickets[agent_tickets['sentiment'] == 'pozitiv']) / len(agent_tickets) * 100) if 'sentiment' in agent_tickets.columns and len(agent_tickets) > 0 else 0
        }

        agent_data.append(metrics)

    return pd.DataFrame(agent_data)


def create_agent_leaderboard(agent_df: pd.DataFrame):
    """Create leaderboard visualization"""

    if agent_df is None or len(agent_df) == 0:
        return None

    # Sort by total tickets
    agent_df_sorted = agent_df.sort_values('Total Tickets', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=agent_df_sorted['Total Tickets'],
        y=agent_df_sorted['Agent'],
        orientation='h',
        marker=dict(
            color=agent_df_sorted['Total Tickets'],
            colorscale='Greens',
            showscale=True
        ),
        text=agent_df_sorted['Total Tickets'],
        textposition='auto',
    ))

    fig.update_layout(
        title='Leaderboard - Tickets Procesate per Agent',
        xaxis_title='Număr Tickets',
        yaxis_title='Agent',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=400
    )

    return fig


def create_satisfaction_chart(agent_df: pd.DataFrame):
    """Create satisfaction comparison chart"""

    if agent_df is None or len(agent_df) == 0:
        return None

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=agent_df['Agent'],
        y=agent_df['Satisfaction %'],
        mode='markers+lines',
        marker=dict(
            size=15,
            color=agent_df['Satisfaction %'],
            colorscale='RdYlGn',
            showscale=True,
            cmin=0,
            cmax=100
        ),
        line=dict(color=COLORS['primary'], width=2)
    ))

    # Add average line
    avg_satisfaction = agent_df['Satisfaction %'].mean()
    fig.add_hline(y=avg_satisfaction, line_dash="dash", line_color=COLORS['warning'],
                  annotation_text=f"Media: {avg_satisfaction:.1f}%")

    fig.update_layout(
        title='Satisfacție Clienți per Agent (%)',
        xaxis_title='Agent',
        yaxis_title='Satisfacție (%)',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        yaxis=dict(range=[0, 105]),
        height=400
    )

    return fig


def create_resolution_time_chart(agent_df: pd.DataFrame):
    """Create resolution time comparison"""

    if agent_df is None or len(agent_df) == 0:
        return None

    agent_df_sorted = agent_df.sort_values('Avg Resolution Time (h)')

    colors = [COLORS['success'] if x < agent_df['Avg Resolution Time (h)'].mean()
             else COLORS['danger'] for x in agent_df_sorted['Avg Resolution Time (h)']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=agent_df_sorted['Agent'],
        y=agent_df_sorted['Avg Resolution Time (h)'],
        marker_color=colors,
        text=agent_df_sorted['Avg Resolution Time (h)'].round(1),
        textposition='auto',
    ))

    avg_time = agent_df['Avg Resolution Time (h)'].mean()
    fig.add_hline(y=avg_time, line_dash="dash", line_color=COLORS['warning'],
                  annotation_text=f"Media: {avg_time:.1f}h")

    fig.update_layout(
        title='Timp Mediu Rezolvare per Agent',
        xaxis_title='Agent',
        yaxis_title='Timp (ore)',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=400
    )

    return fig


def create_workload_distribution(agent_df: pd.DataFrame):
    """Create workload distribution pie chart"""

    if agent_df is None or len(agent_df) == 0:
        return None

    fig = go.Figure(data=[go.Pie(
        labels=agent_df['Agent'],
        values=agent_df['Total Tickets'],
        hole=0.4,
        marker=dict(
            colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent'],
                   COLORS['info'], COLORS['success']]
        )
    )])

    fig.update_layout(
        title='Distribuția Workload-ului între Agenți',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=400
    )

    return fig


def create_activity_timeline(df: pd.DataFrame):
    """Create timeline of agent activity"""

    if 'created_hour' not in df.columns:
        return None

    hourly_activity = df.groupby('created_hour').size().reset_index(name='count')

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hourly_activity['created_hour'],
        y=hourly_activity['count'],
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color=COLORS['primary'], width=2),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title='Activity Timeline - Tickets per Oră',
        xaxis_title='Ora din Zi',
        yaxis_title='Număr Tickets',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=400,
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )

    return fig


def main():
    """Main team performance function"""

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
    st.title("👥 Team Performance")
    st.markdown("### Analiza performanței echipei de suport")

    st.markdown("---")

    # Show filter summary
    show_filter_summary(df_original, df_filtered)

    st.markdown("---")

    # Check if we have data
    if len(df_filtered) == 0:
        st.warning("⚠️ Nu există date pentru filtrele selectate.")
        return

    # Info message about agent data
    st.info("""
    ℹ️ **Notă:** Datele despre agenți sunt generate pentru demonstrație.
    În producție, aceștia ar fi extrași din câmpul 'conversation' sau dintr-o coloană dedicată 'agent_name'.
    """)

    # Create agent performance dataframe
    agent_df = create_agent_dataframe(df_filtered)

    if agent_df is None or len(agent_df) == 0:
        st.warning("Nu s-au putut extrage date despre agenți")
        return

    st.markdown("---")

    # Team Overview Metrics
    st.subheader("📊 Overview Echipă")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total Agenți", len(agent_df))

    with col2:
        avg_tickets = agent_df['Total Tickets'].mean()
        st.metric("📊 Media Tickets/Agent", f"{avg_tickets:.0f}")

    with col3:
        avg_resolution = agent_df['Avg Resolution Time (h)'].mean()
        st.metric("⏱️ Timp Mediu Rezolvare", f"{avg_resolution:.1f}h")

    with col4:
        avg_satisfaction = agent_df['Satisfaction %'].mean()
        st.metric("😊 Satisfacție Medie", f"{avg_satisfaction:.1f}%")

    st.markdown("---")

    # Leaderboard
    st.subheader("🏆 Leaderboard")

    fig_leaderboard = create_agent_leaderboard(agent_df)
    if fig_leaderboard:
        st.plotly_chart(fig_leaderboard, use_container_width=True)

    st.markdown("---")

    # Performance Metrics
    st.subheader("📈 Metrici Performanță")

    col1, col2 = st.columns(2)

    with col1:
        fig_satisfaction = create_satisfaction_chart(agent_df)
        if fig_satisfaction:
            st.plotly_chart(fig_satisfaction, use_container_width=True)

    with col2:
        fig_resolution = create_resolution_time_chart(agent_df)
        if fig_resolution:
            st.plotly_chart(fig_resolution, use_container_width=True)

    st.markdown("---")

    # Workload Distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Distribuție Workload")
        fig_workload = create_workload_distribution(agent_df)
        if fig_workload:
            st.plotly_chart(fig_workload, use_container_width=True)

    with col2:
        st.subheader("🕐 Activity Timeline")
        fig_timeline = create_activity_timeline(df_filtered)
        if fig_timeline:
            st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("---")

    # Detailed Agent Table
    st.subheader("📋 Tabel Detaliat Performanță Agenți")

    # Style the dataframe
    def highlight_best_performer(s):
        """Highlight best performer in green"""
        is_max = s == s.max()
        return ['background-color: #10B98166' if v else '' for v in is_max]

    # Display styled dataframe
    styled_df = agent_df.style.apply(highlight_best_performer, subset=['Total Tickets', 'Satisfaction %'])

    st.dataframe(
        agent_df.sort_values('Total Tickets', ascending=False),
        use_container_width=True,
        hide_index=True
    )

    # Agent comparison selector
    st.markdown("---")
    st.subheader("🔍 Comparație Agenți")

    col1, col2 = st.columns(2)

    with col1:
        agent1 = st.selectbox("Selectează primul agent:", options=agent_df['Agent'].tolist())

    with col2:
        agent2 = st.selectbox("Selectează al doilea agent:", options=agent_df['Agent'].tolist(), index=1 if len(agent_df) > 1 else 0)

    if agent1 and agent2:
        agent1_data = agent_df[agent_df['Agent'] == agent1].iloc[0]
        agent2_data = agent_df[agent_df['Agent'] == agent2].iloc[0]

        # Comparison metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Tickets",
                f"{agent1_data['Total Tickets']}",
                delta=f"{agent1_data['Total Tickets'] - agent2_data['Total Tickets']:+.0f} vs {agent2}"
            )

        with col2:
            st.metric(
                "Timp Rezolvare",
                f"{agent1_data['Avg Resolution Time (h)']:.1f}h",
                delta=f"{agent1_data['Avg Resolution Time (h)'] - agent2_data['Avg Resolution Time (h)']:+.1f}h vs {agent2}",
                delta_color="inverse"
            )

        with col3:
            st.metric(
                "Blockers",
                f"{agent1_data['Blockers']}",
                delta=f"{agent1_data['Blockers'] - agent2_data['Blockers']:+.0f} vs {agent2}",
                delta_color="inverse"
            )

        with col4:
            st.metric(
                "Satisfacție",
                f"{agent1_data['Satisfaction %']:.1f}%",
                delta=f"{agent1_data['Satisfaction %'] - agent2_data['Satisfaction %']:+.1f}% vs {agent2}"
            )

    st.markdown("---")

    # Export
    st.subheader("📤 Export")

    if st.button("📥 Export Date Performanță ca CSV", use_container_width=True):
        csv = agent_df.to_csv(index=False)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv,
            file_name=f"team_performance_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
