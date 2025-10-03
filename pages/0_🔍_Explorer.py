"""
SmartBill Support Explorer
Pagină simplificată cu mega filtrare și vizualizare tickete
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor

st.set_page_config(page_title="Explorer", page_icon="🔍", layout="wide")


def initialize_filters():
    """Initialize all filter states"""
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            # Search
            'global_search': '',

            # Date & Time
            'date_from': None,
            'date_to': None,
            'ticket_status': 'toate',  # toate, deschise, închise

            # Platform & Area
            'platforms': [],
            'areas': [],
            'area_search': '',

            # Type & Taxonomy
            'tip': [],
            'taxonomy': [],

            # Severity
            'urgency': [],
            'affects_business': None,  # None, True, False
            'is_recurrent': None,
            'agent_intervention': None,

            # Client & Sentiment
            'sentiment': [],
            'apreciere': [],
            'mailbox': [],

            # Problem Type
            'problem_type': [],
            'pain_point_search': '',

            # Technical
            'integration': [],
            'mentioned_features': '',
            'error_messages': '',
        }


def reset_filters():
    """Reset all filters"""
    st.session_state.filters = {
        'global_search': '',
        'date_from': None,
        'date_to': None,
        'ticket_status': 'toate',
        'platforms': [],
        'areas': [],
        'area_search': '',
        'tip': [],
        'taxonomy': [],
        'urgency': [],
        'affects_business': None,
        'is_recurrent': None,
        'agent_intervention': None,
        'sentiment': [],
        'apreciere': [],
        'mailbox': [],
        'problem_type': [],
        'pain_point_search': '',
        'integration': [],
        'mentioned_features': '',
        'error_messages': '',
    }
    st.rerun()


def apply_filters(df, filters):
    """Apply all active filters to dataframe"""
    filtered_df = df.copy()

    # Global search
    if filters['global_search']:
        search_term = filters['global_search'].lower()
        mask = (
            filtered_df['pain_point'].astype(str).str.lower().str.contains(search_term, na=False) |
            filtered_df['summary'].astype(str).str.lower().str.contains(search_term, na=False) |
            filtered_df['user_goal'].astype(str).str.lower().str.contains(search_term, na=False) |
            filtered_df['conversation'].astype(str).str.lower().str.contains(search_term, na=False)
        )
        filtered_df = filtered_df[mask]

    # Date filters
    if filters['date_from']:
        filtered_df = filtered_df[filtered_df['created_at'] >= pd.Timestamp(filters['date_from'])]
    if filters['date_to']:
        filtered_df = filtered_df[filtered_df['created_at'] <= pd.Timestamp(filters['date_to'])]

    # Ticket status
    if filters['ticket_status'] == 'închise':
        filtered_df = filtered_df[filtered_df['is_closed'] == True]
    elif filters['ticket_status'] == 'deschise':
        filtered_df = filtered_df[filtered_df['is_closed'] == False]

    # Platform
    if filters['platforms']:
        filtered_df = filtered_df[filtered_df['platform'].isin(filters['platforms'])]

    # Area
    if filters['areas']:
        filtered_df = filtered_df[filtered_df['area'].isin(filters['areas'])]
    if filters['area_search']:
        search_term = filters['area_search'].lower()
        filtered_df = filtered_df[filtered_df['area'].astype(str).str.lower().str.contains(search_term, na=False)]

    # Type
    if filters['tip']:
        filtered_df = filtered_df[filtered_df['tip'].isin(filters['tip'])]
    if filters['taxonomy']:
        filtered_df = filtered_df[filtered_df['taxonomy'].isin(filters['taxonomy'])]

    # Severity
    if filters['urgency']:
        filtered_df = filtered_df[filtered_df['urgency'].isin(filters['urgency'])]
    if filters['affects_business'] is not None:
        filtered_df = filtered_df[filtered_df['affects_business_flow'] == filters['affects_business']]
    if filters['is_recurrent'] is not None:
        filtered_df = filtered_df[filtered_df['is_recurrent'] == filters['is_recurrent']]
    if filters['agent_intervention'] is not None:
        filtered_df = filtered_df[filtered_df['agent_intervention_needed'] == filters['agent_intervention']]

    # Sentiment
    if filters['sentiment']:
        filtered_df = filtered_df[filtered_df['sentiment'].isin(filters['sentiment'])]
    if filters['apreciere']:
        filtered_df = filtered_df[filtered_df['apreciere_parere_support'].isin(filters['apreciere'])]
    if filters['mailbox']:
        filtered_df = filtered_df[filtered_df['mailbox_name'].isin(filters['mailbox'])]

    # Problem type
    if filters['problem_type']:
        filtered_df = filtered_df[filtered_df['problem_type'].isin(filters['problem_type'])]
    if filters['pain_point_search']:
        search_term = filters['pain_point_search'].lower()
        filtered_df = filtered_df[filtered_df['pain_point'].astype(str).str.lower().str.contains(search_term, na=False)]

    # Technical
    if filters['integration']:
        filtered_df = filtered_df[filtered_df['integration'].isin(filters['integration'])]
    if filters['mentioned_features']:
        search_term = filters['mentioned_features'].lower()
        filtered_df = filtered_df[filtered_df['mentioned_features'].astype(str).str.lower().str.contains(search_term, na=False)]
    if filters['error_messages']:
        search_term = filters['error_messages'].lower()
        filtered_df = filtered_df[filtered_df['specific_error_messages'].astype(str).str.lower().str.contains(search_term, na=False)]

    return filtered_df


def get_count(df, column, value):
    """Get count for a specific filter value"""
    if pd.isna(value) or value == '':
        return 0
    return len(df[df[column] == value]) if column in df.columns else 0


def render_sidebar_filters(df):
    """Render all filters in sidebar"""
    st.sidebar.title("🔍 FILTRE AVANSATE")

    filters = st.session_state.filters

    # Global search
    st.sidebar.markdown("### 🔎 Caută în toate")
    filters['global_search'] = st.sidebar.text_input(
        "Caută cuvinte cheie",
        value=filters['global_search'],
        placeholder="ex: autorizare spv",
        key="global_search"
    )

    st.sidebar.markdown("---")

    # Date & Time
    st.sidebar.markdown("### 📅 DATE ȘI TIMP")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        filters['date_from'] = st.date_input(
            "De la",
            value=filters['date_from'],
            key="date_from"
        )
    with col2:
        filters['date_to'] = st.date_input(
            "Până la",
            value=filters['date_to'],
            key="date_to"
        )

    filters['ticket_status'] = st.sidebar.radio(
        "Status ticket",
        ['toate', 'deschise', 'închise'],
        index=['toate', 'deschise', 'închise'].index(filters['ticket_status']),
        horizontal=True,
        key="ticket_status"
    )

    st.sidebar.markdown("---")

    # Platform
    st.sidebar.markdown("### 🏢 PLATFORMĂ")
    if 'platform' in df.columns:
        platforms = sorted(df['platform'].dropna().unique())
        for platform in platforms:
            count = get_count(df, 'platform', platform)
            checked = platform in filters['platforms']
            if st.sidebar.checkbox(f"{platform.title()} ({count})", value=checked, key=f"platform_{platform}"):
                if platform not in filters['platforms']:
                    filters['platforms'].append(platform)
            else:
                if platform in filters['platforms']:
                    filters['platforms'].remove(platform)

    st.sidebar.markdown("---")

    # Area
    st.sidebar.markdown("### 📂 ARIE FUNCȚIONALĂ")
    filters['area_search'] = st.sidebar.text_input(
        "Caută arie",
        value=filters['area_search'],
        key="area_search"
    )

    if 'area' in df.columns:
        areas = sorted(df['area'].dropna().unique())
        # Filter areas by search
        if filters['area_search']:
            areas = [a for a in areas if filters['area_search'].lower() in str(a).lower()]

        for area in areas[:10]:  # Limit to first 10
            count = get_count(df, 'area', area)
            checked = area in filters['areas']
            if st.sidebar.checkbox(f"{area} ({count})", value=checked, key=f"area_{area}"):
                if area not in filters['areas']:
                    filters['areas'].append(area)
            else:
                if area in filters['areas']:
                    filters['areas'].remove(area)

    st.sidebar.markdown("---")

    # Tip Ticket
    st.sidebar.markdown("### 🏷️ TIP TICKET")
    if 'tip' in df.columns:
        tips = sorted(df['tip'].dropna().unique())
        for tip in tips:
            count = get_count(df, 'tip', tip)
            checked = tip in filters['tip']
            if st.sidebar.checkbox(f"{tip.title()} ({count})", value=checked, key=f"tip_{tip}"):
                if tip not in filters['tip']:
                    filters['tip'].append(tip)
            else:
                if tip in filters['tip']:
                    filters['tip'].remove(tip)

    st.sidebar.markdown("---")

    # Severitate
    st.sidebar.markdown("### 🚨 SEVERITATE")
    if 'urgency' in df.columns:
        urgencies = ['blocker', 'mediu', 'scazut']
        for urgency in urgencies:
            count = get_count(df, 'urgency', urgency)
            checked = urgency in filters['urgency']
            icon = '🔴' if urgency == 'blocker' else '🟠' if urgency == 'mediu' else '🟡'
            if st.sidebar.checkbox(f"{icon} {urgency.title()} ({count})", value=checked, key=f"urgency_{urgency}"):
                if urgency not in filters['urgency']:
                    filters['urgency'].append(urgency)
            else:
                if urgency in filters['urgency']:
                    filters['urgency'].remove(urgency)

    st.sidebar.markdown("---")

    # Sentiment
    st.sidebar.markdown("### 😀 SENTIMENT CLIENT")
    if 'sentiment' in df.columns:
        sentiments = ['pozitiv', 'neutru', 'negativ']
        for sentiment in sentiments:
            count = get_count(df, 'sentiment', sentiment)
            checked = sentiment in filters['sentiment']
            icon = '😊' if sentiment == 'pozitiv' else '😐' if sentiment == 'neutru' else '😠'
            if st.sidebar.checkbox(f"{icon} {sentiment.title()} ({count})", value=checked, key=f"sentiment_{sentiment}"):
                if sentiment not in filters['sentiment']:
                    filters['sentiment'].append(sentiment)
            else:
                if sentiment in filters['sentiment']:
                    filters['sentiment'].remove(sentiment)

    st.sidebar.markdown("---")

    # Problem Type
    st.sidebar.markdown("### 🐛 TIP PROBLEMĂ")
    if 'problem_type' in df.columns:
        problem_types = sorted(df['problem_type'].dropna().unique())
        for ptype in problem_types:
            count = get_count(df, 'problem_type', ptype)
            checked = ptype in filters['problem_type']
            if st.sidebar.checkbox(f"{ptype.title()} ({count})", value=checked, key=f"ptype_{ptype}"):
                if ptype not in filters['problem_type']:
                    filters['problem_type'].append(ptype)
            else:
                if ptype in filters['problem_type']:
                    filters['problem_type'].remove(ptype)

    st.sidebar.markdown("---")

    # Status Special
    st.sidebar.markdown("### 🔄 STATUS SPECIAL")

    recurrent_count = len(df[df['is_recurrent'] == True]) if 'is_recurrent' in df.columns else 0
    affects_count = len(df[df['affects_business_flow'] == True]) if 'affects_business_flow' in df.columns else 0
    agent_count = len(df[df['agent_intervention_needed'] == True]) if 'agent_intervention_needed' in df.columns else 0

    recurrent_check = st.sidebar.checkbox(f"🔄 Recurrent ({recurrent_count})", value=filters['is_recurrent'] == True, key="is_recurrent")
    filters['is_recurrent'] = True if recurrent_check else None

    affects_check = st.sidebar.checkbox(f"💼 Afectează Business ({affects_count})", value=filters['affects_business'] == True, key="affects_business")
    filters['affects_business'] = True if affects_check else None

    agent_check = st.sidebar.checkbox(f"🔧 Intervenție Agent ({agent_count})", value=filters['agent_intervention'] == True, key="agent_intervention")
    filters['agent_intervention'] = True if agent_check else None

    st.sidebar.markdown("---")

    # Reset button
    if st.sidebar.button("🔄 Resetează Toate Filtrele", use_container_width=True):
        reset_filters()


def render_top_problems(df):
    """Render top problems bar chart"""
    if 'pain_point' not in df.columns or df.empty:
        st.info("Nu există date pentru a afișa problemele")
        return

    # Get top 10 pain points
    top_problems = df['pain_point'].value_counts().head(10)

    if top_problems.empty:
        st.info("Nu există probleme de afișat")
        return

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=top_problems.values,
        y=top_problems.index,
        orientation='h',
        marker_color='#10B981',
        text=top_problems.values,
        textposition='auto',
    ))

    fig.update_layout(
        title='🔥 Top 10 Probleme',
        xaxis_title='Număr Tickete',
        yaxis_title='',
        height=400,
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)


def render_ticket_card(row, index):
    """Render a single ticket card"""
    urgency_icon = '🔴' if row.get('urgency') == 'blocker' else '🟠' if row.get('urgency') == 'mediu' else '🟡'
    sentiment_icon = '😊' if row.get('sentiment') == 'pozitiv' else '😐' if row.get('sentiment') == 'neutru' else '😠'

    # Create expandable card
    with st.expander(
        f"#{index} | {row.get('created_at', 'N/A').strftime('%d %b %Y %H:%M') if pd.notna(row.get('created_at')) else 'N/A'} | {urgency_icon} {row.get('urgency', 'N/A').title()}",
        expanded=False
    ):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"**{urgency_icon} {row.get('urgency', 'N/A').title()}** | {row.get('platform', 'N/A').title()} > {row.get('area', 'N/A')}")
            st.markdown(f"{sentiment_icon} Sentiment: **{row.get('sentiment', 'N/A').title()}**")
            st.markdown("")
            st.markdown(f"👤 {row.get('customer_email_extracted', 'N/A')}")
            st.markdown(f"📧 {row.get('mailbox_name', 'N/A')}")

        with col2:
            if pd.notna(row.get('is_recurrent')) and row.get('is_recurrent'):
                st.markdown("🔄 **Recurrent**")
            if pd.notna(row.get('affects_business_flow')) and row.get('affects_business_flow'):
                st.markdown("💼 **Afectează Business**")
            if pd.notna(row.get('agent_intervention_needed')) and row.get('agent_intervention_needed'):
                st.markdown("🔧 **Intervenție Agent**")

        st.markdown("---")
        st.markdown("**💬 Problemă:**")
        st.markdown(f"> {row.get('pain_point', 'N/A')}")

        if pd.notna(row.get('user_goal')):
            st.markdown(f"**🎯 Obiectiv:** {row.get('user_goal')}")

        if pd.notna(row.get('summary')):
            st.markdown(f"**📝 Sumar:** {row.get('summary')}")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"⏱️ **Creat:** {row.get('created_at', 'N/A').strftime('%d %b %Y %H:%M') if pd.notna(row.get('created_at')) else 'N/A'}")
        with col2:
            if pd.notna(row.get('closed_at')):
                st.markdown(f"✅ **Închis:** {row.get('closed_at').strftime('%d %b %Y %H:%M')}")
                if pd.notna(row.get('resolution_time_hours')):
                    st.markdown(f"⌛ **Timp rezolvare:** {row.get('resolution_time_hours'):.1f}h")
            else:
                st.markdown("⏳ **În lucru**")


def main():
    """Main function"""

    # Check if data is loaded
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate. Te rog să încarci un fișier CSV din pagina principală.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original

    # Initialize filters
    initialize_filters()

    # Render sidebar filters
    render_sidebar_filters(df)

    # Apply filters
    filtered_df = apply_filters(df, st.session_state.filters)

    # Main content
    st.title("🔍 SmartBill Support Explorer")

    # Top bar with counter
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 📊 Afișez: **{len(filtered_df):,}** din **{len(df):,}** tickete")
    with col2:
        percentage = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0
        st.metric("Filtrat", f"{percentage:.1f}%")

    st.markdown("---")

    # Top Problems
    st.markdown("## 🔥 Top Probleme")
    render_top_problems(filtered_df)

    st.markdown("---")

    # Ticket list
    st.markdown("## 💬 Tickete")

    if filtered_df.empty:
        st.info("🔍 Niciun ticket găsit. Ajustează filtrele pentru a vedea rezultate.")
    else:
        # Sort by created_at descending
        filtered_df_sorted = filtered_df.sort_values('created_at', ascending=False) if 'created_at' in filtered_df.columns else filtered_df

        # Pagination
        items_per_page = 20
        total_pages = (len(filtered_df_sorted) + items_per_page - 1) // items_per_page

        if 'current_page' not in st.session_state:
            st.session_state.current_page = 0

        # Page navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(
                f"Pagina (1-{total_pages})",
                min_value=1,
                max_value=max(1, total_pages),
                value=st.session_state.current_page + 1,
                key="page_selector"
            ) - 1
            st.session_state.current_page = page

        # Get page data
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_df_sorted))
        page_df = filtered_df_sorted.iloc[start_idx:end_idx]

        # Render tickets
        for idx, row in page_df.iterrows():
            render_ticket_card(row, idx)


if __name__ == "__main__":
    main()
