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
import json

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
PREFERENCES_FILE = '.streamlit/column_preferences.json'


# ========================================
# Filter Management Functions
# ========================================

def initialize_filters(df):
    """Initialize filter session state"""
    if 'investigation_filters' not in st.session_state:
        st.session_state.investigation_filters = {
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


def load_column_preferences():
    """Load column preferences from file"""
    try:
        with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
            return prefs.get('visible_columns', DEFAULT_COLUMNS)
    except:
        return DEFAULT_COLUMNS


def save_column_preferences(visible_columns):
    """Save column preferences to file"""
    try:
        with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump({'visible_columns': visible_columns}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Nu s-au putut salva preferințele: {e}")


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

        # Area
        if 'area' in df_original.columns:
            areas = sorted(df_original['area'].dropna().unique().tolist())
            selected_areas = st.multiselect(
                "📍 Area",
                options=areas,
                key="inv_area"
            )
            st.session_state.investigation_filters['areas'] = selected_areas

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
                'areas': [],
                'tip': [],
                'urgency': [],
                'problem_type': [],
                'platform': [],
                'affects_business': None
            }
            st.rerun()

    # Apply filters
    df = apply_filters(df_original, st.session_state.investigation_filters)

    # Tabbed interface
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Data Explorer",
        "🌟 Visualizer",
        "🔥 Pain Point Analysis",
        "💡 Opportunity Finder",
        "📈 Statistical Analysis"
    ])

    with tab1:
        st.markdown("### 📊 Data Explorer")
        st.markdown("Explore all filtered ticket data")

        # Load saved column preferences
        saved_columns = load_column_preferences()

        # Filter available columns (only show columns that exist in the dataframe)
        available_columns = [col for col in DEFAULT_COLUMNS if col in df.columns]

        # Initialize selected columns (intersection of saved prefs and available columns)
        default_selected = [col for col in saved_columns if col in available_columns]
        if not default_selected:
            default_selected = available_columns

        # Column selector
        selected_columns = st.multiselect(
            "🔍 Selectează coloanele de afișat:",
            options=available_columns,
            default=default_selected,
            key="data_explorer_columns"
        )

        # Save preferences when changed
        if selected_columns != saved_columns:
            save_column_preferences(selected_columns)

        # Show total records
        st.info(f"📊 Afișare {len(df):,} înregistrări | {len(selected_columns)} coloane selectate")

        # Prepare dataframe with selected columns in the correct order
        if selected_columns:
            # Reorder columns according to DEFAULT_COLUMNS order
            ordered_columns = [col for col in DEFAULT_COLUMNS if col in selected_columns]
            df_display = df[ordered_columns]

            # Configure special columns
            column_config = {}

            if 'ticket_url' in ordered_columns:
                column_config['ticket_url'] = st.column_config.LinkColumn(
                    "Ticket URL",
                    display_text="🔗 View"
                )

            if 'is_recurrent' in ordered_columns:
                column_config['is_recurrent'] = st.column_config.CheckboxColumn("Recurrent")

            if 'agent_intervention_needed' in ordered_columns:
                column_config['agent_intervention_needed'] = st.column_config.CheckboxColumn("Agent Needed")

            if 'affects_business_flow' in ordered_columns:
                column_config['affects_business_flow'] = st.column_config.CheckboxColumn("Business Impact")

            # Display dataframe
            st.dataframe(
                df_display,
                use_container_width=True,
                height=700,
                column_config=column_config
            )
        else:
            st.warning("⚠️ Te rugăm să selectezi cel puțin o coloană pentru afișare.")

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

    with tab5:
        st.markdown("### 📈 Statistical Analysis")

        if 'created_at' in df.columns:
            st.markdown("#### Ticket Volume Over Time")

            # Time series with moving average
            daily_counts = df.groupby(df['created_at'].dt.date).size().reset_index(name='count')
            daily_counts.columns = ['date', 'count']
            daily_counts['date'] = pd.to_datetime(daily_counts['date'])

            # Calculate 7-day moving average
            daily_counts['ma_7'] = daily_counts['count'].rolling(window=7, min_periods=1).mean()

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=daily_counts['date'],
                y=daily_counts['count'],
                mode='lines',
                name='Daily Count',
                line=dict(color=COLORS['info'], width=1),
                opacity=0.5
            ))

            fig.add_trace(go.Scatter(
                x=daily_counts['date'],
                y=daily_counts['ma_7'],
                mode='lines',
                name='7-Day Moving Average',
                line=dict(color=COLORS['primary'], width=3)
            ))

            fig.update_layout(
                title='Ticket Volume with 7-Day Moving Average',
                xaxis_title='Date',
                yaxis_title='Ticket Count',
                hovermode='x unified',
                **DARK_TEMPLATE['layout']
            )

            fig.update_xaxes(**AXIS_STYLE)
            fig.update_yaxes(**AXIS_STYLE)

            st.plotly_chart(fig, use_container_width=True)

        # Distribution analysis
        if 'urgency' in df.columns and 'platform' in df.columns:
            st.markdown("#### Distribution: Urgency by Platform")

            pivot_data = pd.crosstab(df['platform'], df['urgency'])

            fig = go.Figure()

            for urgency in pivot_data.columns:
                fig.add_trace(go.Bar(
                    name=urgency,
                    x=pivot_data.index,
                    y=pivot_data[urgency]
                ))

            fig.update_layout(
                barmode='stack',
                xaxis_title='Platform',
                yaxis_title='Count',
                **DARK_TEMPLATE['layout']
            )

            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
