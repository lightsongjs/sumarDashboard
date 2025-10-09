"""
SmartBill Support Analytics Dashboard
Main entry point for the Streamlit application
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import subprocess
import requests
import time

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.data_processor import CSVProcessor
from utils.filters import render_sidebar_filters, show_filter_summary, create_quick_filters_ui

# Page configuration
st.set_page_config(
    page_title="SmartBill Support Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def check_flask_server(port=5000, timeout=1):
    """Check if Flask server is running"""
    try:
        response = requests.get(f"http://localhost:{port}/api/tickets", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def start_flask_server():
    """Start the Flask server in the background"""
    try:
        # Get the path to the Flask server
        flask_server_path = Path(__file__).parent / "ticket_commenter_server.py"

        if not flask_server_path.exists():
            return False

        # Start the Flask server in the background
        if sys.platform == "win32":
            # Windows - use CREATE_NO_WINDOW to hide console
            subprocess.Popen(
                [sys.executable, str(flask_server_path)],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Unix/Linux/Mac
            subprocess.Popen(
                [sys.executable, str(flask_server_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # Wait a bit for server to start
        time.sleep(2)

        # Verify it started
        return check_flask_server(timeout=3)

    except Exception as e:
        return False


def initialize_session_state():
    """Initialize session state variables"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

    if 'df_original' not in st.session_state:
        st.session_state.df_original = None

    if 'csv_file_path' not in st.session_state:
        st.session_state.csv_file_path = None

    if 'flask_started' not in st.session_state:
        st.session_state.flask_started = False


def load_data_from_file(uploaded_file):
    """Load data from uploaded file"""
    try:
        # Save uploaded file temporarily
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Load and process
        with st.spinner('Loading and processing CSV...'):
            df = CSVProcessor.load_csv(tmp_path)

            # Validate
            is_valid, errors = CSVProcessor.validate_dataframe(df)

            if not is_valid:
                st.error("❌ CSV validation failed:")
                for error in errors:
                    st.error(f"  • {error}")
                return None

            # Process
            df_processed = CSVProcessor.process_dataframe(df)

            # Clean up temp file
            os.unlink(tmp_path)

            return df_processed

    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")
        return None


