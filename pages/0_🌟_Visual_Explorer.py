"""
SmartBill Visual Explorer
Vizualizare ierarhică interactivă cu Sunburst/Treemap/Icicle
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.data_processor import CSVProcessor

st.set_page_config(page_title="Visual Explorer", page_icon="🌟", layout="wide")


def initialize_visual_state():
    """Initialize visual explorer state"""
    if 'visual' not in st.session_state:
        st.session_state.visual = {
            'chart_type': 'sunburst',  # sunburst, treemap, icicle
            'selected_path': None,
            'color_by': 'volume'  # volume, severity, sentiment
        }


def prepare_hierarchy_data(df):
    """Prepare hierarchical data for visualization"""
    # Create hierarchy: Platform → Severity → Problem Type
    hierarchy = []

    # Add root
    hierarchy.append({
        'id': 'Total',
        'parent': '',
        'value': len(df),
        'label': f'Total: {len(df)} tickete'
    })

    # Level 1: Platforms
    if 'platform' in df.columns:
        platforms = df['platform'].value_counts()
        for platform, count in platforms.items():
            if pd.notna(platform):
                hierarchy.append({
                    'id': f'{platform}',
                    'parent': 'Total',
                    'value': count,
                    'label': f'{platform.title()}: {count}'
                })

                # Level 2: Severity per platform
                platform_df = df[df['platform'] == platform]
                if 'urgency' in platform_df.columns:
                    urgencies = platform_df['urgency'].value_counts()
                    for urgency, urg_count in urgencies.items():
                        if pd.notna(urgency):
                            hierarchy.append({
                                'id': f'{platform}_{urgency}',
                                'parent': f'{platform}',
                                'value': urg_count,
                                'label': f'{urgency.title()}: {urg_count}'
                            })

                            # Level 3: Problem type per severity
                            urgency_df = platform_df[platform_df['urgency'] == urgency]
                            if 'problem_type' in urgency_df.columns:
                                problem_types = urgency_df['problem_type'].value_counts()
                                for ptype, ptype_count in problem_types.items():
                                    if pd.notna(ptype):
                                        hierarchy.append({
                                            'id': f'{platform}_{urgency}_{ptype}',
                                            'parent': f'{platform}_{urgency}',
                                            'value': ptype_count,
                                            'label': f'{ptype.title()}: {ptype_count}'
                                        })

    return pd.DataFrame(hierarchy)


def get_color_mapping(df, color_by):
    """Get color mapping based on selected criterion"""
    if color_by == 'severity':
        return {
            'blocker': '#EF4444',
            'mediu': '#F59E0B',
            'scazut': '#10B981'
        }
    elif color_by == 'sentiment':
        return {
            'negativ': '#EF4444',
            'neutru': '#6B7280',
            'pozitiv': '#10B981'
        }
    else:  # volume
        return None


def render_sunburst(hierarchy_df):
    """Render Sunburst chart"""
    fig = go.Figure(go.Sunburst(
        ids=hierarchy_df['id'],
        labels=hierarchy_df['label'],
        parents=hierarchy_df['parent'],
        values=hierarchy_df['value'],
        branchvalues="total",
        marker=dict(
            colorscale='Greens',
            cmid=hierarchy_df['value'].mean()
        ),
        hovertemplate='<b>%{label}</b><br>Tickete: %{value}<extra></extra>',
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=600,
        paper_bgcolor='#0E1117',
        font={'color': '#FAFAFA', 'size': 12}
    )

    return fig


def render_treemap(hierarchy_df):
    """Render Treemap chart"""
    fig = go.Figure(go.Treemap(
        ids=hierarchy_df['id'],
        labels=hierarchy_df['label'],
        parents=hierarchy_df['parent'],
        values=hierarchy_df['value'],
        branchvalues="total",
        marker=dict(
            colorscale='Viridis',
            cmid=hierarchy_df['value'].mean()
        ),
        textposition='middle center',
        hovertemplate='<b>%{label}</b><br>Tickete: %{value}<extra></extra>',
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=600,
        paper_bgcolor='#0E1117',
        font={'color': '#FAFAFA', 'size': 12}
    )

    return fig


def render_icicle(hierarchy_df):
    """Render Icicle chart"""
    fig = go.Figure(go.Icicle(
        ids=hierarchy_df['id'],
        labels=hierarchy_df['label'],
        parents=hierarchy_df['parent'],
        values=hierarchy_df['value'],
        branchvalues="total",
        marker=dict(
            colorscale='Blues',
            cmid=hierarchy_df['value'].mean()
        ),
        hovertemplate='<b>%{label}</b><br>Tickete: %{value}<extra></extra>',
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=600,
        paper_bgcolor='#0E1117',
        font={'color': '#FAFAFA', 'size': 12}
    )

    return fig


def render_sidebar_controls():
    """Render sidebar controls"""
    st.sidebar.title("🎨 Controale Vizualizare")

    # Chart type selector
    st.sidebar.markdown("### 📊 Tip Vizualizare")
    chart_type = st.sidebar.radio(
        "Alege vizualizarea",
        ['sunburst', 'treemap', 'icicle'],
        format_func=lambda x: {
            'sunburst': '🌞 Sunburst',
            'treemap': '🗺️ Treemap',
            'icicle': '🧊 Icicle'
        }[x],
        key="chart_type_selector"
    )
    st.session_state.visual['chart_type'] = chart_type

    st.sidebar.markdown("---")

    # Color by selector
    st.sidebar.markdown("### 🎨 Culoare după")
    color_by = st.sidebar.radio(
        "Alege criteriu",
        ['volume', 'severity', 'sentiment'],
        format_func=lambda x: {
            'volume': '📊 Volum',
            'severity': '🚨 Severitate',
            'sentiment': '😀 Sentiment'
        }[x],
        key="color_by_selector"
    )
    st.session_state.visual['color_by'] = color_by

    st.sidebar.markdown("---")

    # Info
    st.sidebar.markdown("### ℹ️ Instrucțiuni")
    st.sidebar.info("""
    **Cum să folosești:**

    1. 🖱️ **Click** pe orice segment pentru a explora
    2. 🔍 **Hover** pentru detalii
    3. 🔄 **Selectează** tip vizualizare
    4. 🎨 **Schimbă** criteriul de culoare

    **Ierarhie:**
    - Nivel 1: Platformă
    - Nivel 2: Severitate
    - Nivel 3: Tip Problemă
    """)

    st.sidebar.markdown("---")

    # Reset button
    if st.sidebar.button("🔄 Resetează Vizualizare", use_container_width=True):
        st.session_state.visual['selected_path'] = None
        st.rerun()


def render_details_panel(df, hierarchy_df):
    """Render details panel based on selection"""
    st.markdown("### 📊 Statistici Generale")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Total Tickete", f"{len(df):,}")

    with col2:
        platforms = df['platform'].nunique() if 'platform' in df.columns else 0
        st.metric("🏢 Platforme", platforms)

    with col3:
        if 'urgency' in df.columns:
            blockers = len(df[df['urgency'] == 'blocker'])
            st.metric("🔴 Blockers", blockers)

    with col4:
        if 'sentiment' in df.columns:
            negative = len(df[df['sentiment'] == 'negativ'])
            st.metric("😠 Negativ", negative)

    st.markdown("---")

    # Distribution charts
    col1, col2 = st.columns(2)

    with col1:
        if 'platform' in df.columns:
            st.markdown("#### 📊 Distribuție Platformă")
            platform_dist = df['platform'].value_counts().head(5)

            fig = go.Figure(go.Bar(
                x=platform_dist.values,
                y=platform_dist.index,
                orientation='h',
                marker_color='#10B981'
            ))

            fig.update_layout(
                height=250,
                paper_bgcolor='#0E1117',
                plot_bgcolor='#262730',
                font={'color': '#FAFAFA'},
                margin=dict(l=0, r=0, t=0, b=0),
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if 'urgency' in df.columns:
            st.markdown("#### 🚨 Distribuție Severitate")
            urgency_dist = df['urgency'].value_counts()

            colors = {'blocker': '#EF4444', 'mediu': '#F59E0B', 'scazut': '#10B981'}
            fig = go.Figure(go.Bar(
                x=urgency_dist.values,
                y=urgency_dist.index,
                orientation='h',
                marker_color=[colors.get(x, '#6B7280') for x in urgency_dist.index]
            ))

            fig.update_layout(
                height=250,
                paper_bgcolor='#0E1117',
                plot_bgcolor='#262730',
                font={'color': '#FAFAFA'},
                margin=dict(l=0, r=0, t=0, b=0),
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig, use_container_width=True)


def main():
    """Main function"""

    # Check if data is loaded
    if not st.session_state.get('data_loaded') or st.session_state.get('df_original') is None:
        st.warning("⚠️ Nu există date încărcate. Te rog să încarci un fișier CSV din pagina principală.")
        if st.button("📊 Mergi la pagina principală"):
            st.switch_page("app.py")
        return

    df = st.session_state.df_original

    # Initialize state
    initialize_visual_state()

    # Render sidebar controls
    render_sidebar_controls()

    # Main content
    st.title("🌟 SmartBill Visual Explorer")
    st.markdown("### Explorare ierarhică interactivă a datelor")

    # Prepare hierarchy data
    hierarchy_df = prepare_hierarchy_data(df)

    # Render chart based on selected type
    chart_type = st.session_state.visual['chart_type']

    if chart_type == 'sunburst':
        st.markdown("#### 🌞 Sunburst Chart - Click pe segmente pentru a explora")
        fig = render_sunburst(hierarchy_df)
    elif chart_type == 'treemap':
        st.markdown("#### 🗺️ Treemap - Click pe zone pentru a explora")
        fig = render_treemap(hierarchy_df)
    else:  # icicle
        st.markdown("#### 🧊 Icicle Chart - Click pe benzi pentru a explora")
        fig = render_icicle(hierarchy_df)

    # Display chart with click events
    selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

    st.markdown("---")

    # Render details panel
    render_details_panel(df, hierarchy_df)


if __name__ == "__main__":
    main()
