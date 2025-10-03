"""
Filters Module for SmartBill Support Analytics
Provides sidebar filter UI components and state management
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Tuple, List, Optional


def initialize_filter_state():
    """Initialize session state for filters"""
    if 'filter_date_range' not in st.session_state:
        st.session_state.filter_date_range = None

    if 'filter_platforms' not in st.session_state:
        st.session_state.filter_platforms = []

    if 'filter_areas' not in st.session_state:
        st.session_state.filter_areas = []

    if 'filter_urgency' not in st.session_state:
        st.session_state.filter_urgency = []

    if 'filter_sentiment' not in st.session_state:
        st.session_state.filter_sentiment = 'toate'

    if 'filter_recurrent' not in st.session_state:
        st.session_state.filter_recurrent = False

    if 'filter_business' not in st.session_state:
        st.session_state.filter_business = False

    if 'filter_search' not in st.session_state:
        st.session_state.filter_search = ''


def reset_filters():
    """Reset all filters to default values"""
    st.session_state.filter_date_range = None
    st.session_state.filter_platforms = []
    st.session_state.filter_areas = []
    st.session_state.filter_urgency = []
    st.session_state.filter_sentiment = 'toate'
    st.session_state.filter_recurrent = False
    st.session_state.filter_business = False
    st.session_state.filter_search = ''


def render_sidebar_filters(df: pd.DataFrame) -> dict:
    """
    Render all filter controls in the sidebar

    Args:
        df: DataFrame to extract filter options from

    Returns:
        Dictionary containing all filter values
    """

    initialize_filter_state()

    st.sidebar.header("🔍 Filtrare")

    # Date Range Filter
    st.sidebar.subheader("📅 Perioada")

    if 'created_at' in df.columns:
        min_date = df['created_at'].min().date()
        max_date = df['created_at'].max().date()

        # Quick date range buttons
        col1, col2, col3 = st.sidebar.columns(3)

        with col1:
            if st.button("7 zile", use_container_width=True):
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=7)
                st.session_state.filter_date_range = (start_date, end_date)

        with col2:
            if st.button("30 zile", use_container_width=True):
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)
                st.session_state.filter_date_range = (start_date, end_date)

        with col3:
            if st.button("90 zile", use_container_width=True):
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=90)
                st.session_state.filter_date_range = (start_date, end_date)

        # Custom date range picker
        date_range = st.sidebar.date_input(
            "Interval personalizat:",
            value=st.session_state.filter_date_range if st.session_state.filter_date_range else (min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key='date_range_picker'
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            st.session_state.filter_date_range = date_range
        else:
            st.session_state.filter_date_range = None

    st.sidebar.divider()

    # Platform Filter
    if 'platform' in df.columns:
        st.sidebar.subheader("🏢 Platforme")
        all_platforms = sorted(df['platform'].dropna().unique().tolist())

        platforms = st.sidebar.multiselect(
            "Selectează platforme:",
            options=all_platforms,
            default=st.session_state.filter_platforms,
            key='platforms_multiselect'
        )
        st.session_state.filter_platforms = platforms

    st.sidebar.divider()

    # Area Filter
    if 'area' in df.columns:
        st.sidebar.subheader("📍 Arii")
        all_areas = sorted(df['area'].dropna().unique().tolist())

        areas = st.sidebar.multiselect(
            "Selectează arii:",
            options=all_areas,
            default=st.session_state.filter_areas,
            key='areas_multiselect'
        )
        st.session_state.filter_areas = areas

    st.sidebar.divider()

    # Urgency Filter
    if 'urgency' in df.columns:
        st.sidebar.subheader("⚠️ Urgență")

        urgency_options = ['blocker', 'mediu', 'scazut']
        urgency_selected = []

        for urgency in urgency_options:
            if st.sidebar.checkbox(
                urgency,
                value=urgency in st.session_state.filter_urgency,
                key=f'urgency_{urgency}'
            ):
                urgency_selected.append(urgency)

        st.session_state.filter_urgency = urgency_selected

    st.sidebar.divider()

    # Sentiment Filter
    if 'sentiment' in df.columns:
        st.sidebar.subheader("💭 Sentiment")

        sentiment = st.sidebar.radio(
            "Selectează sentiment:",
            options=['toate', 'pozitiv', 'neutru', 'negativ'],
            index=['toate', 'pozitiv', 'neutru', 'negativ'].index(st.session_state.filter_sentiment),
            key='sentiment_radio'
        )
        st.session_state.filter_sentiment = sentiment

    st.sidebar.divider()

    # Boolean Filters
    st.sidebar.subheader("🎯 Filtre Speciale")

    if 'is_recurrent' in df.columns:
        recurrent = st.sidebar.checkbox(
            "🔁 Doar probleme recurente",
            value=st.session_state.filter_recurrent,
            key='recurrent_checkbox'
        )
        st.session_state.filter_recurrent = recurrent

    if 'affects_business_flow' in df.columns:
        business = st.sidebar.checkbox(
            "💼 Afectează business flow",
            value=st.session_state.filter_business,
            key='business_checkbox'
        )
        st.session_state.filter_business = business

    st.sidebar.divider()

    # Search Filter
    st.sidebar.subheader("🔎 Căutare Text")
    search = st.sidebar.text_input(
        "Caută în pain points și summary:",
        value=st.session_state.filter_search,
        placeholder="ex: factura, API, eroare...",
        key='search_input'
    )
    st.session_state.filter_search = search

    st.sidebar.divider()

    # Reset button
    if st.sidebar.button("🔄 Reset Toate Filtrele", use_container_width=True):
        reset_filters()
        st.rerun()

    # Return filter values as dictionary
    filters = {
        'date_range': st.session_state.filter_date_range,
        'platforms': st.session_state.filter_platforms,
        'areas': st.session_state.filter_areas,
        'urgency_levels': st.session_state.filter_urgency,
        'sentiment': st.session_state.filter_sentiment,
        'only_recurrent': st.session_state.filter_recurrent,
        'affects_business': st.session_state.filter_business,
        'search_text': st.session_state.filter_search
    }

    return filters


def show_filter_summary(df_original: pd.DataFrame, df_filtered: pd.DataFrame):
    """
    Show a summary of active filters and result count

    Args:
        df_original: Original DataFrame before filtering
        df_filtered: DataFrame after filtering
    """

    original_count = len(df_original)
    filtered_count = len(df_filtered)
    percentage = (filtered_count / original_count * 100) if original_count > 0 else 0

    # Create columns for summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="📊 Total Tickets",
            value=f"{original_count:,}",
        )

    with col2:
        st.metric(
            label="✅ După Filtrare",
            value=f"{filtered_count:,}",
            delta=f"{filtered_count - original_count:,}" if filtered_count != original_count else None
        )

    with col3:
        st.metric(
            label="📈 Procent",
            value=f"{percentage:.1f}%"
        )

    # Show active filters
    active_filters = get_active_filters()

    if active_filters:
        st.info(f"🔍 **Filtre active:** {', '.join(active_filters)}")


def get_active_filters() -> List[str]:
    """Get list of currently active filter names"""

    active = []

    if st.session_state.get('filter_date_range'):
        active.append("Perioadă personalizată")

    if st.session_state.get('filter_platforms'):
        active.append(f"Platforme ({len(st.session_state.filter_platforms)})")

    if st.session_state.get('filter_areas'):
        active.append(f"Arii ({len(st.session_state.filter_areas)})")

    if st.session_state.get('filter_urgency'):
        active.append(f"Urgență ({len(st.session_state.filter_urgency)})")

    if st.session_state.get('filter_sentiment') != 'Toate':
        active.append(f"Sentiment: {st.session_state.filter_sentiment}")

    if st.session_state.get('filter_recurrent'):
        active.append("Doar recurente")

    if st.session_state.get('filter_business'):
        active.append("Afectează business")

    if st.session_state.get('filter_search'):
        active.append(f"Căutare: '{st.session_state.filter_search}'")

    return active


def create_quick_filters_ui(df: pd.DataFrame):
    """
    Create quick filter buttons for common scenarios

    Args:
        df: DataFrame to filter
    """

    st.subheader("⚡ Filtre Rapide")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚨 Doar Blockers", use_container_width=True):
            reset_filters()
            st.session_state.filter_urgency = ['blocker']
            st.rerun()

    with col2:
        if st.button("🔁 Probleme Recurente", use_container_width=True):
            reset_filters()
            st.session_state.filter_recurrent = True
            st.rerun()

    with col3:
        if st.button("😞 Sentiment Negativ", use_container_width=True):
            reset_filters()
            st.session_state.filter_sentiment = 'negativ'
            st.rerun()

    with col4:
        if st.button("💼 Impact Business", use_container_width=True):
            reset_filters()
            st.session_state.filter_business = True
            st.rerun()
