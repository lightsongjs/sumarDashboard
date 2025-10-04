"""
Deep Dive Explorer - Ticket Data Explorer
Interactive granular analysis with multi-dimensional filtering
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.charts import COLORS

st.set_page_config(page_title="Deep Dive Explorer", page_icon="🔬", layout="wide")


def initialize_filters(df):
    """Initialize filter session state"""
    if 'deep_dive_filters' not in st.session_state:
        st.session_state.deep_dive_filters = {
            'date_range': None,
            'areas': [],
            'tip': [],
            'urgency': [],
            'problem_type': [],
            'platform': [],
            'affects_business': None
        }


def clear_all_filters():
    """Clear all filters"""
    st.session_state.deep_dive_filters = {
        'date_range': None,
        'areas': [],
        'tip': [],
        'urgency': [],
        'problem_type': [],
        'platform': [],
        'affects_business': None
    }


def apply_filters(df, filters):
    """Apply all active filters to the dataframe"""
    filtered_df = df.copy()

    # Date range filter
    if filters['date_range'] and len(filters['date_range']) == 2:
        filtered_df = filtered_df[
            (filtered_df['created_at'].dt.date >= filters['date_range'][0]) &
            (filtered_df['created_at'].dt.date <= filters['date_range'][1])
        ]

    # Multi-select filters
    if filters['areas'] and 'area' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['area'].isin(filters['areas'])]

    if filters['tip'] and 'tip' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['tip'].isin(filters['tip'])]

    if filters['urgency'] and 'urgency' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['urgency'].isin(filters['urgency'])]

    if filters['problem_type'] and 'problem_type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['problem_type'].isin(filters['problem_type'])]

    if filters['platform'] and 'platform' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['platform'].isin(filters['platform'])]

    # Boolean filter
    if filters['affects_business'] is not None and 'affects_business_flow' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['affects_business_flow'] == filters['affects_business']]

    return filtered_df


def render_filter_summary(original_count, filtered_count):
    """Show summary of applied filters"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tickets", f"{original_count:,}")

    with col2:
        st.metric("Filtered Tickets", f"{filtered_count:,}")

    with col3:
        if original_count > 0:
            pct = (filtered_count / original_count) * 100
            st.metric("% of Total", f"{pct:.1f}%")


