# 📊 SmartBill Support Analytics Dashboard

Dashboard interactiv pentru analiza ticket-urilor de suport SmartBill.

![Status](https://img.shields.io/badge/status-functional-success)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.50-red)

---

## 🚀 Quick Start

### 1. Instalare

```bash
# Instalează uv (dacă nu e deja instalat)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Creează virtual environment
uv venv

# Instalează dependențe
uv pip install -r requirements.txt
 uv pip install -r requirements.txt --force-reinstall
```

### 2. Rulare

```bash
# Activează environment
source .venv/bin/activate  # Linux/Mac
# sau
.venv\Scripts\activate     # Windows

# Pornește aplicația
streamlit run app.py
```

### 3. Accesare

Deschide browser la: **http://localhost:8501**

---

## 📁 Structură

```
📦 sumarDashboard/
├── 📄 app.py                    # Entry point
├── 📄 requirements.txt          # Dependențe
├── 📄 tickets.csv              # Date (4.9MB)
├── 📁 .streamlit/
│   └── config.toml             # Configurare
├── 📁 utils/                   # Module utilitare
│   ├── data_processor.py       # Procesare CSV
│   ├── charts.py               # Grafice Plotly
│   ├── filters.py              # Filtre sidebar
│   └── export.py               # Export rapoarte
├── 📁 pages/                   # Pagini aplicație (v3.0)
│   ├── 1_📊_Strategic_Dashboard.py  # Dashboard principal cu KPIs
│   ├── 2_🔬_Investigation_Hub.py    # Analiza probleme + insights
│   ├── 3_👥_Team_Performance.py     # Performance echipă
│   ├── 4_📤_Export_Reports.py       # Generare rapoarte
│   └── 5_📝_Ticket_Reviewer.py      # Review individual tickets
├── 📁 ticket_commenter_static/      # Flask app pentru ticket reviewer
│   ├── app.js                       # Frontend logic
│   ├── index.html                   # Ticket reviewer UI
│   └── style.css                    # Styles
└── 📄 ticket_commenter_server.py    # Flask backend server
```

---

## ✨ Features (v3.0)

### 📊 Strategic Dashboard
- Consolidated KPIs with delta metrics
- Interactive Plotly visualizations
- Advanced sidebar filtering
- Quick filters (Blockers, Recurrent, etc.)
- Pain points matrix and word cloud
- Timeline analysis

### 🔬 Investigation Hub
- Top pain points analysis
- Word frequency analysis
- Drill-down capabilities
- Pattern detection
- Export insights

### 👥 Team Performance
- Agent leaderboard
- Performance metrics
- Agent comparison
- Activity timeline

### 📤 Export Reports
- Multi-format export (CSV, Excel, PDF, PowerPoint)
- Customizable reports
- Quick export templates
- Automated report generation

### 📝 Ticket Reviewer (NEW!)
- Browse tickets one-by-one with keyboard navigation
- Multi-filter support (mailbox, area, sentiment, urgency, platform, etc.)
- Inline comments with auto-save
- Full conversation view (agent + client)
- Jump to specific ticket number
- Opens in separate tab for focused review

---

## 🎨 Filtre Disponibile

- 📅 **Perioadă:** Date picker + quick buttons (7/30/90 zile)
- 🏢 **Platforme:** Multiselect (Facturare, Gestiune, SPV, API, etc.)
- 📍 **Arii:** Multiselect (toate valorile din CSV)
- ⚠️ **Urgență:** Checkbox (Blocker, Mediu, Scazut)
- 💭 **Sentiment:** Radio (Toate, Pozitiv, Neutru, Negativ)
- 🔁 **Recurente:** Toggle
- 💼 **Impact Business:** Toggle
- 🔍 **Search:** Text în pain points

---

## 📊 CSV Format

### Coloane Obligatorii:
- `created_at` - Data (datetime)
- `platform` - Platformă
- `area` - Arie

### Coloane Opționale (26 total):
Vezi `.claude/claude.md` pentru lista completă.

### Valori Acceptate:
**urgency:** blocker, mediu, scazut
**sentiment:** pozitiv, neutru, negativ
**platform:** facturare, gestiune, api, spv, pos, conta, etc.

⚠️ **Note:** CSV-ul poate conține date "murdare" - aplicația le normalizează automat.

---

## 🛠️ Tech Stack

### Core Framework
- **Python** 3.12
- **Streamlit** 1.40+ (Dashboard framework)
- **Flask** 3.1+ (Ticket Reviewer backend)

### Data & Visualization
- **Pandas** 2.2+
- **Plotly** 5.24+
- **Matplotlib** 3.9+
- **Seaborn** 0.13+

### Export & Reporting
- **OpenPyXL** 3.1+
- **XlsxWriter** 3.2+
- **ReportLab** 4.2+
- **FPDF2** 2.8+

### Additional
- **Flask-CORS** (for Ticket Reviewer API)
- **python-dotenv** 1.0+
- **chardet** 5.2+ (encoding detection)

---

## 📝 Utilizare

### Dashboard Principal

1. **Homepage:** Click "📂 Folosește tickets.csv local"
2. **Navigare:** Sidebar → selectează pagina
3. **Filtrare:** Sidebar → aplică filtre
4. **Export:** Reports → alege format

### Ticket Reviewer

1. **Start Flask server:**
   ```bash
   cd sumarDashboard
   python ticket_commenter_server.py
   ```

2. **Access from dashboard:** Click "📝 Ticket Reviewer" in sidebar (opens in new tab)

3. **Or direct access:** http://localhost:5000

4. **Navigation:**
   - Use **Ctrl + ←/→** for keyboard navigation
   - Click Previous/Next buttons
   - Jump to specific ticket number
   - Apply filters in header

5. **Comments:**
   - Type in comments textarea
   - Auto-saves after 500ms
   - Persists to CSV "Comments" column

---

## 🐛 Troubleshooting

### Aplicația nu pornește?
```bash
# Verifică dacă portul 8501 e liber
lsof -i :8501

# Sau specifică alt port
streamlit run app.py --server.port 8502
```

### Erori la import?
```bash
# Reinstalează pachete
uv pip install --force-reinstall streamlit pandas plotly
```

### CSV nu se încarcă?
- Verifică encoding-ul (UTF-8, Latin-1 suportate)
- Verifică dacă are coloanele obligatorii
- Vezi mesajele de eroare în app

---

## 📚 Documentație

- **Full docs:** `.claude/claude.md`
- **TODO list:** `TODOS.md`
- **Prompt original:** `prompt.md`

---

## 🤝 Support

Pentru issues și features noi, consultă echipa de dezvoltare.

**Developed with ❤️ using Claude Code**
