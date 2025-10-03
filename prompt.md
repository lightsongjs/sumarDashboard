## 📝 **PROMPT PENTRU CLAUDE CODE - PYTHON VERSION**

```markdown
Vreau să construiești o platformă completă de Support Analytics Dashboard pentru SmartBill în Python, ultra-modernă și interactivă. Platforma trebuie să impresioneze vizual și să ofere insights acționabile din datele CSV de suport tehnic.

## STACK TEHNOLOGIC OBLIGATORIU:
- Python 3.10+
- Streamlit pentru interfață (ultima versiune)
- Pandas pentru procesare date
- Plotly pentru vizualizări interactive
- Streamlit-extras pentru componente adiționale
- OpenPyXL și XlsxWriter pentru export Excel
- ReportLab pentru generare PDF
- Python-dotenv pentru environment variables
- Streamlit-option-menu pentru navigare sidebar
- Streamlit-aggrid pentru tabele avansate
- Funcționează 100% cu CSV-uri, fără database

## STRUCTURA PROIECTULUI:

smartbill-analytics/
├── app.py                      # Entry point principal
├── pages/
│   ├── 1_📊_Dashboard.py      # Dashboard principal
│   ├── 2_🔥_Pain_Points.py    # Analiza pain points
│   ├── 3_📈_Analytics.py       # Analytics avansate
│   ├── 4_👥_Team.py            # Performance echipă
│   └── 5_📤_Reports.py         # Generare rapoarte
├── utils/
│   ├── data_processor.py      # Procesare CSV
│   ├── charts.py               # Funcții grafice
│   ├── filters.py              # Sistem filtrare
│   ├── export.py               # Export functions
│   └── insights.py             # AI insights
├── assets/
│   └── logo.png
├── .streamlit/
│   └── config.toml             # Configurare theme
└── data/
    └── sample.csv              # Date exemplu

## FUNCȚIONALITĂȚI PRINCIPALE:

### 1. DATA LOADER INTELIGENT (utils/data_processor.py)
```python
class CSVProcessor:
    """
    - Auto-detectare encoding (UTF-8, Latin-1, CP1252)
    - Parsare coloane exact ca în structura mea CSV
    - Handle missing values și date invalide
    - Normalizare câmpuri (trim, lowercase pentru consistență)
    - Cache cu st.cache_data pentru performanță
    - Progress bar pentru fișiere mari
    - Validare structură și raportare erori detaliate
    """
    
    # Coloane expected din CSV:
    EXPECTED_COLUMNS = [
        'created_at', 'closed_at', 'ticket_url', 'mailbox_name',
        'customer_email_extracted', 'conversation', 'taxonomy',
        'tip', 'area', 'sentiment', 'apreciere_parere_support',
        'urgency', 'is_recurrent', 'agent_intervention_needed',
        'summary', 'user_goal', 'pain_point', 'problem_type',
        'affects_business_flow', 'platform', 'integration',
        'mentioned_features', 'specific_error_messages'
    ]