def main():
    """Main application function"""

    initialize_session_state()

    # Auto-start Flask server for Ticket Reviewer (only once)
    if not st.session_state.flask_started:
        if not check_flask_server():
            # Try to start Flask server
            start_flask_server()
        # Mark as attempted (don't retry every rerun)
        st.session_state.flask_started = True

    # Check if default CSV exists
    default_csv_path = Path(__file__).parent / "tickets.csv"

    # Auto-load default CSV if it exists and data not already loaded
    if not st.session_state.data_loaded and default_csv_path.exists():
        try:
            with st.spinner('Loading local CSV...'):
                df = CSVProcessor.load_csv(str(default_csv_path))
                df_processed = CSVProcessor.process_dataframe(df)
                st.session_state.df_original = df_processed
                st.session_state.data_loaded = True
                st.session_state.csv_file_path = str(default_csv_path)
        except Exception as e:
            st.error(f"❌ Error auto-loading tickets.csv: {str(e)}")

    # Header
    st.title("📊 SmartBill Support Analytics Dashboard")
    st.markdown("### Analiză completă a ticket-urilor de suport")

    # File upload section
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "📁 Încarcă fișier CSV cu ticket-uri",
            type=['csv'],
            help="Încarcă un fișier CSV cu structura SmartBill support tickets"
        )

    with col2:
        if default_csv_path.exists():
            if st.button("📂 Folosește tickets.csv local", use_container_width=True):
                with st.spinner('Loading local CSV...'):
                    df = CSVProcessor.load_csv(str(default_csv_path))
                    df_processed = CSVProcessor.process_dataframe(df)
                    st.session_state.df_original = df_processed
                    st.session_state.data_loaded = True
                    st.session_state.csv_file_path = str(default_csv_path)
                    st.success("✅ Date încărcate cu succes!")
                    st.rerun()

    # Load uploaded file
    if uploaded_file is not None:
        df_processed = load_data_from_file(uploaded_file)

        if df_processed is not None:
            st.session_state.df_original = df_processed
            st.session_state.data_loaded = True
            st.session_state.csv_file_path = uploaded_file.name
            st.success(f"✅ Fișier încărcat cu succes: {uploaded_file.name}")

    # Check if we should load mock data
    if not st.session_state.data_loaded and not default_csv_path.exists():
        st.info("💡 **Tip:** Niciun fișier încărcat. Folosim date mock pentru demonstrație.")

        if st.button("🎲 Generează date mock pentru demo", use_container_width=True):
            with st.spinner('Generating mock data...'):
                df_mock = CSVProcessor.get_mock_data()
                st.session_state.df_original = df_mock
                st.session_state.data_loaded = True
                st.session_state.csv_file_path = "mock_data"
                st.rerun()

    # If data is loaded, show preview and navigation
    if st.session_state.data_loaded and st.session_state.df_original is not None:

        st.markdown("---")

        # Data overview
        st.subheader("📋 Date încărcate")

        df = st.session_state.df_original

        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("📊 Total Tickets", f"{len(df):,}")

        with col2:
            if 'created_at' in df.columns:
                date_range_days = (df['created_at'].max() - df['created_at'].min()).days
                st.metric("📅 Perioada (zile)", f"{date_range_days:,}")

        with col3:
            if 'platform' in df.columns:
                st.metric("🏢 Platforme", df['platform'].nunique())

        with col4:
            if 'area' in df.columns:
                st.metric("📍 Arii", df['area'].nunique())

        with col5:
            if 'urgency' in df.columns and 'blocker' in df['urgency'].values:
                blocker_count = len(df[df['urgency'] == 'blocker'])
                st.metric("🚨 Blockers", blocker_count)

        # Data preview
        with st.expander("👁️ Previzualizare date (primele 10 rânduri)", expanded=False):
            st.dataframe(
                df.head(10),
                use_container_width=True,
                height=300
            )

        # Data quality info
        with st.expander("ℹ️ Informații despre date", expanded=False):
            summary = CSVProcessor.get_data_summary(df)

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Interval temporal:**")
                if summary['date_range']['start'] and summary['date_range']['end']:
                    st.write(f"- Start: {summary['date_range']['start'].strftime('%Y-%m-%d')}")
                    st.write(f"- End: {summary['date_range']['end'].strftime('%Y-%m-%d')}")

            with col2:
                st.write("**Valori unice per categorie:**")
                for col, count in summary['unique_values'].items():
                    st.write(f"- {col}: {count}")

            # Missing values
            if summary['missing_values']:
                st.write("**Valori lipsă:**")
                missing_df = pd.DataFrame([
                    {'Column': col, 'Missing': count}
                    for col, count in summary['missing_values'].items()
                    if count > 0
                ])
                if not missing_df.empty:
                    st.dataframe(missing_df, use_container_width=True)

        st.markdown("---")
        st.success("✅ Date încărcate cu succes! Acum poți naviga la orice pagină folosind sidebar-ul.")

    else:
        # No data loaded - show welcome screen
        st.markdown("---")

        st.markdown("""
        ## 👋 Bine ai venit!

        Acest dashboard îți permite să analizezi ticket-urile de suport SmartBill într-un mod vizual și interactiv.

        ### 🚀 Cum să începi:

        1. **Încarcă un fișier CSV** folosind upload-ul de mai sus
        2. Sau **folosește fișierul local** `tickets.csv` dacă există
        3. Sau **generează date mock** pentru o demonstrație

        ### 📊 Ce poți face:

        - 📈 Vizualizează tendințe și patterns în tickets
        - 🔍 Filtrează după platformă, urgență, sentiment, etc.
        - 🔥 Identifică cele mai frecvente probleme (pain points)
        - 👥 Analizează performanța echipei
        - 📤 Exportă rapoarte în PDF, Excel sau PowerPoint

        ### 📋 Structura CSV așteptată:

        CSV-ul trebuie să conțină următoarele coloane:
        - `created_at`, `closed_at` - Date și ore
        - `platform` - Facturare, Gestiune, SPV, API, etc.
        - `area` - Area funcțională
        - `urgency` - Blocker, Mediu, Scazut
        - `sentiment` - Pozitiv, Neutru, Negativ
        - `problem_type` - Feature_Gap, Bug, Usability, etc.
        - `pain_point` - Descrierea problemei
        - Și altele...

        """)

        # Show example CSV structure
        with st.expander("📄 Vezi exemplu de structură CSV"):
            example_data = {
                'created_at': ['2024-01-15 10:30:00', '2024-01-15 11:45:00'],
                'platform': ['Facturare', 'SPV'],
                'area': ['Modificare factura', 'Date firma'],
                'urgency': ['blocker', 'mediu'],
                'sentiment': ['negativ', 'neutru'],
                'problem_type': ['Bug', 'Feature_Gap'],
                'pain_point': ['Nu se pot modifica facturile...', 'Lipsă opțiune pentru...']
            }
            st.dataframe(pd.DataFrame(example_data), use_container_width=True)


if __name__ == "__main__":
    main()
