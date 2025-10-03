"""
Pain Points Analysis Page - Detailed analysis of reported problems
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor
from utils.filters import render_sidebar_filters, show_filter_summary
from utils.charts import create_sankey_diagram, COLORS

# Page config
st.set_page_config(
    page_title="Pain Points - SmartBill Analytics",
    page_icon="🔥",
    layout="wide"
)


def create_word_frequency_chart(text_series: pd.Series, top_n: int = 20):
    """Create bar chart of most frequent words in pain points"""

    # Combine all text
    all_text = ' '.join(text_series.dropna().astype(str))

    # Simple word tokenization (lowercase, split by space)
    words = all_text.lower().split()

    # Remove common Romanian stop words and short words
    stop_words = {'de', 'la', 'in', 'si', 'cu', 'pe', 'din', 'a', 'au', 'ca', 'ce', 'mai',
                  'nu', 'un', 'o', 'pentru', 'se', 'este', 'sunt', 'am', 'fi', 'cum'}

    words = [w for w in words if len(w) > 3 and w not in stop_words]

    # Count frequencies
    word_counts = Counter(words).most_common(top_n)

    if not word_counts:
        return None

    words, counts = zip(*word_counts)

    fig = go.Figure(data=[
        go.Bar(
            x=list(counts),
            y=list(words),
            orientation='h',
            marker_color=COLORS['primary']
        )
    ])

    fig.update_layout(
        title=f'Top {top_n} Cuvinte Frecvente în Pain Points',
        xaxis_title='Frecvență',
        yaxis_title='Cuvânt',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    return fig


def create_tree_view(df: pd.DataFrame, area_col: str = 'area',
                     problem_col: str = 'problem_type',
                     pain_col: str = 'pain_point'):
    """Create expandable tree view of problems"""

    # Group by area and problem type
    grouped = df.groupby([area_col, problem_col]).agg({
        pain_col: 'count'
    }).reset_index()

    grouped.columns = ['Area', 'Problem Type', 'Count']
    grouped = grouped.sort_values(['Area', 'Count'], ascending=[True, False])

    return grouped


def render_top_pain_points(df: pd.DataFrame, pain_col: str = 'pain_point', top_n: int = 10):
    """Display top recurring pain points"""

    if pain_col not in df.columns:
        st.warning(f"Coloana '{pain_col}' nu există în date")
        return

    # Count pain points
    pain_counts = df[pain_col].value_counts().head(top_n)

    if len(pain_counts) == 0:
        st.info("Nu există pain points de afișat")
        return

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=pain_counts.values,
            y=pain_counts.index,
            orientation='h',
            marker=dict(
                color=pain_counts.values,
                colorscale='Reds',
                showscale=True
            ),
            text=pain_counts.values,
            textposition='auto',
        )
    ])

    fig.update_layout(
        title=f'Top {top_n} Cele Mai Frecvente Probleme',
        xaxis_title='Număr de Apariții',
        yaxis_title='',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)


def render_area_problem_matrix(df: pd.DataFrame):
    """Create heatmap showing area vs problem type distribution"""

    if 'area' not in df.columns or 'problem_type' not in df.columns:
        st.warning("Datele necesare pentru matrix nu sunt disponibile")
        return

    # Create pivot table
    matrix = df.groupby(['area', 'problem_type']).size().reset_index(name='count')
    matrix_pivot = matrix.pivot(index='area', columns='problem_type', values='count').fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=matrix_pivot.values,
        x=matrix_pivot.columns,
        y=matrix_pivot.index,
        colorscale='Reds',
        text=matrix_pivot.values,
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='Area: %{y}<br>Problem Type: %{x}<br>Count: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title='Matrix: Arii × Tipuri de Probleme',
        xaxis_title='Tip Problemă',
        yaxis_title='Arie',
        paper_bgcolor='#0E1117',
        plot_bgcolor='#262730',
        font={'color': '#FAFAFA'},
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main pain points analysis function"""

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
    st.title("🔥 Analiza Pain Points")
    st.markdown("### Identificare și analiză probleme frecvente")

    st.markdown("---")

    # Show filter summary
    show_filter_summary(df_original, df_filtered)

    st.markdown("---")

    # Check if we have data
    if len(df_filtered) == 0:
        st.warning("⚠️ Nu există date pentru filtrele selectate.")
        return

    # Overview metrics
    st.subheader("📊 Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if 'pain_point' in df_filtered.columns:
            unique_pain_points = df_filtered['pain_point'].nunique()
            st.metric("🔍 Probleme Unice", f"{unique_pain_points:,}")

    with col2:
        if 'area' in df_filtered.columns:
            areas = df_filtered['area'].nunique()
            st.metric("📍 Arii Afectate", f"{areas:,}")

    with col3:
        if 'problem_type' in df_filtered.columns:
            problem_types = df_filtered['problem_type'].nunique()
            st.metric("🏷️ Tipuri Probleme", f"{problem_types:,}")

    with col4:
        if 'is_recurrent' in df_filtered.columns:
            recurrent = len(df_filtered[df_filtered['is_recurrent'] == True])
            recurrent_pct = (recurrent / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
            st.metric("🔁 Recurente", f"{recurrent:,}", f"{recurrent_pct:.1f}%")

    st.markdown("---")

    # Top Pain Points
    st.subheader("🎯 Top Probleme Frecvente")

    if 'pain_point' in df_filtered.columns:
        top_n = st.slider("Număr de probleme de afișat:", min_value=5, max_value=30, value=10, step=5)
        render_top_pain_points(df_filtered, pain_col='pain_point', top_n=top_n)
    else:
        st.info("Coloana 'pain_point' nu este disponibilă")

    st.markdown("---")

    # Word Frequency Analysis
    st.subheader("📝 Analiza Cuvinte Frecvente")

    if 'pain_point' in df_filtered.columns:
        fig_words = create_word_frequency_chart(df_filtered['pain_point'], top_n=20)
        if fig_words:
            st.plotly_chart(fig_words, use_container_width=True)
        else:
            st.info("Nu există suficiente date pentru analiza cuvintelor")
    else:
        st.info("Coloana 'pain_point' nu este disponibilă")

    st.markdown("---")

    # Area vs Problem Type Matrix
    st.subheader("🔥 Matrix Arii × Tipuri Probleme")
    render_area_problem_matrix(df_filtered)

    st.markdown("---")

    # Tree View
    st.subheader("🌳 Structură Ierarhică Probleme")

    if 'area' in df_filtered.columns and 'problem_type' in df_filtered.columns:
        tree_data = create_tree_view(df_filtered)

        # Group by area
        areas = tree_data['Area'].unique()

        for area in areas:
            area_data = tree_data[tree_data['Area'] == area]
            total_count = area_data['Count'].sum()

            with st.expander(f"▶️ **{area}** ({total_count:,} probleme)", expanded=False):
                # Show problem types for this area
                for _, row in area_data.iterrows():
                    st.markdown(f"- **{row['Problem Type']}**: {row['Count']:,} probleme")

                # Show actual pain points for this area
                area_df = df_filtered[df_filtered['area'] == area]

                if 'pain_point' in area_df.columns:
                    pain_points = area_df['pain_point'].value_counts().head(5)

                    if len(pain_points) > 0:
                        st.markdown("**Top 5 Pain Points:**")
                        for pain, count in pain_points.items():
                            st.markdown(f"  • `{pain}` ({count} apariții)")
    else:
        st.info("Datele necesare pentru tree view nu sunt disponibile")

    st.markdown("---")

    # Sankey Diagram
    st.subheader("📊 Flow Diagram: Platform → Arie → Tip Problemă")

    if all(col in df_filtered.columns for col in ['platform', 'area', 'problem_type']):
        try:
            fig_sankey = create_sankey_diagram(
                df_filtered,
                source_col='platform',
                target_col='area'
            )
            st.plotly_chart(fig_sankey, use_container_width=True)
        except Exception as e:
            st.error(f"Eroare la crearea diagramei Sankey: {str(e)}")
    else:
        st.info("Datele necesare pentru diagrama Sankey nu sunt disponibile")

    st.markdown("---")

    # Detailed Pain Points Table
    st.subheader("📋 Tabel Detaliat Pain Points")

    # Select columns to display
    display_cols = []
    if 'created_at' in df_filtered.columns:
        display_cols.append('created_at')
    if 'platform' in df_filtered.columns:
        display_cols.append('platform')
    if 'area' in df_filtered.columns:
        display_cols.append('area')
    if 'problem_type' in df_filtered.columns:
        display_cols.append('problem_type')
    if 'urgency' in df_filtered.columns:
        display_cols.append('urgency')
    if 'pain_point' in df_filtered.columns:
        display_cols.append('pain_point')
    if 'is_recurrent' in df_filtered.columns:
        display_cols.append('is_recurrent')

    if display_cols:
        # Sort by priority
        if 'priority_score' in df_filtered.columns:
            df_display = df_filtered.sort_values('priority_score', ascending=False)
        else:
            df_display = df_filtered

        # Add search filter
        search_term = st.text_input("🔍 Caută în tabel:", placeholder="Introdu text pentru căutare...")

        if search_term:
            mask = False
            for col in display_cols:
                if df_display[col].dtype == 'object':
                    mask |= df_display[col].astype(str).str.contains(search_term, case=False, na=False)
            df_display = df_display[mask]

        st.dataframe(
            df_display[display_cols],
            use_container_width=True,
            height=400
        )

        # Export filtered pain points
        if st.button("📥 Export Pain Points ca CSV"):
            csv = df_display[display_cols].to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"pain_points_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nu există coloane de afișat")


if __name__ == "__main__":
    main()