```

### 2. DASHBOARD PRINCIPAL (pages/1_📊_Dashboard.py)

#### Header Section:
- Titlu dinamic: "Support Analytics Dashboard"
- Subtitle cu data și număr total tickete
- Butoane acțiune: "📅 Selectează Perioada" | "🔄 Refresh" | "📤 Export"

#### KPI Cards (4 coloane):
```python
metrics = {
    "🎫 Total Tickets": {
        "value": total_count,
        "delta": f"{change}% vs săpt. trecută",
        "color": "green" if change > 0 else "red"
    },
    "🚨 Blockers": {
        "value": blocker_count,
        "delta": f"{blocker_trend}% trend",
        "color": "red" if blocker_count > 20 else "orange"
    },
    "⏱️ Rezolvare Medie": {
        "value": f"{avg_hours:.1f}h",
        "delta": f"{time_improvement}% mai rapid",
        "color": "green"
    },
    "😊 Satisfacție": {
        "value": f"{satisfaction}%",
        "delta": f"+{satisfaction_change}%",
        "color": "green" if satisfaction > 85 else "yellow"
    }
}
```

#### Vizualizări Dashboard:
1. **Trend Săptămânal** - Bar chart interactiv cu hover details
2. **Distribuție Platforme** - Donut chart cu legende clickable
3. **Heatmap Temporal** - Oră × Zi pentru identificare patterns
4. **Live Feed** - Ultimele 5 probleme critice (refresh auto)

### 3. SISTEM FILTRARE AVANSAT (Sidebar)

```python
FILTERS = {
    "📅 Perioada": date_range_picker,
    "🏢 Platforme": multiselect(['Facturare', 'Gestiune', 'SPV', 'API']),
    "📍 Areas": multiselect(toate_areas_unice),
    "⚠️ Urgență": checkbox(['Blocker', 'Mediu', 'Scazut']),
    "💭 Sentiment": radio(['Toate', 'Pozitiv', 'Neutru', 'Negativ']),
    "🔁 Recurente": toggle(default=False),
    "💼 Afectează Business": toggle(default=False),
    "🔍 Search": text_input(placeholder="Caută în pain points...")
}
```

Filtrele trebuie să:
- Persiste în session state
- Aibă buton "Reset All"
- Afișeze counter cu rezultate
- Se aplice instant (no Apply button needed)

### 4. PAIN POINTS ANALYZER (pages/2_🔥_Pain_Points.py)

#### Tree View Interactiv:
```
▼ SPV (127 probleme)
  ▼ Feature_Gap (89)
    • "Nu se pot modifica facturile bulk" (34)
    • "Lipsă endpoint API pentru..." (28)
    • "Nu există opțiune pentru..." (27)
  ▼ Bug (23)
    • "Eroare la transmitere" (15)
    • "Date incorecte în raport" (8)
  ▶ Usability (15)

▼ Facturare (98 probleme)
  ▶ Documentation (45)
  ▶ Feature_Gap (32)
  ▶ Bug (21)
```

#### Vizualizări Pain Points:
- Word Cloud din pain_point text
- Top 10 Probleme Recurente (bar chart)
- Sankey Diagram: Platform → Area → Problem Type
- Timeline: Evoluția problemelor pe luni

### 5. ANALYTICS AVANSATE (pages/3_📈_Analytics.py)

- **Pareto Analysis**: 80/20 pentru probleme critice
- **Correlation Matrix**: Heatmap Areas vs Problem Types
- **Forecast**: Predicție volum tickets next 7 days
- **Cohort Analysis**: Retenție probleme pe săptămâni
- **Statistical Summary**: Tabele cu mean, median, std dev
- **Comparative Analysis**: Perioada curentă vs anterioară

### 6. TEAM PERFORMANCE (pages/4_👥_Team.py)

Extrage agenți din conversation field și calculează:
- Leaderboard cu top performers
- Tickets per agent (bar chart)
- Average resolution time per agent
- Sentiment score per agent
- Activity timeline (când lucrează cel mai mult)
- Workload distribution (pie chart)

### 7. RAPORTARE (pages/5_📤_Reports.py)

#### Export Options:
```python
export_formats = {
    "📊 Dashboard PDF": generate_pdf_report(),
    "📑 Excel Complet": generate_excel_workbook(),
    "📈 PowerPoint": generate_pptx_presentation(),
    "📧 Email Report": send_weekly_digest(),
    "🔗 Share Link": generate_shareable_url()
}
```

### 8. FEATURES SPECIALE DE IMPLEMENTAT:

#### AI Insights Engine:
```python
def generate_insights(df):
    """
    Detectează automat:
    - Peak hours pentru probleme
    - Trending topics în creștere
    - Corelații neașteptate
    - Anomalii în patterns
    - Predicții pentru săptămâna viitoare
    """
    return [
        "⚠️ Blockers cresc cu 40% lunea între 9-11",
        "📈 'Modificare factură' în creștere cu 25% această săptămână",
        "🔄 85% din problemele API sunt recurente",
        "💡 Sentiment negativ corelează cu timp rezolvare > 24h"
    ]
