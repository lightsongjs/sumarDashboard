# 📊 SmartBill Support Analytics Dashboard

**Version 3.1** - Comprehensive analytics platform for SmartBill support ticket analysis

![Status](https://img.shields.io/badge/status-production-success)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.40+-red)
![Flask](https://img.shields.io/badge/flask-3.1+-green)

---

## 🎯 Overview

SmartBill Support Analytics Dashboard este o platformă de analiză avansată pentru ticket-urile de suport, oferind:
- **Dashboard executiv** cu KPI-uri și metrici detaliate
- **Investigare avansată** cu filtre multiple și vizualizări interactive
- **Ticket Reviewer** pentru review individual cu comentarii auto-save
- **Export multi-format** (CSV, Excel, PDF)
- **Documentație completă** pentru calculul indicatorilor

---

## 🚀 Quick Start

### Prerequisite
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### 1. Instalare

```bash
# Instalează uv (dacă nu e deja instalat)
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonează repository
git clone https://github.com/lightsongjs/sumarDashboard.git
cd sumarDashboard

# Creează virtual environment
uv venv

# Instalează dependențe
uv pip install -r requirements.txt

# În caz de probleme, forțează reinstalarea
uv pip install -r requirements.txt --force-reinstall
```

### 2. Rulare

```bash
# Activează virtual environment
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Pornește aplicația (Flask auto-start pentru Ticket Reviewer)
streamlit run app.py
```

### 3. Accesare

- **Dashboard Principal:** http://localhost:8501
- **Ticket Reviewer:** http://localhost:5000 (auto-start în background)

---

## 📁 Structură Proiect

```
📦 sumarDashboard/
├── 📄 app.py                           # Entry point principal
├── 📄 requirements.txt                 # Dependențe Python
├── 📄 tickets.csv                      # Date (EXCLUDED din git)
├── 📄 INDICATOR_CALCULATIONS.md        # Documentație calcul indicatori
├── 📄 README.md                        # Acest fișier
│
├── 📁 .streamlit/
│   └── config.toml                     # Configurare Streamlit
│
├── 📁 .claude/
│   ├── settings.local.json             # Setări Claude Code
│   └── CLAUDE.md                       # Documentație tehnică completă
│
├── 📁 utils/                           # Module utilitare
│   ├── __init__.py
│   ├── data_processor.py               # Încărcare și procesare CSV
│   ├── charts.py                       # Generare grafice Plotly
│   ├── filters.py                      # Filtre sidebar (deprecated)
│   └── export.py                       # Export rapoarte
│
├── 📁 pages/                           # Pagini Streamlit (v3.1)
│   ├── 1_📊_DASHBOARD.py               # Dashboard executiv
│   ├── 2_🔬_Investigation_Hub.py       # Investigare avansată
│   ├── 3_📝_Ticket_Reviewer.py         # Review individual tickete
│   └── 4_📋_Raw_Data.py                # Vizualizare date brute
│
├── 📁 ticket_commenter_static/         # Frontend Ticket Reviewer
│   ├── app.js                          # JavaScript logic
│   ├── index.html                      # HTML interface
│   └── style.css                       # Styles
│
└── 📄 ticket_commenter_server.py       # Flask backend pentru Ticket Reviewer
```

---

## ✨ Features v3.1

### 📊 DASHBOARD (Executive Overview)

**Tab 1: Health Check**
- **Ticket Volume Trend:** Line + Bar charts cu grouping (Day/Week/Month)
- **Resolution Time:** Median + Average (business hours only: Mon-Fri, 9-18)
  - Trend calculation (previous vs current period)
  - Outlier filtering (> 30 days excluded)
- **Sentiment Distribution:** Donut chart (Pozitiv/Neutru/Negativ)
- **Urgency Breakdown:** Bar chart (Blocker/Mediu/Scăzut)
- **Summary Metrics:** Total, Blockers, Business Impact, Recurrent, Negative
- **Business Flow Impact:** Gauge chart cu praguri (30%/50%)
- **Recurring Issues:** 4 metrici detaliate
  - Total recurring issues + percentage
  - Recurring + Business Impact
  - Recurring Blockers
  - Recurring Bugs
- **Platform Distribution:** Pie/Treemap cu breakdown table
- **Critical Open Issues:** Tickete blocker care afectează business-ul

**Tab 2: Executive Summary**
- **KPIs:** Total Tickets, Critical Issues, Business Impact, 7-Day Trend
- **Top 5 Pain Points:** Cele mai frecvente probleme
- **Health Metrics:** Resolution Rate, Sentiment Score, Recurring %
- **Platform Overview:** Top 5 platforme cu procentaje
- **Ticket Volume Trend:** Ultimele 30 zile cu fill area

---

### 🔬 Investigation Hub (Deep Dive Analysis)

**Sidebar Filters (Global - apply to all tabs):**
1. 📅 **Date Range:** Date picker
2. 🏢 **Platform:** Multi-select dropdown
3. 📝 **Tip:** Multi-select dropdown
4. 📍 **Area:** Multi-select dropdown
5. 😊 **Sentiment:** Multi-select dropdown
6. 🚨 **Urgency:** Multi-select dropdown
7. 🐛 **Problem Type:** Multi-select dropdown
8. 💼 **Business Impact:** Radio (All/Yes/No)

**Tab 1: Data Explorer**
- Tabel interactiv cu toate ticketele filtrate
- Column visibility toggle (👁️ icon)
- Customizable column order
- Export CSV

**Tab 2: Visualizer**
- Sunburst chart hierarchic (Platform → Area)
- Interactive color-coded visualization

**Tab 3: Pain Point Analysis**
- Top 10 Pain Points (horizontal bar chart)
- Detailed pain points table

**Tab 4: Opportunity Finder**
- Top Problem Areas (bar chart)
- Problem Types distribution (pie chart)

---

### 📝 Ticket Reviewer (Individual Ticket Review)

**Features:**
- **Navigation:**
  - Keyboard shortcuts: `Ctrl + ←` (Previous), `Ctrl + →` (Next)
  - Previous/Next buttons
  - Jump to ticket # (input number + Go button)
- **Filters (Row 1 - 3 columns):**
  - Column 1: Ticket ID search
  - Column 2: Platform, Area, Tip (main categories)
  - Column 3: Sentiment, Urgency, Mailbox + Ticket counter
- **Filters (Row 2):**
  - Integration, Recurrent (True/False), Agent Needed (True/False)
  - Go to ticket #, Reset Filters button
- **Display:**
  - Subject + Ticket ID (#12345)
  - Summary
  - VEZI TICKET button (opens ticket URL)
  - Full conversation (CLIENT/AGENT format with timestamps)
  - Comments textarea (auto-save after 500ms)
  - Metadata (15 fields): tip, area, sentiment, urgency, etc.
- **Search in Area Filter:**
  - Area dropdown has search box
  - Type to filter large lists (78+ values)
  - Select All/Deselect All work on visible items only
- **Filter Caching:**
  - Server-side caching for better performance
  - API endpoint: `/api/filter-options`
  - localStorage validation for obsolete values

**Backend (Flask):**
- Auto-start când rulezi `streamlit run app.py`
- Port: 5000
- CORS enabled
- CSV field size limit: 10MB
- Routes:
  - `GET /` - Serve HTML
  - `GET /api/tickets` - Return all tickets
  - `GET /api/filter-options` - Return cached filter values
  - `POST /api/tickets/<index>/comment` - Save comment

---

### 📋 Raw Data (Data Table View)

- Vizualizare tabel cu toate ticketele
- Column configuration
- Export CSV

---

## 📊 Indicator Calculations

**Vezi documentația completă în:** `INDICATOR_CALCULATIONS.md`

### Exemple de Indicatori Explicați:

**💥 Business Flow Impact**
```
Formula: (business_impact_count / total_count) × 100
Coloane: affects_business_flow (Boolean)
Praguri: 0-30% (verde), 30-50% (galben), 50%+ (roșu)
```

**🔄 Recurring Issues**
```
Recurring Issues: count(is_recurrent = TRUE)
Percentage: (recurrent_count / total_count) × 100
Recurring + Business Impact: count(is_recurrent=TRUE AND affects_business_flow=TRUE)
Recurring Blockers: count(is_recurrent=TRUE AND urgency='blocker')
Recurring Bugs: count(is_recurrent=TRUE AND problem_type='bug')
```

**⏱️ Average Resolution Time**
```
Business Hours: Luni-Vineri, 09:00-18:00
Excludere: Tickete > 30 zile (270 ore business)
Calcul Trend: ((current_avg - previous_avg) / previous_avg) × 100
```

**📈 7-Day Trend**
```
Formula: ((last_7_days_count - prev_7_days_count) / prev_7_days_count) × 100
```

---

## 📊 CSV Data Format

### Coloane Obligatorii:
- `created_at` - Datetime (când a fost creat ticketul)
- `closed_at` - Datetime (când a fost închis)
- `platform` - Platformă (facturare, gestiune, api, spv, etc.)
- `area` - Arie funcțională

### Coloane Opționale (28 total):
- `ticket_url` - Link către ticket
- `mailbox_name` - Tip mailbox
- `customer_email_extracted` - Email client
- `gdrp_free_conversation` sau `formatted_conversation` - Conversație ticket
- `taxonomy` - Taxonomie ticket
- `tip` - Tip ticket (problema tehnica, feature request, etc.)
- `sentiment` - Sentiment (pozitiv, neutru, negativ)
- `apreciere_parere_support` - Rating support
- `urgency` - Urgență (blocker, mediu, scazut)
- `is_recurrent` - Boolean (TRUE/FALSE)
- `agent_intervention_needed` - Boolean
- `summary` - Rezumat ticket
- `user_goal` - Obiectivul utilizatorului
- `pain_point` - Descriere problemă principală
- `problem_type` - Tip problemă (feature_gap, bug, usability, etc.)
- `affects_business_flow` - Boolean
- `integration` - Nume integrare
- `mentioned_features` - Features menționate
- `specific_error_messages` - Mesaje de eroare
- `classification_index` - Index pentru clasificare
- `total_classifications` - Total clasificări
- `Comments` - Comentarii utilizator (adăugate prin Ticket Reviewer)

### Valori Valide:

| Coloană | Valori |
|---------|--------|
| **urgency** | blocker, mediu, scazut |
| **sentiment** | pozitiv, neutru, negativ |
| **platform** | facturare, gestiune, api, aplicatie mobil, spv, niciunul |
| **problem_type** | feature_gap, usability, documentation, bug, performance, integration |
| **tip** | problema tehnica, feature request, cerere administrativa/comerciala, intrebare contabila/fiscala |

⚠️ **Note:**
- Encoding suportat: UTF-8, Latin-1, CP1252
- CSV poate conține date "murdare" - aplicația le normalizează automat
- Fișierul `tickets.csv` este EXCLUS din git (.gitignore)

---

## 🛠️ Tech Stack

### Core Frameworks
| Library | Version | Utilizare |
|---------|---------|-----------|
| **Python** | 3.12 | Limbaj programare |
| **Streamlit** | 1.40+ | Dashboard framework |
| **Flask** | 3.1+ | Backend Ticket Reviewer |

### Data Processing
| Library | Version | Utilizare |
|---------|---------|-----------|
| **Pandas** | 2.2+ | Manipulare date |
| **NumPy** | 1.26+ | Operații numerice |

### Visualization
| Library | Version | Utilizare |
|---------|---------|-----------|
| **Plotly** | 5.24+ | Grafice interactive |
| **Matplotlib** | 3.9+ | Ploturi statice |
| **Seaborn** | 0.13+ | Vizualizări statistice |

### Export & Reporting
| Library | Version | Utilizare |
|---------|---------|-----------|
| **OpenPyXL** | 3.1+ | Operații Excel |
| **XlsxWriter** | 3.2+ | Formatare Excel |
| **ReportLab** | 4.2+ | Generare PDF |
| **FPDF2** | 2.8+ | Creare PDF |

### Additional Libraries
| Library | Version | Utilizare |
|---------|---------|-----------|
| **Flask-CORS** | - | Cross-origin requests |
| **python-dotenv** | 1.0+ | Variabile environment |
| **chardet** | 5.2+ | Detecție encoding |
| **streamlit-extras** | 0.4+ | Componente Streamlit extinse |

---

## 🎨 Cum se Folosește

### 1. Încărcare Date

**Opțiune 1: Auto-load (Recomandat)**
```bash
# Pune fișierul tickets.csv în root folder
cp /path/to/tickets.csv ./tickets.csv

# Rulează aplicația (CSV se încarcă automat)
streamlit run app.py
```

**Opțiune 2: Manual din interfață**
1. Deschide http://localhost:8501
2. Click "📂 Folosește tickets.csv local"

---

### 2. Navigare Dashboard

**Sidebar Navigation:**
- **📊 DASHBOARD** - Overview executiv + Health Check
- **🔬 Investigation Hub** - Analiză avansată cu filtre
- **📝 Ticket Reviewer** - Review individual (deschide în tab nou)
- **📋 Raw Data** - Tabel date brute

**Global Date Filter:**
- Top pagină: Date Range picker
- Afectează toate vizualizările din pagina curentă

---

### 3. Folosire Investigation Hub

1. **Selectează filtre din sidebar:**
   - Date Range, Platform, Tip, Area, Sentiment, Urgency, Problem Type
2. **Navighează între tab-uri:**
   - Data Explorer, Visualizer, Pain Point Analysis, Opportunity Finder
3. **Export rezultate:**
   - Click "📥 Export Filtered Data (CSV)"

---

### 4. Folosire Ticket Reviewer

**Acces:**
- Din sidebar: Click "📝 Ticket Reviewer" (deschide http://localhost:5000)
- Sau direct: http://localhost:5000

**Navigare:**
- **Keyboard:** `Ctrl + ←` (anterior), `Ctrl + →` (următor)
- **Mouse:** Click Previous/Next buttons
- **Jump:** Introdu # ticket → Click "Go"

**Filtrare:**
- **Row 1:** Ticket ID search, Platform/Area/Tip, Sentiment/Urgency/Mailbox
- **Row 2:** Integration, Recurrent, Agent Needed, Jump to ticket
- **Area Filter:** Are search box pentru filtrare rapidă (78+ valori)

**Comentarii:**
- Scrie în textarea
- Auto-save după 500ms
- Se salvează în coloana "Comments" din CSV
- Status: "Saving..." → "Saved ✓"

---

## 🐛 Troubleshooting

### ❌ Aplicația nu pornește

**Problema: Port 8501 ocupat**
```bash
# Verifică ce proces folosește portul
# Windows
netstat -ano | findstr :8501

# Linux/Mac
lsof -i :8501

# Rulează pe alt port
streamlit run app.py --server.port 8502
```

**Problema: Port 5000 ocupat (Ticket Reviewer)**
```bash
# Modifică portul în ticket_commenter_server.py
# Linia 486: app.run(debug=True, port=5001)  # Schimbă 5000 → 5001
```

---

### ❌ Erori la import module

**Problema: ModuleNotFoundError**
```bash
# Verifică virtual environment activat
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Reinstalează toate dependențele
uv pip install -r requirements.txt --force-reinstall
```

**Problema: Protobuf errors**
```bash
uv pip install --upgrade streamlit protobuf
```

---

### ❌ CSV nu se încarcă

**Problema: Encoding greșit**
```python
# Aplicația suportă: UTF-8, Latin-1, CP1252
# Dacă primești eroare, convertește CSV la UTF-8
```

**Problema: Coloane lipsă**
```
Verifică că CSV-ul conține minim:
- created_at (datetime)
- closed_at (datetime)
- platform (text)
- area (text)
```

**Problema: Fișier prea mare**
```bash
# Flask CSV field size limit: 10MB
# Pentru fișiere > 10MB, editează ticket_commenter_server.py
# Linia 18: csv.field_size_limit(20 * 1024 * 1024)  # 20MB
```

---

### ❌ Filtre nu funcționează

**Problema: LocalStorage outdated**
```javascript
// Deschide Developer Console (F12)
// Rulează:
localStorage.clear()
location.reload()
```

**Problema: Valori filtru nu se afișează**
```
Verifică:
1. CSV conține date în coloana respectivă
2. Valorile nu sunt toate goale ('-' sau '')
3. Encoding-ul este corect (UTF-8)
```

---

## 📚 Documentație Suplimentară

| Document | Descriere |
|----------|-----------|
| **INDICATOR_CALCULATIONS.md** | Explicații detaliate pentru calculul tuturor indicatorilor |
| **.claude/CLAUDE.md** | Documentație tehnică completă pentru dezvoltatori |
| **requirements.txt** | Lista dependențelor Python |
| **.streamlit/config.toml** | Configurare Streamlit (theme, port, etc.) |

---

## 🔄 Version History

### v3.1 (Current - 2025-10-09)
- ✅ Removed Team Performance and Export Reports pages
- ✅ Simplified to 3 core pages (Dashboard, Investigation Hub, Ticket Reviewer)
- ✅ Flask server auto-starts with Streamlit (single command)
- ✅ Added search functionality to Area filter (dropdown)
- ✅ Reorganized Investigation Hub filters (Platform, Tip, Area, Sentiment, Urgency, Problem Type)
- ✅ Removed Statistical Analysis tab from Investigation Hub
- ✅ Added comprehensive INDICATOR_CALCULATIONS.md documentation
- ✅ Updated README with complete feature list

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

## 🤝 Contributing

Pentru issues, bug reports, sau feature requests, consultă echipa de dezvoltare.

---

## 📄 License

Proprietary - SmartBill Internal Use Only

---

## 💡 Tips & Best Practices

### Pentru Performanță Optimă:
1. **Folosește filtre Date Range** înainte de a selecta alte filtre
2. **Limitează selecțiile multi-select** la maxim 5-10 valori
3. **Închide tab-urile nefolosite** pentru a economisi memorie
4. **Exportă date filtrate** în loc să procesezi totul în Excel

### Pentru Analiză Eficientă:
1. **Start cu Executive Summary** pentru overview rapid
2. **Folosește Investigation Hub** pentru deep-dive în probleme specifice
3. **Ticket Reviewer** pentru review individual și comentarii
4. **Consultă INDICATOR_CALCULATIONS.md** pentru înțelegerea metricilor

---

## 🙏 Acknowledgments

**Developed with ❤️ using:**
- [Claude Code](https://claude.com/claude-code) - AI-assisted development
- [Streamlit](https://streamlit.io/) - Dashboard framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

---

**Last Updated:** 2025-10-09
**Maintained By:** Development Team
**Repository:** https://github.com/lightsongjs/sumarDashboard
