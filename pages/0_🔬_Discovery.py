"""
SmartBill Data Discovery
Explorare progresivă a datelor - de la zero la detalii
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils.data_processor import CSVProcessor

st.set_page_config(page_title="Discovery", page_icon="🔬", layout="wide")


def initialize_discovery_state():
    """Initialize discovery navigation state"""
    if 'discovery' not in st.session_state:
        st.session_state.discovery = {
            'level': 0,  # 0=start, 1=platform, 2=criteria, 3=results
            'platform': None,
            'criteria_type': None,  # 'arii', 'severitate', 'sentiment', 'problem_type', 'perioada', 'status'
            'criteria_value': None,
            'filters': []  # List of applied filters
        }


def reset_discovery():
    """Reset discovery to start"""
    st.session_state.discovery = {
        'level': 0,
        'platform': None,
        'criteria_type': None,
        'criteria_value': None,
        'filters': []
    }


def go_back():
    """Go back one level"""
    if st.session_state.discovery['level'] > 0:
        st.session_state.discovery['level'] -= 1
        if st.session_state.discovery['level'] == 0:
            reset_discovery()
        elif st.session_state.discovery['level'] == 1:
            st.session_state.discovery['criteria_type'] = None
            st.session_state.discovery['criteria_value'] = None
        elif st.session_state.discovery['level'] == 2:
            st.session_state.discovery['criteria_value'] = None


def render_breadcrumbs():
    """Render breadcrumb navigation"""
    disc = st.session_state.discovery
    breadcrumbs = ["🏠 Start"]

    if disc['platform']:
        icon = {'facturare': '📄', 'gestiune': '📦', 'spv': '💰', 'api': '🔌', 'aplicatie mobil': '📱'}.get(disc['platform'], '📊')
        breadcrumbs.append(f"{icon} {disc['platform'].title()}")

    if disc['criteria_type']:
        type_icons = {
            'arii': '📂', 'severitate': '🚨', 'sentiment': '😀',
            'problem_type': '🐛', 'perioada': '📅', 'status': '🔄'
        }
        breadcrumbs.append(f"{type_icons.get(disc['criteria_type'], '📊')} {disc['criteria_type'].title()}")

    if disc['criteria_value']:
        breadcrumbs.append(f"→ {disc['criteria_value']}")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(" ".join(breadcrumbs))
    with col2:
        if disc['level'] > 0:
            if st.button("← Înapoi", use_container_width=True):
                go_back()
                st.rerun()


def get_filtered_df(df):
    """Get dataframe filtered by current discovery state"""
    disc = st.session_state.discovery
    filtered = df.copy()

    if disc['platform']:
        filtered = filtered[filtered['platform'] == disc['platform']]

    if disc['criteria_type'] and disc['criteria_value']:
        col_map = {
            'arii': 'area',
            'severitate': 'urgency',
            'sentiment': 'sentiment',
            'problem_type': 'problem_type',
            'status': None  # Special handling
        }

        if disc['criteria_type'] == 'status':
            if disc['criteria_value'] == 'recurrent':
                filtered = filtered[filtered['is_recurrent'] == True]
            elif disc['criteria_value'] == 'business':
                filtered = filtered[filtered['affects_business_flow'] == True]
            elif disc['criteria_value'] == 'agent':
                filtered = filtered[filtered['agent_intervention_needed'] == True]
        else:
            col = col_map.get(disc['criteria_type'])
            if col and col in filtered.columns:
                filtered = filtered[filtered[col] == disc['criteria_value']]

    return filtered


def render_level_0_start(df):
    """Level 0: Choose platform"""
    st.markdown("## 🔬 SmartBill Data Discovery")
    st.markdown("### 📊 Ce vrei să explorezi astăzi?")
    st.markdown("")

    platforms = ['facturare', 'gestiune', 'spv', 'api', 'aplicatie mobil']
    platform_icons = {'facturare': '📄', 'gestiune': '📦', 'spv': '💰', 'api': '🔌', 'aplicatie mobil': '📱'}

    cols = st.columns(3)

    for idx, platform in enumerate(platforms):
        if platform not in df['platform'].values:
            continue

        count = len(df[df['platform'] == platform])

        with cols[idx % 3]:
            st.markdown(f"""
            <div style="
                border: 2px solid #10B981;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
                margin: 10px 0;
                cursor: pointer;
            ">
                <h1 style="margin: 0; font-size: 48px;">{platform_icons.get(platform, '📊')}</h1>
                <h3 style="margin: 10px 0;">{platform.upper()}</h3>
                <p style="color: #10B981; font-size: 20px; margin: 0;">{count} tickete</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Explorează {platform.title()}", key=f"platform_{platform}", use_container_width=True):
                st.session_state.discovery['platform'] = platform
                st.session_state.discovery['level'] = 1
                st.rerun()