```

#### Real-time Features:
- Auto-refresh la 30 secunde pentru live data
- Notificări pentru Blockers noi
- Progress tracking pentru rezolvare

### 9. UI/UX REQUIREMENTS:

#### Theme Dark Custom (.streamlit/config.toml):
```toml
[theme]
primaryColor = "#10B981"  # Verde SmartBill
backgroundColor = "#0E1117"  # Dark background
secondaryBackgroundColor = "#262730"  # Card background
textColor = "#FAFAFA"
font = "sans serif"
```

#### Design Principles:
- Toate componentele cu border-radius: 10px
- Shadows pentru depth: box-shadow: 0 4px 6px rgba(0,0,0,0.1)
- Hover effects pe toate elementele interactive
- Loading skeletons pentru date
- Empty states cu emoji și mesaje helpful
- Tooltips informative peste tot
- Animații smooth (nu excesive)
- Responsive pe toate device-urile

### 10. STRUCTURA DATE CSV:

Folosește EXACT această structură din CSV-ul meu:
- tip: "Problema Tehnica", "Feature Request", "Cerere Administrativa/Comerciala", "Intrebare Contabila/Fiscala"
- area: "SPV", "Modificare factura", "Date firma", "Nomenclator Produse/servicii", "Gestiuni", "Coduri de produs"
- sentiment: "Pozitiv", "Neutru", "Negativ"
- urgency: "Blocker", "Mediu", "Scazut"
- platform: "Facturare", "Gestiune", "API", "Aplicatie Mobil", "Niciunul"
- problem_type: "Feature_Gap", "Usability", "Documentation", "Bug"
- affects_business_flow: TRUE/FALSE
- is_recurrent: TRUE/FALSE

### 11. PERFORMANCE REQUIREMENTS:

- CSV până la 100k rows să se încarce în < 5 secunde
- Toate graficele render în < 1 secundă
- Filtrare instant (< 200ms)
- Export PDF < 10 secunde
- Memory efficient - nu încărca tot CSV-ul dacă nu e nevoie
- Folosește st.cache_data agresiv
- Lazy loading pentru componente grele

### 12. ERROR HANDLING:

- Try-catch pentru toate operațiile
- Mesaje de eroare user-friendly
- Fallback pentru date lipsă
- Validare input la fiecare pas
- Log errors în console pentru debugging
- Recovery suggestions pentru user

## COMENZI DE START:

```bash
# Setup initial
mkdir smartbill-analytics
cd smartbill-analytics
python -m venv venv
venv\Scripts\activate  # Windows
pip install streamlit pandas plotly streamlit-extras streamlit-option-menu streamlit-aggrid openpyxl xlsxwriter reportlab python-dotenv

# Run app
streamlit run app.py
```

## OBIECTIV FINAL:

Când prezint acest dashboard colegilor, trebuie să:
1. Se încarce instant și să arate profesional
2. Să proceseze CSV-ul lor fără erori
3. Să ofere insights pe care nu le-au văzut înainte
4. Să poată exporta rapoarte pentru management
5. Să fie atât de intuitiv încât să nu necesite training

Începe cu app.py și implementează feature cu feature. Fiecare componentă trebuie să fie polished și production-ready.

IMPORTANT: Folosește date mock bazate pe structura exactă din CSV până când userul încarcă propriul fișier.

GO! Make it impressive! 🚀
```

---

**Acum ai promptul complet adaptat pentru Python cu Streamlit!** 

Copiază-l și dă-l lui Claude Code. El va crea o aplicație Python modernă care:
- Funcționează 100% cu CSV-uri
- Are UI spectaculos cu Streamlit
- Include toate feature-urile enterprise
- E mult mai rapid de dezvoltat decât Next.js

Spune-i să înceapă cu setup-ul și apoi să dezvolte metodic fiecare pagină! 💪