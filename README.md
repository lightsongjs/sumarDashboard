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
uv pip install streamlit pandas plotly openpyxl xlsxwriter chardet
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
└── 📁 pages/                   # Pagini aplicație
    ├── 1_📊_Dashboard.py       # KPIs + vizualizări
    ├── 2_🔥_Pain_Points.py     # Analiza probleme
    ├── 3_📈_Analytics.py       # Analytics avansate
    ├── 4_👥_Team.py            # Performance echipă
    └── 5_📤_Reports.py         # Generare rapoarte
```

---

## ✨ Features

### 📊 Dashboard Principal
- 4 KPIs cu delta vs perioadă anterioară
- 6+ grafice interactive (Plotly)
- Filtrare avansată în sidebar
- Quick filters (Blockers, Recurente, etc.)

### 🔥 Pain Points Analysis
- Top 10 probleme frecvente
- Word frequency analysis
- Matrix Arii × Tipuri probleme
- Tree view expandabil
- Export dedicat

### 📈 Analytics Avansate
- Pareto analysis (80/20)
- Forecast linear 7-14 zile
- Period comparison
- AI insights automate
- Statistical summaries

### 👥 Team Performance
- Leaderboard agenți
- Metrici de performanță
- Comparație între agenți
- Activity timeline

### 📤 Reports & Export
- Export CSV/Excel
- Raport Excel complet (multiple sheets)
- Rapoarte personalizate
- Quick exports (Blockers, Negative, etc.)

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

- **Python** 3.12
- **Streamlit** 1.50
- **Pandas** 2.3.3
- **Plotly** 6.3.1
- **OpenPyXL** 3.1.5

---

## 📝 Utilizare

1. **Homepage:** Click "📂 Folosește tickets.csv local"
2. **Navigare:** Sidebar → selectează pagina
3. **Filtrare:** Sidebar → aplică filtre
4. **Export:** Reports → alege format

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
