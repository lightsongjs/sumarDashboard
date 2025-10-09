# SmartBill Support Analytics Dashboard - Claude Documentation

## Project Overview

This is a comprehensive Streamlit-based analytics dashboard for SmartBill support ticket analysis. The application has been refactored to v3.0 with consolidated pages and an embedded ticket review interface.

---

## Architecture

### v3.0 Consolidation (Latest)

The dashboard was refactored from 14 pages to 3 focused pages:

1. **Strategic Dashboard** - Consolidated KPIs, visualizations, and metrics
2. **Investigation Hub** - Pain points analysis and deep-dive exploration
3. **Ticket Reviewer** - Individual ticket review with Flask backend (auto-starts)

---

## Tech Stack

### Core Frameworks
- **Streamlit 1.40+** - Main dashboard framework
- **Flask 3.1+** - Backend for Ticket Reviewer
- **Python 3.12** - Programming language

### Data Processing
- **Pandas 2.2+** - Data manipulation
- **NumPy 1.26+** - Numerical operations

### Visualization
- **Plotly 5.24+** - Interactive charts
- **Matplotlib 3.9+** - Static plots
- **Seaborn 0.13+** - Statistical visualizations

### Export & Reporting
- **OpenPyXL 3.1+** - Excel file operations
- **XlsxWriter 3.2+** - Excel formatting
- **ReportLab 4.2+** - PDF generation
- **FPDF2 2.8+** - PDF creation

### Additional Libraries
- **Flask-CORS** - Cross-origin requests for Ticket Reviewer
- **python-dotenv 1.0+** - Environment variable management
- **chardet 5.2+** - Character encoding detection
- **streamlit-extras 0.4+** - Extended Streamlit components
- **streamlit-option-menu 0.4+** - Navigation menus
- **streamlit-aggrid 0.3+** - Data grid component

---

## File Structure

```
sumarDashboard/
├── app.py                          # Main entry point
├── requirements.txt                # Python dependencies
├── tickets.csv                     # Data file (excluded from git)
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── .claude/
│   ├── settings.local.json         # Claude Code settings
│   └── claude.md                   # This file
├── utils/                          # Utility modules
│   ├── data_processor.py           # CSV loading and processing
│   ├── charts.py                   # Plotly chart generation
│   ├── filters.py                  # Sidebar filter rendering
│   └── export.py                   # Report export functionality
├── pages/                          # Streamlit pages (v3.0)
│   ├── 1_📊_Strategic_Dashboard.py
│   ├── 2_🔬_Investigation_Hub.py
│   └── 3_📝_Ticket_Reviewer.py
├── ticket_commenter_server.py      # Flask backend for ticket reviewer
└── ticket_commenter_static/        # Ticket reviewer frontend
    ├── app.js                      # JavaScript logic
    ├── index.html                  # HTML interface
    └── style.css                   # Styles
```

---

## CSV Data Schema

### Required Columns
- `created_at` - Datetime (when ticket was created)
- `closed_at` - Datetime (when ticket was closed)
- `platform` - Platform name (facturare, gestiune, api, spv, etc.)
- `area` - Functional area

### Optional Columns (28 total)
- `ticket_url` - Link to ticket
- `mailbox_name` - Mailbox type
- `customer_email_extracted` - Client email
- `gdrp_free_conversation` or `formatted_conversation` - Ticket conversation
- `taxonomy` - Ticket taxonomy
- `tip` - Ticket type (problema tehnica, feature request, etc.)
- `sentiment` - pozitiv, neutru, negativ
- `apreciere_parere_support` - Support rating
- `urgency` - blocker, mediu, scazut
- `is_recurrent` - Boolean (TRUE/FALSE)
- `agent_intervention_needed` - Boolean
- `summary` - Ticket summary
- `user_goal` - What user wanted to achieve
- `pain_point` - Main problem description
- `problem_type` - feature_gap, bug, usability, documentation, performance, integration
- `affects_business_flow` - Boolean
- `integration` - Integration name
- `mentioned_features` - Features mentioned
- `specific_error_messages` - Error messages
- `classification_index` - Index for classification
- `total_classifications` - Total number of classifications
- `Comments` - User comments (added by Ticket Reviewer)

