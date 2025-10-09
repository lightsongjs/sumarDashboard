"""
Raw Data Page
Interactive data table with filtering, sorting, and export capabilities
"""

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from st_aggrid.shared import JsCode
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_processor import CSVProcessor, auto_load_default_csv
from utils.filters import render_sidebar_filters

# Page configuration
st.set_page_config(
    page_title="Raw Data",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)


def create_aggrid_table(df):
    """Create interactive AG Grid table with all features"""

    # Configure grid options
    gb = GridOptionsBuilder.from_dataframe(df)

    # Enable filtering on all columns
    gb.configure_default_column(
        filterable=True,
        sortable=True,
        resizable=True,
        filter=True,
        editable=False
    )

    # Enable selection (optional)
    gb.configure_selection(selection_mode='multiple', use_checkbox=False)

    # Grid options
    gb.configure_grid_options(
        domLayout='normal',  # Normal layout (not autoHeight)
        enableRangeSelection=True,
        suppressPaginationPanel=True,  # No pagination
        suppressScrollOnNewData=True,
        rowSelection='multiple'
    )

    # Alternating row colors (zebra striping)
    cell_style_jscode = JsCode("""
    function(params) {
        if (params.node.rowIndex % 2 === 0) {
            return {
                'backgroundColor': '#f8f9fa'
            }
        }
        return {
            'backgroundColor': 'white'
        }
    }
    """)

    # Apply alternating colors to all columns
    for col in df.columns:
        gb.configure_column(col, cellStyle=cell_style_jscode)

    # Special formatting for specific columns
    if 'created_at' in df.columns:
        gb.configure_column('created_at', type=['dateColumnFilter', 'customDateTimeFormat'], custom_format_string='yyyy-MM-dd HH:mm')

    if 'closed_at' in df.columns:
        gb.configure_column('closed_at', type=['dateColumnFilter', 'customDateTimeFormat'], custom_format_string='yyyy-MM-dd HH:mm')

    # Color coding for urgency
    if 'urgency' in df.columns:
        urgency_style = JsCode("""
        function(params) {
            var bgColor = 'white';
            if (params.node.rowIndex % 2 === 0) {
                bgColor = '#f8f9fa';
            }

            var color = 'black';
            if (params.value === 'blocker') {
                color = '#dc3545';
            } else if (params.value === 'mediu') {
                color = '#fd7e14';
            } else if (params.value === 'scazut') {
                color = '#28a745';
            }

            return {
                'backgroundColor': bgColor,
                'color': color,
                'fontWeight': params.value === 'blocker' ? 'bold' : 'normal'
            }
        }
        """)
        gb.configure_column('urgency', cellStyle=urgency_style)

    # Color coding for sentiment
    if 'sentiment' in df.columns:
        sentiment_style = JsCode("""
        function(params) {
            var bgColor = 'white';
            if (params.node.rowIndex % 2 === 0) {
                bgColor = '#f8f9fa';
            }

            var color = 'black';
            if (params.value === 'pozitiv') {
                color = '#28a745';
            } else if (params.value === 'negativ') {
                color = '#dc3545';
            }

            return {
                'backgroundColor': bgColor,
                'color': color
            }
        }
        """)
        gb.configure_column('sentiment', cellStyle=sentiment_style)

    grid_options = gb.build()

    # Render AG Grid
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
        theme='streamlit',  # Use Streamlit theme
        height=700,  # Fixed height with scrolling
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False
    )

    return grid_response


def main():
    """Main application function"""

    # Auto-load CSV if available
    auto_load_default_csv()

    st.title("📋 Raw Data - Date Complete")
    st.markdown("### Tabel interactiv cu toate datele - filtrare, sortare, export")

    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.warning("⚠️ Nu există date încărcate. Vă rugăm să încărcați un fișier CSV de pe pagina principală.")

        if st.button("🏠 Mergi la pagina principală", use_container_width=True):
            st.switch_page("app.py")
        return

    # Get data from session state
    df_original = st.session_state.df_original

    # Render sidebar filters
    st.sidebar.markdown("## 🔍 Filtre")
    filter_params = render_sidebar_filters(df_original)

    # Apply filters
    df_filtered = CSVProcessor.apply_filters(df_original, **filter_params)

    # Quick stats
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📊 Total Tickets", f"{len(df_filtered):,}")

    with col2:
        if 'platform' in df_filtered.columns:
            st.metric("🏢 Platforme", df_filtered['platform'].nunique())

    with col3:
        if 'urgency' in df_filtered.columns and 'blocker' in df_filtered['urgency'].values:
            blocker_count = len(df_filtered[df_filtered['urgency'] == 'blocker'])
            st.metric("🚨 Blockers", blocker_count)
        else:
            st.metric("🚨 Blockers", 0)

    with col4:
        if 'is_recurrent' in df_filtered.columns:
            recurrent_count = len(df_filtered[df_filtered['is_recurrent'] == True])
            st.metric("🔄 Recurente", recurrent_count)
        else:
            st.metric("🔄 Recurente", "-")

    with col5:
        if 'created_at' in df_filtered.columns:
            date_range_days = (df_filtered['created_at'].max() - df_filtered['created_at'].min()).days
            st.metric("📅 Interval (zile)", f"{date_range_days:,}")

    st.markdown("---")

    # Export section
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("**💡 Tip:** Click pe headerele coloanelor pentru a sorta. Folosește filtrele din sidebar sau din tabel.")

    with col2:
        # Export to CSV
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv,
            file_name=f"raw_data_{len(df_filtered)}_tickets.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col3:
        # Export to Excel
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_filtered.to_excel(writer, index=False, sheet_name='Raw Data')
        excel_data = output.getvalue()

        st.download_button(
            label="📥 Export Excel",
            data=excel_data,
            file_name=f"raw_data_{len(df_filtered)}_tickets.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.markdown("---")

    # Display AG Grid table
    if len(df_filtered) == 0:
        st.warning("⚠️ Nu există date care să corespundă filtrelor selectate.")
    else:
        # Info about filtering
        if len(df_filtered) < len(df_original):
            st.info(f"📊 Se afișează {len(df_filtered):,} din {len(df_original):,} tickets (filtrate)")

        # Create and display table
        grid_response = create_aggrid_table(df_filtered)

        # Show selection info
        selected_rows = grid_response['selected_rows']
        if selected_rows is not None and len(selected_rows) > 0:
            st.success(f"✅ {len(selected_rows)} rânduri selectate")


if __name__ == "__main__":
    main()
