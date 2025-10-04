"""
Product Opportunity Finder Dashboard
Identify product friction areas and improvement opportunities
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.charts import COLORS, DARK_TEMPLATE, AXIS_STYLE

st.set_page_config(page_title="Product Opportunity", page_icon="💡", layout="wide")


def create_top_problem_areas_chart(df, top_n=10):
    """Create horizontal bar chart of top problem areas"""
    area_counts = df['area'].value_counts().head(top_n).reset_index()
    area_counts.columns = ['area', 'count']

    # Sort ascending for horizontal bar (so highest is on top)
    area_counts = area_counts.sort_values('count', ascending=True)

    fig = go.Figure(data=[go.Bar(
        y=area_counts['area'],
        x=area_counts['count'],
        orientation='h',
        marker=dict(
            color=area_counts['count'],
            colorscale='Reds',
            showscale=False
        ),
        text=area_counts['count'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Tickets: %{x}<extra></extra>'
    )])

    fig.update_layout(
        title=f'Top {top_n} Problem Areas (by Ticket Count)',
        xaxis_title='Number of Tickets',
        yaxis_title='Product Area',
        height=max(400, top_n * 40),
        **DARK_TEMPLATE['layout']
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_root_cause_chart(df):
    """Create bar chart of problem types (root causes)"""
    problem_counts = df['problem_type'].value_counts().reset_index()
    problem_counts.columns = ['problem_type', 'count']

    # Color mapping for problem types
    color_map = {
        'bug': COLORS['danger'],
        'feature_gap': COLORS['warning'],
        'usability': COLORS['info'],
        'documentation': COLORS['secondary'],
        'performance': COLORS['accent'],
        'integration': COLORS['primary']
    }

    colors = [color_map.get(p.lower(), COLORS['gray']) for p in problem_counts['problem_type']]

    fig = go.Figure(data=[go.Bar(
        x=problem_counts['problem_type'],
        y=problem_counts['count'],
        marker=dict(color=colors),
        text=problem_counts['count'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title='Root Cause Analysis (Problem Type Distribution)',
        xaxis_title='Problem Type',
        yaxis_title='Number of Tickets',
        **DARK_TEMPLATE['layout']
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def parse_mentioned_features(df):
    """Parse mentioned_features column (semicolon-delimited) and count occurrences"""
    all_features = []

    for features_str in df['mentioned_features'].dropna():
        if isinstance(features_str, str) and features_str.strip():
            # Split by semicolon and clean
            features = [f.strip() for f in features_str.split(';') if f.strip()]
            all_features.extend(features)

    # Count occurrences
    feature_counts = Counter(all_features)

    # Convert to DataFrame
    df_features = pd.DataFrame(feature_counts.most_common(), columns=['feature', 'count'])

    return df_features


def create_mentioned_features_chart(df_features, top_n=20):
    """Create bar chart of most mentioned features"""
    df_top = df_features.head(top_n)

    fig = go.Figure(data=[go.Bar(
        x=df_top['feature'],
        y=df_top['count'],
        marker=dict(
            color=df_top['count'],
            colorscale='Blues',
            showscale=False
        ),
        text=df_top['count'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Mentions: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title=f'Top {top_n} Most Mentioned Features',
        xaxis_title='Feature',
        yaxis_title='Number of Mentions',
        height=500,
        xaxis={'tickangle': -45},
        **DARK_TEMPLATE['layout']
    )

    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    return fig


def create_pain_points_table(df):
    """Create pain points frequency table"""
    # Count pain points
    pain_point_counts = df.groupby('pain_point').agg({
        'pain_point': 'size',
        'area': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A'
    }).rename(columns={'pain_point': 'frequency', 'area': 'most_common_area'})

    pain_point_counts = pain_point_counts.reset_index()
    pain_point_counts.columns = ['pain_point', 'frequency', 'related_area']

    # Sort by frequency
    pain_point_counts = pain_point_counts.sort_values('frequency', ascending=False)

    return pain_point_counts


def main():
    # Check if data is loaded
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original.copy()

    # Page header
    st.title("💡 Product Opportunity Finder")
    st.markdown("Identify areas of the product causing friction and discover improvement opportunities")

    st.markdown("---")

    # Component 1: Top Problem Areas
    st.markdown("### 🎯 Top Problem Areas")
    st.markdown("Product areas generating the most support tickets")

    col1, col2 = st.columns([3, 1])

    with col2:
        top_n_areas = st.slider("Show top N areas", min_value=5, max_value=20, value=10, key="top_n_areas")

    with col1:
        if 'area' in df.columns:
            fig_areas = create_top_problem_areas_chart(df, top_n=top_n_areas)
            st.plotly_chart(fig_areas, use_container_width=True)
        else:
            st.warning("Column 'area' not found")

    st.markdown("---")

    # Component 2: Root Cause Analysis
    st.markdown("### 🔍 Root Cause Analysis")
    st.markdown("Understand whether issues are bugs, usability problems, or feature gaps")

    if 'problem_type' in df.columns:
        col1, col2 = st.columns([3, 1])

        with col1:
            fig_root_cause = create_root_cause_chart(df)
            st.plotly_chart(fig_root_cause, use_container_width=True)

        with col2:
            st.markdown("#### Breakdown")
            problem_counts = df['problem_type'].value_counts()
            for problem_type, count in problem_counts.items():
                pct = (count / len(df)) * 100
                st.metric(problem_type.title(), f"{count} ({pct:.1f}%)")
    else:
        st.warning("Column 'problem_type' not found")

    st.markdown("---")

    # Component 3: Most Mentioned Features
    st.markdown("### ⭐ Most Mentioned Features")
    st.markdown("Features that appear most frequently in support tickets")

    if 'mentioned_features' in df.columns:
        df_features = parse_mentioned_features(df)

        if not df_features.empty:
            col1, col2 = st.columns([3, 1])

            with col2:
                top_n_features = st.slider("Show top N features", min_value=10, max_value=50, value=20, key="top_n_features")
                display_mode = st.radio("Display as", ["Chart", "Table"], key="feature_display")

            with col1:
                if display_mode == "Chart":
                    fig_features = create_mentioned_features_chart(df_features, top_n=top_n_features)
                    st.plotly_chart(fig_features, use_container_width=True)
                else:
                    st.dataframe(
                        df_features.head(top_n_features),
                        use_container_width=True,
                        height=500
                    )

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Unique Features Mentioned", len(df_features))
            with col2:
                st.metric("Total Feature Mentions", df_features['count'].sum())
            with col3:
                if len(df_features) > 0:
                    st.metric("Most Mentioned", f"{df_features.iloc[0]['feature']} ({df_features.iloc[0]['count']})")
        else:
            st.info("No features mentioned in the tickets")
    else:
        st.warning("Column 'mentioned_features' not found")

    st.markdown("---")

    # Component 4: Top User Pain Points
    st.markdown("### 💬 Top User Pain Points")
    st.markdown("Direct qualitative feedback from users, sorted by frequency")

    if 'pain_point' in df.columns and 'area' in df.columns:
        pain_points_df = create_pain_points_table(df)

        # Search filter
        search_term = st.text_input("🔍 Search pain points", key="pain_point_search")

        if search_term:
            pain_points_df = pain_points_df[
                pain_points_df['pain_point'].str.contains(search_term, case=False, na=False)
            ]

        # Display table
        st.dataframe(
            pain_points_df,
            use_container_width=True,
            height=500,
            column_config={
                "pain_point": st.column_config.TextColumn("Pain Point", width="large"),
                "frequency": st.column_config.NumberColumn("Frequency", format="%d"),
                "related_area": st.column_config.TextColumn("Most Common Area", width="medium")
            }
        )

        # Export button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("📥 Export to CSV"):
                csv = pain_points_df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "pain_points.csv",
                    "text/csv"
                )

        # Summary
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Unique Pain Points", len(pain_points_df))
        with col2:
            st.metric("Total Occurrences", pain_points_df['frequency'].sum())
        with col3:
            if len(pain_points_df) > 0:
                st.metric("Most Frequent", f"{pain_points_df.iloc[0]['frequency']} occurrences")

    else:
        st.warning("Columns 'pain_point' or 'area' not found")


if __name__ == "__main__":
    main()