### Valid Values

**urgency:**
- blocker
- mediu
- scazut

**sentiment:**
- pozitiv
- neutru
- negativ

**platform:**
- facturare
- gestiune
- api
- aplicatie mobil
- spv
- niciunul

**problem_type:**
- feature_gap
- usability
- documentation
- bug
- performance
- integration

**tip:**
- problema tehnica
- feature request
- cerere administrativa/comerciala
- intrebare contabila/fiscala

---

## Key Features

### 1. Strategic Dashboard
- **KPIs:** Total tickets, avg resolution time, blocker count, recurrent issues
- **Charts:** Platform distribution, urgency levels, sentiment breakdown, timeline
- **Pain Points:** Word cloud, top 10 problems, area matrix
- **Filters:** Date range, platform, area, urgency, sentiment, recurrent, business impact

### 2. Investigation Hub
- **Deep Dive:** Drill-down into specific problems
- **Pattern Detection:** Identify recurring issues
- **Word Analysis:** Frequency analysis of pain points
- **Export:** Dedicated export for investigation results

### 3. Ticket Reviewer
- **Navigation:** Keyboard shortcuts (Ctrl + ←/→), Previous/Next buttons, Jump to ticket #
- **Filters:** Mailbox, Tip, Area, Sentiment, Urgency, Platform, Integration, Recurrent, Agent Needed, Ticket ID
- **Comments:** Auto-save textarea (500ms debounce), persists to CSV
- **Conversation:** Full view of client-agent conversation
- **Backend:** Flask server on port 5000
- **Frontend:** Vanilla JS, no framework dependencies

---

## Running the Application

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run Streamlit dashboard (Flask auto-starts in background)
streamlit run app.py

# Or with specific port
streamlit run app.py --server.port 8502
```

**Note:** The Flask backend for Ticket Reviewer starts automatically when you run the Streamlit app. No need to start a separate server!

### Accessing Pages
- Strategic Dashboard: Main page at http://localhost:8501
- Investigation Hub: Available in sidebar
- Ticket Reviewer: Opens in new tab at http://localhost:5000

---

## Development Notes

### Data Processing (`utils/data_processor.py`)

**CSVProcessor class methods:**
- `load_csv()` - Load CSV with auto-encoding detection
- `validate_dataframe()` - Validate required columns
- `process_dataframe()` - Clean and normalize data
- `apply_filters()` - Apply user-selected filters
- `get_data_summary()` - Get summary statistics
- `get_mock_data()` - Generate mock data for testing

**Key Processing Steps:**
1. Auto-detect encoding (UTF-8, Latin-1, CP1252 supported)
2. Convert dates to datetime objects
3. Normalize text (lowercase, trim whitespace)
4. Convert boolean columns
5. Add computed columns (resolution_time, created_date, priority_score)

### Filters (`utils/filters.py`)

**Available Filters:**
- Date range (with quick select: 7d, 30d, 90d)
- Multi-select: Platform, Area, Urgency
- Radio: Sentiment
- Toggles: Recurrent only, Business impact only
- Search: Text search in pain points/summary

### Charts (`utils/charts.py`)

**Chart Types:**
- Bar charts (platform distribution, urgency, etc.)
- Pie charts (sentiment breakdown)
- Timeline charts (tickets over time)
- Scatter plots (resolution time analysis)
- Heatmaps (area × problem type)

### Export (`utils/export.py`)

**Export Functions:**
- `export_to_csv()` - Simple CSV export
- `export_to_excel_simple()` - Single sheet Excel
- `export_to_excel_multi()` - Multiple sheets with formatting
- `export_to_pdf()` - PDF report with charts
- `export_to_powerpoint()` - PowerPoint presentation

---

## Ticket Reviewer Architecture

### Backend (Flask)

**File:** `ticket_commenter_server.py`

**Routes:**
- `GET /` - Serve HTML interface
- `GET /api/tickets` - Return all tickets as JSON
- `POST /api/tickets/<index>/comment` - Update ticket comment

**Features:**
- CORS enabled for cross-origin requests
- CSV field size limit: 10MB
- UTF-8 encoding support
- Auto-reload on file changes (debug mode)

### Frontend (Vanilla JS)

**Files:**
- `ticket_commenter_static/index.html` - UI structure
- `ticket_commenter_static/app.js` - Logic
- `ticket_commenter_static/style.css` - Styling

**Key Features:**
- Dropdown multi-select filters
- Keyboard navigation (Ctrl + arrows)
- Auto-save with debounce (500ms)
- LocalStorage for filter/position persistence
- Conversation parsing (CLIENT/AGENT format)

**Conversation Format:**
```
[CLIENT - 2025-08-12 11:24]
Client message here...

