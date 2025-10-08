"""
Filters Module
Advanced filtering logic for the dashboard
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class DataFilter:
    """
    Advanced filtering system for support tickets
    """

    @staticmethod
    def initialize_filters(df: pd.DataFrame) -> None:
        """
        Initialize filter state in session_state
        """
        if 'filters' not in st.session_state:
            st.session_state.filters = {}

        # Date range
        if 'date_range' not in st.session_state.filters:
            if 'created_at' in df.columns and df['created_at'].notna().any():
                min_date = df['created_at'].min().date()
                max_date = df['created_at'].max().date()
                st.session_state.filters['date_range'] = (min_date, max_date)
            else:
                st.session_state.filters['date_range'] = None

        # Platforms
        if 'platforms' not in st.session_state.filters:
            st.session_state.filters['platforms'] = []

        # Areas
        if 'areas' not in st.session_state.filters:
            st.session_state.filters['areas'] = []

        # Urgency
        if 'urgency' not in st.session_state.filters:
            st.session_state.filters['urgency'] = []

        # Sentiment
        if 'sentiment' not in st.session_state.filters:
            st.session_state.filters['sentiment'] = 'Toate'

        # Problem types
        if 'problem_types' not in st.session_state.filters:
            st.session_state.filters['problem_types'] = []

        # Recurrent toggle
        if 'is_recurrent' not in st.session_state.filters:
            st.session_state.filters['is_recurrent'] = False

        # Affects business flow toggle
        if 'affects_business' not in st.session_state.filters:
            st.session_state.filters['affects_business'] = False

        # Search query
        if 'search_query' not in st.session_state.filters:
            st.session_state.filters['search_query'] = ''

    @staticmethod
    def reset_filters(df: pd.DataFrame) -> None:
        """
        Reset all filters to default
        """
        if 'created_at' in df.columns and df['created_at'].notna().any():
            min_date = df['created_at'].min().date()
            max_date = df['created_at'].max().date()
            st.session_state.filters['date_range'] = (min_date, max_date)
        else:
            st.session_state.filters['date_range'] = None

        st.session_state.filters['platforms'] = []
        st.session_state.filters['areas'] = []
        st.session_state.filters['urgency'] = []
        st.session_state.filters['sentiment'] = 'Toate'
        st.session_state.filters['problem_types'] = []
        st.session_state.filters['is_recurrent'] = False
        st.session_state.filters['affects_business'] = False
        st.session_state.filters['search_query'] = ''

    @staticmethod
    def render_sidebar_filters(df: pd.DataFrame) -> None:
        """
        Render all filters in the sidebar
        """
        DataFilter.initialize_filters(df)

        st.sidebar.markdown("### 🔍 Filtrare Avansată")

        # Date range filter
        if 'created_at' in df.columns and df['created_at'].notna().any():
            min_date = df['created_at'].min().date()
            max_date = df['created_at'].max().date()

            st.sidebar.markdown("#### 📅 Perioada")
            date_range = st.sidebar.date_input(
                "Selectează intervalul",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key='date_filter'
            )

            if len(date_range) == 2:
                st.session_state.filters['date_range'] = date_range

        # Quick date filters
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("📆 Săptămâna aceasta", use_container_width=True):
                today = datetime.now().date()
                week_start = today - timedelta(days=today.weekday())
                st.session_state.filters['date_range'] = (week_start, today)
                st.rerun()

        with col2:
            if st.button("📆 Luna aceasta", use_container_width=True):
                today = datetime.now().date()
                month_start = today.replace(day=1)
                st.session_state.filters['date_range'] = (month_start, today)
                st.rerun()

        st.sidebar.markdown("---")

        # Platform filter
        if 'platform' in df.columns:
            st.sidebar.markdown("#### 🏢 Platforme")
            platforms = df['platform'].dropna().unique().tolist()
            platforms.sort()

            selected_platforms = st.sidebar.multiselect(
                "Selectează platforme",
                options=platforms,
                default=st.session_state.filters.get('platforms', []),
                key='platform_filter'
            )
            st.session_state.filters['platforms'] = selected_platforms

        # Area filter
        if 'area' in df.columns:
            st.sidebar.markdown("#### 📍 Areas")
            areas = df['area'].dropna().unique().tolist()
            areas.sort()

            selected_areas = st.sidebar.multiselect(
                "Selectează areas",
                options=areas,
                default=st.session_state.filters.get('areas', []),
                key='area_filter',
                max_selections=10
            )
            st.session_state.filters['areas'] = selected_areas

        st.sidebar.markdown("---")

        # Urgency filter
        if 'urgency' in df.columns:
            st.sidebar.markdown("#### ⚠️ Urgență")
            urgency_levels = df['urgency'].dropna().unique().tolist()

            # Create checkboxes for each urgency level
            selected_urgency = []
            for level in ['Blocker', 'Mediu', 'Scazut']:
                if level in urgency_levels:
                    if st.sidebar.checkbox(
                        level,
                        value=level in st.session_state.filters.get('urgency', []),
                        key=f'urgency_{level}'
                    ):
                        selected_urgency.append(level)

            st.session_state.filters['urgency'] = selected_urgency

        # Sentiment filter
        if 'sentiment' in df.columns:
            st.sidebar.markdown("#### 💭 Sentiment")
            sentiment = st.sidebar.radio(
                "Selectează sentiment",
                options=['Toate', 'Pozitiv', 'Neutru', 'Negativ'],
                index=['Toate', 'Pozitiv', 'Neutru', 'Negativ'].index(
                    st.session_state.filters.get('sentiment', 'Toate')
                ),
                key='sentiment_filter'
            )
            st.session_state.filters['sentiment'] = sentiment

        st.sidebar.markdown("---")

        # Problem type filter
        if 'problem_type' in df.columns:
            st.sidebar.markdown("#### 🔧 Tip Problemă")
            problem_types = df['problem_type'].dropna().unique().tolist()
            problem_types.sort()

            selected_problem_types = st.sidebar.multiselect(
                "Selectează tipuri",
                options=problem_types,
                default=st.session_state.filters.get('problem_types', []),
                key='problem_type_filter'
            )
            st.session_state.filters['problem_types'] = selected_problem_types

        # Toggle filters
        st.sidebar.markdown("#### ⚙️ Opțiuni Speciale")

        is_recurrent = st.sidebar.checkbox(
            "🔁 Doar probleme recurente",
            value=st.session_state.filters.get('is_recurrent', False),
            key='recurrent_filter'
        )
        st.session_state.filters['is_recurrent'] = is_recurrent

        affects_business = st.sidebar.checkbox(
            "💼 Afectează business flow",
            value=st.session_state.filters.get('affects_business', False),
            key='business_filter'
        )
        st.session_state.filters['affects_business'] = affects_business

        st.sidebar.markdown("---")

        # Search filter
        st.sidebar.markdown("#### 🔎 Căutare Text")
        search_query = st.sidebar.text_input(
            "Caută în pain points",
            value=st.session_state.filters.get('search_query', ''),
            placeholder="ex: factura, API, etc.",
            key='search_filter'
        )
        st.session_state.filters['search_query'] = search_query

        st.sidebar.markdown("---")

        # Reset button
        if st.sidebar.button("🔄 Reset Toate Filtrele", use_container_width=True, type="primary"):
            DataFilter.reset_filters(df)
            st.rerun()

    @staticmethod
    def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all active filters to the dataframe

        Returns:
            Filtered dataframe
        """
        if 'filters' not in st.session_state:
            return df

        filtered_df = df.copy()
        filters = st.session_state.filters

        # Date range filter
        if filters.get('date_range') and 'created_at' in filtered_df.columns:
            date_range = filters['date_range']
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    (filtered_df['created_at'].dt.date >= start_date) &
                    (filtered_df['created_at'].dt.date <= end_date)
                ]

        # Platform filter
        if filters.get('platforms') and 'platform' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['platform'].isin(filters['platforms'])]

        # Area filter
        if filters.get('areas') and 'area' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['area'].isin(filters['areas'])]

        # Urgency filter
        if filters.get('urgency') and 'urgency' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['urgency'].isin(filters['urgency'])]

        # Sentiment filter
        if filters.get('sentiment') != 'Toate' and 'sentiment' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['sentiment'] == filters['sentiment']]

        # Problem type filter
        if filters.get('problem_types') and 'problem_type' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['problem_type'].isin(filters['problem_types'])]

        # Recurrent filter
        if filters.get('is_recurrent') and 'is_recurrent' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['is_recurrent'] == True]

        # Business flow filter
        if filters.get('affects_business') and 'affects_business_flow' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['affects_business_flow'] == True]

        # Search filter
        if filters.get('search_query') and filters['search_query'].strip():
            query = filters['search_query'].lower()
            search_columns = ['pain_point', 'summary', 'user_goal', 'problem_type', 'area']

            # Create a mask for rows that match the search query
            mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)

            for col in search_columns:
                if col in filtered_df.columns:
                    mask |= filtered_df[col].astype(str).str.lower().str.contains(query, na=False)

            filtered_df = filtered_df[mask]

        return filtered_df

    @staticmethod
    def get_active_filters_summary() -> List[str]:
        """
        Get a summary of active filters

        Returns:
            List of active filter descriptions
        """
        if 'filters' not in st.session_state:
            return []

        filters = st.session_state.filters
        active = []

        if filters.get('date_range'):
            date_range = filters['date_range']
            if len(date_range) == 2:
                active.append(f"📅 {date_range[0]} → {date_range[1]}")

        if filters.get('platforms'):
            active.append(f"🏢 {len(filters['platforms'])} platforme")

        if filters.get('areas'):
            active.append(f"📍 {len(filters['areas'])} areas")

        if filters.get('urgency'):
            active.append(f"⚠️ {', '.join(filters['urgency'])}")

        if filters.get('sentiment') != 'Toate':
            active.append(f"💭 {filters['sentiment']}")

        if filters.get('problem_types'):
            active.append(f"🔧 {len(filters['problem_types'])} tipuri")

        if filters.get('is_recurrent'):
            active.append("🔁 Recurente")

        if filters.get('affects_business'):
            active.append("💼 Business flow")

        if filters.get('search_query'):
            active.append(f"🔎 '{filters['search_query']}'")

        return active
