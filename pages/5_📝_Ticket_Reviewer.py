"""
Ticket Reviewer Page
Embeds the exact ticket-commenter Flask app interface
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import subprocess
import sys
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Ticket Reviewer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def check_flask_server(port=5000):
    """Check if Flask server is running"""
    try:
        response = requests.get(f"http://localhost:{port}/api/tickets", timeout=1)
        return response.status_code == 200
    except:
        return False


def start_flask_server():
    """Start the Flask server in the background"""
    try:
        # Get the path to the Flask server
        flask_server_path = Path(__file__).parent.parent / "ticket_commenter_server.py"

        # Change to the sumarDashboard directory
        os.chdir(Path(__file__).parent.parent)

        # Start the Flask server in the background
        if sys.platform == "win32":
            # Windows
            subprocess.Popen(
                ["python", str(flask_server_path)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Unix/Linux/Mac
            subprocess.Popen(
                ["python", str(flask_server_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        return True
    except Exception as e:
        st.error(f"Failed to start Flask server: {str(e)}")
        return False


def main():
    """Main application function"""

    # Hide Streamlit header and footer for a cleaner iframe experience
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Check if Flask server is running
    server_running = check_flask_server()

    if not server_running:
        st.title("📝 Ticket Reviewer")
        st.warning("⚠️ The ticket reviewer interface needs the Flask server to be running.")

        st.markdown("### To start the Flask server:")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.code("cd sumarDashboard\npython ticket_commenter_server.py", language="bash")

        with col2:
            if st.button("🚀 Auto-start Server", use_container_width=True):
                with st.spinner("Starting Flask server..."):
                    if start_flask_server():
                        st.success("✅ Server starting... Please refresh this page in a few seconds.")
                        st.balloons()
                    else:
                        st.error("❌ Failed to start server. Please start it manually.")

        st.markdown("---")

        st.info("💡 Once the server is running, refresh this page to see the ticket reviewer interface.")

        # Show a refresh button
        if st.button("🔄 Refresh Page", use_container_width=False):
            st.rerun()

    else:
        # Server is running - open in new tab
        st.markdown("""
            <style>
            .open-tab-button {
                display: inline-block;
                padding: 20px 40px;
                font-size: 24px;
                font-weight: bold;
                color: white;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 10px;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                margin: 50px auto;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease;
            }
            .open-tab-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            }
            </style>
            <script>
                // Auto-open in new tab
                window.open('http://localhost:5000', '_blank');
            </script>
        """, unsafe_allow_html=True)

        st.title("📝 Ticket Reviewer")
        st.success("✅ Flask server is running!")

        st.markdown("---")

        st.info("The Ticket Reviewer has been opened in a new tab.")

        st.markdown("""
            <div style="text-align: center;">
                <a href="http://localhost:5000" target="_blank" class="open-tab-button">
                    🔗 Open Ticket Reviewer in New Tab
                </a>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("**💡 Tip:** You can close this tab and use the Ticket Reviewer directly at http://localhost:5000")


if __name__ == "__main__":
    main()