[AGENT - 2025-08-12 12:03]
Agent response here...
```

---

## Git Workflow

### Branches
- `master` - Production-ready code
- `feature/v3-consolidation` - v3.0 refactoring (merged)
- `embedding_ticket_commenter` - Ticket reviewer integration (merged)
- `feature/auto-start-flask` - Flask auto-start implementation (merged)
- `feature/remove-team-export-pages` - v3.1 simplification (current)

### Excluded from Git (.gitignore)
- `tickets.csv` - Client data
- `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `.DS_Store` - Mac files
- `*.pyc` - Compiled Python

---

## Common Tasks

### Adding a New Page

1. Create file in `pages/` with naming: `N_EMOJI_Name.py`
2. Import required utilities from `utils/`
3. Add page configuration:
   ```python
   st.set_page_config(
       page_title="Page Name",
       page_icon="📊",
       layout="wide"
   )
   ```
4. Check data loaded: `st.session_state.data_loaded`
5. Use `st.session_state.df_original` for data

### Adding a New Filter

1. Add filter UI in `utils/filters.py` → `render_sidebar_filters()`
2. Update filter parameters in `utils/data_processor.py` → `apply_filters()`
3. Test with various filter combinations

### Adding a New Chart

1. Add chart function in `utils/charts.py`
2. Use Plotly for interactive charts
3. Return `fig` object
4. Display with `st.plotly_chart(fig, use_container_width=True)`

### Adding a New Export Format

1. Add export function in `utils/export.py`
2. Add export button in any page (e.g., Strategic Dashboard or Investigation Hub)
3. Handle file download with `st.download_button()`

---

## Troubleshooting

### Streamlit Issues

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

**Cache issues:**
```bash
streamlit cache clear
```

### Flask Issues

**Port 5000 already in use:**
```python
# Edit ticket_commenter_server.py
app.run(debug=True, port=5001)  # Change port
```

**CORS errors:**
- Check Flask-CORS is installed
- Verify `CORS(app)` is called in server.py

### Data Issues

**CSV won't load:**
- Check encoding (should be UTF-8 or Latin-1)
- Verify required columns exist
- Check for very large fields (>10MB)

**Filters not working:**
- Check column names (case-sensitive)
- Verify data types (lowercase for text)
- Check for null values

---

## Future Enhancements

### Potential Features
- AI-powered ticket categorization
- Sentiment analysis improvements
- Real-time data refresh
- Multi-user collaboration
- Advanced search with NLP
- Automated report scheduling
- Integration with ticketing systems

### Known Limitations
- Single CSV file support (no database)
- No user authentication
- Comments in Ticket Reviewer stored in same CSV
- Flask server runs in debug mode (not production-ready)

---

## Version History

### v3.1 (Current)
- Simplified to 3 core pages (removed Team Performance and Export Reports)
- Flask server auto-starts with Streamlit (single command)
- Streamlined focus on ticket analysis and review

### v3.0
- Consolidated 14 pages → 5 pages
- Added Ticket Reviewer with Flask backend
- Improved performance with better caching
- Enhanced export capabilities

### v2.0
- Added multiple export formats
- Team performance analytics
- Advanced filtering

### v1.0
- Initial dashboard with basic KPIs
- Pain points analysis
- Simple export

---

**Last Updated:** 2025-10-09
**Maintained By:** Development Team
**Built With:** Claude Code