def render_level_1_criteria(df):
    """Level 1: Choose grouping criteria"""
    filtered_df = get_filtered_df(df)

    st.markdown(f"## {st.session_state.discovery['platform'].title()} - {len(filtered_df)} tickete")
    st.markdown("### 📊 Cum vrei să explorezi aceste tickete?")
    st.markdown("")

    cols = st.columns(3)

    # Arii Funcționale
    with cols[0]:
        arii_count = filtered_df['area'].nunique() if 'area' in filtered_df.columns else 0
        st.markdown(f"""
        <div style="border: 2px solid #6366F1; border-radius: 10px; padding: 15px; text-align: center; background: #1a1f2e;">
            <h2>📂 ARII</h2>
            <p>{arii_count} arii diferite</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Vezi pe arii", key="criteria_arii", use_container_width=True):
            st.session_state.discovery['criteria_type'] = 'arii'
            st.session_state.discovery['level'] = 2
            st.rerun()

    # Severitate
    with cols[1]:
        blocker_count = len(filtered_df[filtered_df['urgency'] == 'blocker']) if 'urgency' in filtered_df.columns else 0
        st.markdown(f"""
        <div style="border: 2px solid #EF4444; border-radius: 10px; padding: 15px; text-align: center; background: #1a1f2e;">
            <h2>🚨 SEVERITATE</h2>
            <p>🔴 {blocker_count} blockers</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Vezi pe severitate", key="criteria_severitate", use_container_width=True):
            st.session_state.discovery['criteria_type'] = 'severitate'
            st.session_state.discovery['level'] = 2
            st.rerun()

    # Sentiment
    with cols[2]:
        negativ_count = len(filtered_df[filtered_df['sentiment'] == 'negativ']) if 'sentiment' in filtered_df.columns else 0
        st.markdown(f"""
        <div style="border: 2px solid #F59E0B; border-radius: 10px; padding: 15px; text-align: center; background: #1a1f2e;">
            <h2>😀 SENTIMENT</h2>
            <p>😠 {negativ_count} negativ</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Vezi pe sentiment", key="criteria_sentiment", use_container_width=True):
            st.session_state.discovery['criteria_type'] = 'sentiment'
            st.session_state.discovery['level'] = 2
            st.rerun()

    st.markdown("")
    cols2 = st.columns(3)

    # Tip Problemă
    with cols2[0]:
        bug_count = len(filtered_df[filtered_df['problem_type'] == 'bug']) if 'problem_type' in filtered_df.columns else 0
        st.markdown(f"""
        <div style="border: 2px solid #10B981; border-radius: 10px; padding: 15px; text-align: center; background: #1a1f2e;">
            <h2>🐛 TIP PROBLEMĂ</h2>
            <p>🐛 {bug_count} bugs</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Vezi pe tip", key="criteria_problem_type", use_container_width=True):
            st.session_state.discovery['criteria_type'] = 'problem_type'
            st.session_state.discovery['level'] = 2
            st.rerun()

    # Status Special
    with cols2[1]:
        recurrent_count = len(filtered_df[filtered_df['is_recurrent'] == True]) if 'is_recurrent' in filtered_df.columns else 0
        st.markdown(f"""
        <div style="border: 2px solid #8B5CF6; border-radius: 10px; padding: 15px; text-align: center; background: #1a1f2e;">
            <h2>🔄 STATUS</h2>
            <p>🔄 {recurrent_count} recurrent</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Vezi pe status", key="criteria_status", use_container_width=True):
            st.session_state.discovery['criteria_type'] = 'status'
            st.session_state.discovery['level'] = 2
            st.rerun()


def render_level_2_values(df):
    """Level 2: Choose specific value for criteria"""
    filtered_df = get_filtered_df(df)
    criteria_type = st.session_state.discovery['criteria_type']

    st.markdown(f"## Selectează valoarea pentru {criteria_type.title()}")
    st.markdown("")

    col_map = {
        'arii': 'area',
        'severitate': 'urgency',
        'sentiment': 'sentiment',
        'problem_type': 'problem_type'
    }

    if criteria_type == 'status':
        # Special handling for status
        status_options = [
            ('🔄 Recurrent', 'recurrent', len(filtered_df[filtered_df['is_recurrent'] == True])),
            ('💼 Afectează Business', 'business', len(filtered_df[filtered_df['affects_business_flow'] == True])),
            ('🔧 Intervenție Agent', 'agent', len(filtered_df[filtered_df['agent_intervention_needed'] == True]))
        ]

        cols = st.columns(3)
        for idx, (label, value, count) in enumerate(status_options):
            with cols[idx]:
                st.markdown(f"""
                <div style="border: 2px solid #8B5CF6; border-radius: 10px; padding: 20px; text-align: center; background: #1a1f2e;">
                    <h3>{label}</h3>
                    <p style="font-size: 24px; color: #10B981;">{count}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Vezi {label}", key=f"value_{value}", use_container_width=True):
                    st.session_state.discovery['criteria_value'] = value
                    st.session_state.discovery['level'] = 3
                    st.rerun()
    else:
        col = col_map.get(criteria_type)
        if col and col in filtered_df.columns:
            values = filtered_df[col].value_counts().head(10)

            # Icons for different criteria
            icons = {
                'blocker': '🔴', 'mediu': '🟠', 'scazut': '🟡',
                'pozitiv': '😊', 'neutru': '😐', 'negativ': '😠',
                'bug': '🐛', 'feature_gap': '📦', 'usability': '🎨'
            }

            cols = st.columns(min(3, len(values)))
            for idx, (value, count) in enumerate(values.items()):
                with cols[idx % 3]:
                    icon = icons.get(value, '📊')
                    st.markdown(f"""
                    <div style="border: 2px solid #10B981; border-radius: 10px; padding: 20px; text-align: center; background: #1a1f2e;">
                        <h2>{icon}</h2>
                        <h4>{value.title() if isinstance(value, str) else value}</h4>
                        <p style="font-size: 20px; color: #10B981;">{count} tickete</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Explorează", key=f"value_{value}_{idx}", use_container_width=True):
                        st.session_state.discovery['criteria_value'] = value
                        st.session_state.discovery['level'] = 3
                        st.rerun()


def render_level_3_results(df):
    """Level 3: Show results and tickets"""
    filtered_df = get_filtered_df(df)

    criteria_type = st.session_state.discovery['criteria_type']
    criteria_value = st.session_state.discovery['criteria_value']

    # Display title based on criteria
    if criteria_type == 'status':
        status_labels = {'recurrent': '🔄 Recurrent', 'business': '💼 Afectează Business', 'agent': '🔧 Intervenție Agent'}
        title = status_labels.get(criteria_value, criteria_value)
    else:
        icon = {'blocker': '🔴', 'mediu': '🟠', 'scazut': '🟡', 'pozitiv': '😊', 'neutru': '😐', 'negativ': '😠'}.get(criteria_value, '📊')
        title = f"{icon} {criteria_value.title() if isinstance(criteria_value, str) else criteria_value}"

    st.markdown(f"## {title} - {len(filtered_df)} tickete")
    st.markdown("---")

    # Top Problems
    if 'pain_point' in filtered_df.columns and not filtered_df.empty:
        st.markdown("### 🔥 Top 5 Probleme")
        top_problems = filtered_df['pain_point'].value_counts().head(5)

        if not top_problems.empty:
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
                height=300,
                paper_bgcolor='#0E1117',
                plot_bgcolor='#262730',
                font={'color': '#FAFAFA'},
                margin=dict(l=20, r=20, t=20, b=20),
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title='Număr Tickete'
            )

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Tickets list
    st.markdown("### 💬 Tickete")

    if filtered_df.empty:
        st.info("Nu există tickete pentru această selecție")
    else:
        # Sort and paginate
        filtered_df_sorted = filtered_df.sort_values('created_at', ascending=False) if 'created_at' in filtered_df.columns else filtered_df

        items_per_page = 10
        total_pages = max(1, (len(filtered_df_sorted) + items_per_page - 1) // items_per_page)

        page = st.number_input(f"Pagina (1-{total_pages})", min_value=1, max_value=total_pages, value=1) - 1

        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_df_sorted))
        page_df = filtered_df_sorted.iloc[start_idx:end_idx]

        # Render tickets
        for idx, row in page_df.iterrows():
            urgency_icon = '🔴' if row.get('urgency') == 'blocker' else '🟠' if row.get('urgency') == 'mediu' else '🟡'

            with st.expander(
                f"#{idx} | {row.get('created_at', 'N/A').strftime('%d %b %H:%M') if pd.notna(row.get('created_at')) else 'N/A'} | {urgency_icon} {row.get('urgency', 'N/A').title()}",
                expanded=False
            ):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**💬 Problemă:** {row.get('pain_point', 'N/A')}")
                    if pd.notna(row.get('summary')):
                        st.markdown(f"**📝 Sumar:** {row.get('summary')}")

                with col2:
                    st.markdown(f"**Platformă:** {row.get('platform', 'N/A').title()}")
                    st.markdown(f"**Arie:** {row.get('area', 'N/A')}")
                    if pd.notna(row.get('customer_email_extracted')):
                        st.markdown(f"**📧:** {row.get('customer_email_extracted')}")


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
    initialize_discovery_state()

    # Render breadcrumbs
    render_breadcrumbs()

    st.markdown("---")

    # Render appropriate level
    level = st.session_state.discovery['level']

    if level == 0:
        render_level_0_start(df)
    elif level == 1:
        render_level_1_criteria(df)
    elif level == 2:
        render_level_2_values(df)
    elif level == 3:
        render_level_3_results(df)


if __name__ == "__main__":
    main()
