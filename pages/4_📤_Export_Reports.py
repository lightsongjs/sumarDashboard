"""
Reports & Export Page - Generate and export reports in various formats
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor
from utils.filters import render_sidebar_filters, show_filter_summary
from utils.export import (
    export_to_excel, export_to_csv, create_summary_report,
    generate_excel_report, export_charts_data, export_to_excel_multiple_sheets
)

# Page config
st.set_page_config(
    page_title="Reports - SmartBill Analytics",
    page_icon="📤",
    layout="wide"
)


def main():
    """Main reports function"""

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
    st.title("📤 Rapoarte și Export")
    st.markdown("### Generare și export rapoarte în diferite formate")

    st.markdown("---")

    # Show filter summary
    show_filter_summary(df_original, df_filtered)

    st.markdown("---")

    # Check if we have data
    if len(df_filtered) == 0:
        st.warning("⚠️ Nu există date pentru filtrele selectate.")
        return

    # Export Options
    st.subheader("📊 Opțiuni de Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📄 CSV Export")
        st.markdown("Export date filtrate în format CSV")

        if st.button("📥 Export CSV Simplu", use_container_width=True, type="primary"):
            csv_data = export_to_csv(df_filtered)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name=f"smartbill_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col2:
        st.markdown("### 📊 Excel Export")
        st.markdown("Export date în format Excel (.xlsx)")

        if st.button("📥 Export Excel Simplu", use_container_width=True):
            excel_data = export_to_excel(df_filtered, sheet_name='Tickets')
            st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=f"smartbill_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    with col3:
        st.markdown("### 📋 Excel Complet")
        st.markdown("Excel cu multiple sheets și statistici")

        if st.button("📥 Export Excel Complet", use_container_width=True):
            # Create summary stats
            summary_stats = create_summary_report(df_filtered)

            # Generate comprehensive report
            excel_report = generate_excel_report(df_filtered, summary_stats)

            st.download_button(
                label="⬇️ Download Raport Complet",
                data=excel_report,
                file_name=f"smartbill_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    st.markdown("---")

    # Report Customization
    st.subheader("🎨 Personalizare Raport")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Selectează Coloanele de Export")

        all_columns = df_filtered.columns.tolist()

        # Default important columns
        default_columns = []
        for col in ['created_at', 'closed_at', 'platform', 'area', 'urgency',
                    'sentiment', 'problem_type', 'pain_point', 'summary', 'is_recurrent']:
            if col in all_columns:
                default_columns.append(col)

        selected_columns = st.multiselect(
            "Coloane de inclus în export:",
            options=all_columns,
            default=default_columns
        )

    with col2:
        st.markdown("#### Opțiuni Export")

        include_summary = st.checkbox("Include statistici rezumative", value=True)
        include_charts_data = st.checkbox("Include date pentru grafice", value=False)
        sort_by = st.selectbox(
            "Sortare după:",
            options=['created_at', 'urgency', 'platform', 'priority_score'],
            index=0
        )
        sort_order = st.radio(
            "Ordine:",
            options=['Descrescător', 'Crescător'],
            horizontal=True
        )

    # Custom Export Button
    if st.button("📤 Generează Raport Personalizat", use_container_width=True, type="primary"):
        if not selected_columns:
            st.error("⚠️ Selectează cel puțin o coloană!")
        else:
            # Sort data
            ascending = sort_order == 'Crescător'
            if sort_by in df_filtered.columns:
                df_export = df_filtered[selected_columns].sort_values(sort_by, ascending=ascending)
            else:
                df_export = df_filtered[selected_columns]

            # Create sheets dictionary
            sheets = {'Tickets': df_export}

            # Add summary if requested
            if include_summary:
                summary = create_summary_report(df_filtered)
                summary_df = pd.DataFrame([summary['Metadata']])
                sheets['Summary'] = summary_df

            # Add chart data if requested
            if include_charts_data:
                chart_data = export_charts_data(df_filtered)
                for name, data in chart_data.items():
                    if len(name) <= 31:  # Excel sheet name limit
                        sheets[name] = data

            # Generate Excel
            excel_data = export_to_excel_multiple_sheets(sheets)

            st.download_button(
                label="⬇️ Download Raport Personalizat",
                data=excel_data,
                file_name=f"smartbill_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    st.markdown("---")

    # Report Preview
    st.subheader("👁️ Previzualizare Date Export")

    if selected_columns:
        preview_limit = st.slider("Număr rânduri previzualizare:", 5, 100, 20)

        # Sort for preview
        ascending = sort_order == 'Crescător'
        if sort_by in df_filtered.columns:
            df_preview = df_filtered[selected_columns].sort_values(sort_by, ascending=ascending).head(preview_limit)
        else:
            df_preview = df_filtered[selected_columns].head(preview_limit)

        st.dataframe(df_preview, use_container_width=True, height=400)

        # Show stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Rânduri", f"{len(df_filtered):,}")

        with col2:
            st.metric("Coloane Selectate", len(selected_columns))

        with col3:
            if 'urgency' in df_filtered.columns:
                blockers = len(df_filtered[df_filtered['urgency'] == 'blocker'])
                st.metric("Blockers", f"{blockers:,}")

        with col4:
            if 'sentiment' in df_filtered.columns:
                positive = len(df_filtered[df_filtered['sentiment'] == 'pozitiv'])
                positive_pct = (positive / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
                st.metric("Sentiment Pozitiv", f"{positive_pct:.1f}%")

    else:
        st.info("👆 Selectează coloane pentru a vedea previzualizarea")

    st.markdown("---")

    # Quick Reports
    st.subheader("⚡ Rapoarte Rapide")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚨 Doar Blockers", use_container_width=True):
            if 'urgency' in df_filtered.columns:
                blockers_df = df_filtered[df_filtered['urgency'] == 'blocker']
                if len(blockers_df) > 0:
                    csv_data = export_to_csv(blockers_df)
                    st.download_button(
                        label="⬇️ Download Blockers CSV",
                        data=csv_data,
                        file_name=f"blockers_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("✅ Nu există blockers!")
            else:
                st.warning("Coloana 'urgency' nu există")

    with col2:
        if st.button("🔁 Doar Recurente", use_container_width=True):
            if 'is_recurrent' in df_filtered.columns:
                recurrent_df = df_filtered[df_filtered['is_recurrent'] == True]
                if len(recurrent_df) > 0:
                    csv_data = export_to_csv(recurrent_df)
                    st.download_button(
                        label="⬇️ Download Recurente CSV",
                        data=csv_data,
                        file_name=f"recurrent_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Nu există probleme recurente")
            else:
                st.warning("Coloana 'is_recurrent' nu există")

    with col3:
        if st.button("😞 Sentiment Negativ", use_container_width=True):
            if 'sentiment' in df_filtered.columns:
                negative_df = df_filtered[df_filtered['sentiment'] == 'negativ']
                if len(negative_df) > 0:
                    csv_data = export_to_csv(negative_df)
                    st.download_button(
                        label="⬇️ Download Negative CSV",
                        data=csv_data,
                        file_name=f"negative_sentiment_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("✅ Nu există feedback negativ!")
            else:
                st.warning("Coloana 'sentiment' nu există")

    with col4:
        if st.button("💼 Impact Business", use_container_width=True):
            if 'affects_business_flow' in df_filtered.columns:
                business_df = df_filtered[df_filtered['affects_business_flow'] == True]
                if len(business_df) > 0:
                    csv_data = export_to_csv(business_df)
                    st.download_button(
                        label="⬇️ Download Business Impact CSV",
                        data=csv_data,
                        file_name=f"business_impact_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("Nu există tickets cu impact business")
            else:
                st.warning("Coloana 'affects_business_flow' nu există")

    st.markdown("---")

    # Report Summary
    st.subheader("📊 Rezumat Date Curente")

    summary = create_summary_report(df_filtered)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Metadata")
        for key, value in summary['Metadata'].items():
            st.markdown(f"**{key}:** {value}")

    with col2:
        st.markdown("#### 📈 Metrici Cheie")
        for key, value in summary.get('Key Metrics', {}).items():
            st.markdown(f"**{key}:** {value}")

    st.markdown("---")

    # Info section
    st.info("""
    ### 💡 Sfaturi pentru Export

    **CSV:**
    - Ideal pentru import în alte aplicații
    - Compatibil cu Excel, Google Sheets
    - Encoding UTF-8 cu BOM pentru caractere speciale

    **Excel Simplu:**
    - Un singur sheet cu toate datele
    - Formatare automată header
    - Coloane auto-ajustate

    **Excel Complet:**
    - Multiple sheets: Summary, Tickets, By Platform, By Urgency, Blockers
    - Statistici și breakdown-uri
    - Ideal pentru raportare management

    **Raport Personalizat:**
    - Selectează exact coloanele necesare
    - Sortare personalizată
    - Include/exclude statistici după preferință
    """)


if __name__ == "__main__":
    main()
