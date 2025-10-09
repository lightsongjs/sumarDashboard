"""
Investigation Hub - Deep Dive Analysis
Consolidates all explorer and analytics pages into one powerful interface
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

st.set_page_config(page_title="Investigation Hub", page_icon="🔬", layout="wide")

# Default column order for Data Explorer
DEFAULT_COLUMNS = [
    'subject', 'platform', 'tip', 'summary', 'ticket_url',
    'conversation', 'area', 'sentiment', 'apreciere_parere_support',
    'urgency', 'is_recurrent', 'agent_intervention_needed',
    'user_goal', 'pain_point', 'problem_type', 'affects_business_flow',
    'integration', 'mentioned_features', 'specific_error_messages',
    'classification_index', 'total_classifications'
]


# ========================================
# Filter Management Functions
# ========================================

def initialize_filters(df):
    """Initialize filter session state"""
    if 'investigation_filters' not in st.session_state:
        st.session_state.investigation_filters = {
            'date_range': None,
            'platform': [],
            'tip': [],
            'areas': [],
            'sentiment': [],
            'urgency': [],
            'problem_type': [],
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
    if filters['platform'] and 'platform' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['platform'].isin(filters['platform'])]

    if filters['tip'] and 'tip' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['tip'].isin(filters['tip'])]

    if filters['areas'] and 'area' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['area'].isin(filters['areas'])]

    if filters['sentiment'] and 'sentiment' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['sentiment'].isin(filters['sentiment'])]

    if filters['urgency'] and 'urgency' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['urgency'].isin(filters['urgency'])]

    if filters['problem_type'] and 'problem_type' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['problem_type'].isin(filters['problem_type'])]

    # Boolean filter
    if filters['affects_business'] is not None and 'affects_business_flow' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['affects_business_flow'] == filters['affects_business']]

    return filtered_df


# ========================================
# Chart Functions
# ========================================

def create_sunburst_chart(df):
    """Create hierarchical sunburst chart"""
    if 'platform' not in df.columns or 'area' not in df.columns:
        return None

    # Prepare hierarchical data
    hierarchy_df = df.groupby(['platform', 'area']).size().reset_index(name='count')

    fig = px.sunburst(
        hierarchy_df,
        path=['platform', 'area'],
        values='count',
        color='count',
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        title='Ticket Distribution: Platform → Area',
        **DARK_TEMPLATE['layout']
    )

    return fig


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

    df_original = st.session_state.df_original.copy()
    initialize_filters(df_original)

    # Page header
    st.title("🔬 Investigation Hub")
    st.markdown("*Advanced data exploration with unified filtering across all analysis views*")

    # Sidebar for global filters
    with st.sidebar:
        st.markdown("## 🎛️ Global Filters")
        st.markdown("Filters apply to all tabs")

        # Date Range
        if 'created_at' in df_original.columns:
            date_range = st.date_input(
                "📅 Date Range",
                value=(df_original['created_at'].min().date(), df_original['created_at'].max().date()),
                key="inv_date_range"
            )
            st.session_state.investigation_filters['date_range'] = date_range if len(date_range) == 2 else None

        # Platform
        if 'platform' in df_original.columns:
            platforms = sorted(df_original['platform'].dropna().unique().tolist())
            selected_platforms = st.multiselect(
                "🏢 Platform",
                options=platforms,
                key="inv_platform"
            )
            st.session_state.investigation_filters['platform'] = selected_platforms

        # Tip
        if 'tip' in df_original.columns:
            tips = sorted(df_original['tip'].dropna().unique().tolist())
            selected_tips = st.multiselect(
                "📝 Tip",
                options=tips,
                key="inv_tip"
            )
            st.session_state.investigation_filters['tip'] = selected_tips

        # Area
        if 'area' in df_original.columns:
            areas = sorted(df_original['area'].dropna().unique().tolist())
            selected_areas = st.multiselect(
                "📍 Area",
                options=areas,
                key="inv_area"
            )
            st.session_state.investigation_filters['areas'] = selected_areas

        # Sentiment
        if 'sentiment' in df_original.columns:
            sentiments = sorted(df_original['sentiment'].dropna().unique().tolist())
            selected_sentiments = st.multiselect(
                "😊 Sentiment",
                options=sentiments,
                key="inv_sentiment"
            )
            st.session_state.investigation_filters['sentiment'] = selected_sentiments

        # Urgency
        if 'urgency' in df_original.columns:
            urgencies = sorted(df_original['urgency'].dropna().unique().tolist())
            selected_urgencies = st.multiselect(
                "🚨 Urgency",
                options=urgencies,
                key="inv_urgency"
            )
            st.session_state.investigation_filters['urgency'] = selected_urgencies

        # Problem Type
        if 'problem_type' in df_original.columns:
            problem_types = sorted(df_original['problem_type'].dropna().unique().tolist())
            selected_problem_types = st.multiselect(
                "🐛 Problem Type",
                options=problem_types,
                key="inv_problem_type"
            )
            st.session_state.investigation_filters['problem_type'] = selected_problem_types

        # Business Impact
        if 'affects_business_flow' in df_original.columns:
            business_filter = st.radio(
                "💼 Business Impact",
                options=["All", "Yes", "No"],
                key="inv_business"
            )
            st.session_state.investigation_filters['affects_business'] = (
                True if business_filter == "Yes" else False if business_filter == "No" else None
            )

        if st.button("🔄 Clear All Filters"):
            st.session_state.investigation_filters = {
                'date_range': None,
                'platform': [],
                'tip': [],
                'areas': [],
                'sentiment': [],
                'urgency': [],
                'problem_type': [],
                'affects_business': None
            }
            st.rerun()

    # Apply filters
    df = apply_filters(df_original, st.session_state.investigation_filters)

    # Tabbed interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Data Explorer",
        "🌟 Visualizer",
        "🔥 Pain Point Analysis",
        "💡 Opportunity Finder"
    ])

    with tab1:
        st.markdown("### 📊 Data Explorer")
        st.markdown("Explore all filtered ticket data - Use the 👁️ icon in table header to show/hide columns")

        # Show total records
        st.info(f"📊 Afișare {len(df):,} înregistrări")

        # Filter and reorder columns according to DEFAULT_COLUMNS
        available_columns = [col for col in DEFAULT_COLUMNS if col in df.columns]
        df_display = df[available_columns]

        # Configure special columns
        column_config = {
            'ticket_url': st.column_config.LinkColumn(
                "Ticket URL",
                display_text="🔗 View"
            ),
            'is_recurrent': st.column_config.CheckboxColumn("Recurrent"),
            'agent_intervention_needed': st.column_config.CheckboxColumn("Agent Needed"),
            'affects_business_flow': st.column_config.CheckboxColumn("Business Impact")
        }

        # Display dataframe
        st.dataframe(
            df_display,
            use_container_width=True,
            height=700,
            column_config=column_config
        )

        # Export
        st.markdown("---")
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export Filtered Data (CSV)",
            csv,
            "filtered_tickets.csv",
            "text/csv",
            use_container_width=True
        )

    with tab2:
        st.markdown("### 🌟 Visual Explorer")
        st.markdown("Interactive hierarchical visualizations")

        fig = create_sunburst_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns not available for Sunburst chart")

    with tab3:
        st.markdown("### 🔥 Pain Point Analysis")

        if 'pain_point' in df.columns:
            pain_counts = df['pain_point'].value_counts().head(10)

            fig = go.Figure(data=[go.Bar(
                y=pain_counts.index,
                x=pain_counts.values,
                orientation='h',
                marker=dict(color=COLORS['danger']),
                text=pain_counts.values,
                textposition='outside'
            )])

            fig.update_layout(
                title='Top 10 Pain Points',
                xaxis_title='Number of Tickets',
                yaxis_title='Pain Point',
                height=500,
                **DARK_TEMPLATE['layout']
            )

            fig.update_xaxes(**AXIS_STYLE)
            fig.update_yaxes(**AXIS_STYLE)

            st.plotly_chart(fig, use_container_width=True)

            # Pain point table
            st.markdown("#### Pain Point Details")
            st.dataframe(
                df[df['pain_point'].notna()][['created_at', 'pain_point', 'area', 'platform', 'urgency']],
                use_container_width=True,
                height=400
            )
        else:
            st.warning("Column 'pain_point' not found")

    with tab4:
        st.markdown("### 💡 Opportunity Finder")
        st.markdown("Identify product gaps and improvement opportunities")

        if 'area' in df.columns:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Top Problem Areas")
                area_counts = df['area'].value_counts().head(8)

                fig = go.Figure(data=[go.Bar(
                    y=area_counts.index,
                    x=area_counts.values,
                    orientation='h',
                    marker=dict(color=COLORS['warning'])
                )])

                fig.update_layout(
                    xaxis_title='Ticket Count',
                    yaxis_title='Area',
                    height=400,
                    **DARK_TEMPLATE['layout']
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                if 'problem_type' in df.columns:
                    st.markdown("#### Problem Types")
                    type_counts = df['problem_type'].value_counts()

                    fig = go.Figure(data=[go.Pie(
                        labels=type_counts.index,
                        values=type_counts.values,
                        hole=0.3
                    )])

                    fig.update_layout(
                        height=400,
                        **DARK_TEMPLATE['layout']
                    )

                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns not available")


if __name__ == "__main__":
    main()