def main():
    # Check if data is loaded
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original.copy()
    original_count = len(df)

    # Initialize filters
    initialize_filters(df)

    # Page header
    st.title("🔬 Deep Dive Explorer")
    st.markdown("Interactive granular analysis of ticket data with multi-dimensional filtering")

    st.markdown("---")

    # FILTERS SECTION
    st.markdown("## 🎛️ Global Filters")
    st.markdown("Apply filters to narrow down the data. All charts and tables update in real-time.")

    # Filter controls in expandable section
    with st.expander("📊 Filter Controls", expanded=True):
        # Row 1: Date and Business Impact
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📅 Date Range**")
            if 'created_at' in df.columns:
                date_range = st.date_input(
                    "Select date range",
                    value=(df['created_at'].min().date(), df['created_at'].max().date()),
                    key="dd_date_range"
                )
                st.session_state.deep_dive_filters['date_range'] = date_range if len(date_range) == 2 else None

        with col2:
            st.markdown("**💼 Business Impact**")
            if 'affects_business_flow' in df.columns:
                business_filter = st.radio(
                    "Affects Business Flow",
                    options=["All", "Yes", "No"],
                    horizontal=True,
                    key="dd_business"
                )
                st.session_state.deep_dive_filters['affects_business'] = (
                    True if business_filter == "Yes" else False if business_filter == "No" else None
                )

        st.markdown("---")

        # Row 2: Platform, Area, Type
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🏢 Platform**")
            if 'platform' in df.columns:
                platforms = sorted(df['platform'].dropna().unique().tolist())
                selected_platforms = st.multiselect(
                    "Select platforms",
                    options=platforms,
                    key="dd_platform"
                )
                st.session_state.deep_dive_filters['platform'] = selected_platforms

        with col2:
            st.markdown("**📍 Area**")
            if 'area' in df.columns:
                areas = sorted(df['area'].dropna().unique().tolist())
                selected_areas = st.multiselect(
                    "Select areas",
                    options=areas,
                    key="dd_area"
                )
                st.session_state.deep_dive_filters['areas'] = selected_areas

        with col3:
            st.markdown("**📋 Ticket Type**")
            if 'tip' in df.columns:
                tips = sorted(df['tip'].dropna().unique().tolist())
                selected_tips = st.multiselect(
                    "Select types",
                    options=tips,
                    key="dd_tip"
                )
                st.session_state.deep_dive_filters['tip'] = selected_tips

        st.markdown("---")

        # Row 3: Urgency and Problem Type
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🚨 Urgency**")
            if 'urgency' in df.columns:
                urgencies = ['blocker', 'mediu', 'scazut']
                available_urgencies = [u for u in urgencies if u in df['urgency'].unique()]
                selected_urgencies = st.multiselect(
                    "Select urgency levels",
                    options=available_urgencies,
                    key="dd_urgency"
                )
                st.session_state.deep_dive_filters['urgency'] = selected_urgencies

        with col2:
            st.markdown("**🔍 Problem Type**")
            if 'problem_type' in df.columns:
                problem_types = sorted(df['problem_type'].dropna().unique().tolist())
                selected_problem_types = st.multiselect(
                    "Select problem types",
                    options=problem_types,
                    key="dd_problem_type"
                )
                st.session_state.deep_dive_filters['problem_type'] = selected_problem_types

        st.markdown("---")

        # Clear filters button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔄 Clear All Filters", use_container_width=True):
                clear_all_filters()
                st.rerun()

    st.markdown("---")

    # Apply filters
    filtered_df = apply_filters(df, st.session_state.deep_dive_filters)

    # Show filter summary
    render_filter_summary(original_count, len(filtered_df))

    st.markdown("---")

    # MASTER DATA TABLE
    st.markdown("## 📋 Filtered Ticket Data")

    if len(filtered_df) > 0:
        # Column selection
        all_columns = filtered_df.columns.tolist()
        default_columns = [
            'created_at', 'summary', 'area', 'platform', 'urgency',
            'sentiment', 'problem_type', 'pain_point', 'user_goal',
            'affects_business_flow', 'is_recurrent', 'ticket_url'
        ]
        available_defaults = [col for col in default_columns if col in all_columns]

        with st.expander("⚙️ Customize Columns", expanded=False):
            selected_columns = st.multiselect(
                "Select columns to display",
                options=all_columns,
                default=available_defaults,
                key="dd_columns"
            )

        if not selected_columns:
            selected_columns = available_defaults

        # Prepare display dataframe
        display_df = filtered_df[selected_columns].copy()

        # Format datetime columns
        for col in display_df.columns:
            if pd.api.types.is_datetime64_any_dtype(display_df[col]):
                display_df[col] = display_df[col].dt.strftime('%Y-%m-%d %H:%M')

        # Pagination settings
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            page_size = st.selectbox(
                "Rows per page",
                options=[10, 25, 50, 100, 250],
                index=2,
                key="dd_page_size"
            )

        with col2:
            total_pages = (len(display_df) - 1) // page_size + 1
            page_number = st.number_input(
                "Page",
                min_value=1,
                max_value=max(1, total_pages),
                value=1,
                key="dd_page_number"
            )

        # Calculate pagination
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(display_df))

        # Display paginated data
        st.dataframe(
            display_df.iloc[start_idx:end_idx],
            use_container_width=True,
            height=600,
            column_config={
                "ticket_url": st.column_config.LinkColumn("Ticket URL"),
                "created_at": st.column_config.TextColumn("Created At"),
                "closed_at": st.column_config.TextColumn("Closed At"),
                "affects_business_flow": st.column_config.CheckboxColumn("Business Impact"),
                "is_recurrent": st.column_config.CheckboxColumn("Recurrent"),
                "agent_intervention_needed": st.column_config.CheckboxColumn("Agent Intervention")
            }
        )

        # Pagination info
        st.caption(f"Showing rows {start_idx + 1} to {end_idx} of {len(display_df)} (Page {page_number} of {total_pages})")

        # Export options
        st.markdown("---")
        st.markdown("### 📥 Export Data")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            # Export current view
            csv = display_df.iloc[start_idx:end_idx].to_csv(index=False)
            st.download_button(
                "📄 Export Current Page (CSV)",
                csv,
                "tickets_current_page.csv",
                "text/csv",
                use_container_width=True
            )

        with col2:
            # Export all filtered data
            csv_all = display_df.to_csv(index=False)
            st.download_button(
                "📊 Export All Filtered Data (CSV)",
                csv_all,
                "tickets_filtered.csv",
                "text/csv",
                use_container_width=True
            )

    else:
        st.info("No tickets match the current filter criteria. Try adjusting your filters.")

    # Quick stats at bottom
    if len(filtered_df) > 0:
        st.markdown("---")
        st.markdown("### 📊 Quick Statistics")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if 'urgency' in filtered_df.columns:
                blockers = len(filtered_df[filtered_df['urgency'].str.lower() == 'blocker'])
                st.metric("🔴 Blockers", blockers)

        with col2:
            if 'sentiment' in filtered_df.columns:
                negative = len(filtered_df[filtered_df['sentiment'].str.lower() == 'negativ'])
                st.metric("😟 Negative", negative)

        with col3:
            if 'affects_business_flow' in filtered_df.columns:
                business_impact = len(filtered_df[filtered_df['affects_business_flow'] == True])
                st.metric("💼 Business Impact", business_impact)

        with col4:
            if 'is_recurrent' in filtered_df.columns:
                recurrent = len(filtered_df[filtered_df['is_recurrent'] == True])
                st.metric("🔄 Recurrent", recurrent)

        with col5:
            if 'closed_at' in filtered_df.columns:
                closed = len(filtered_df[filtered_df['closed_at'].notna()])
                st.metric("✅ Closed", closed)


if __name__ == "__main__":
    main()
