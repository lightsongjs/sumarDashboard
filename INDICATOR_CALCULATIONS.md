# 📊 Dashboard Indicators - Calculation Documentation

**Version:** 1.0
**Last Updated:** 2025-10-09
**Application:** SmartBill Support Analytics Dashboard

---

## Table of Contents

1. [Business Flow Impact](#1-business-flow-impact)
2. [Recurring Issues](#2-recurring-issues)
3. [Average Time to Resolution](#3-average-time-to-resolution)
4. [Key Performance Indicators](#4-key-performance-indicators)
5. [Health Metrics](#5-health-metrics)
6. [Critical Open Issues](#6-critical-open-issues)
7. [Sentiment Analysis](#7-sentiment-analysis)
8. [Platform Distribution](#8-platform-distribution)
9. [FAQ](#9-faq)

---

## 1. Business Flow Impact

### 💥 Description
Măsoară procentul de tickete care afectează fluxurile de business ale clienților.

### 📋 Formula de Calcul

```python
# Cod sursa: pages/1_📊_DASHBOARD.py, liniile 559-562
business_impact_count = len(df[df['affects_business_flow'] == True])
total_count = len(df)
business_impact_pct = (business_impact_count / total_count * 100) if total_count > 0 else 0
```

### 📊 Praguri de Alarmă

| Nivel | Procent | Culoare | Descriere |
|-------|---------|---------|-----------|
| **Moderate** | 0% - 30% | 🟢 Verde | Nivel normal de impact business |
| **Significant** | 30% - 50% | 🟡 Galben | Atenție - impact crescut |
| **Critical** | 50%+ | 🔴 Roșu | Urgent - impact critic |

**Cod sursa:**
```python
# Liniile 567-572
threshold_red = 50    # Roșu dacă >= 50%
threshold_yellow = 30 # Galben dacă >= 30%
```

### 🗂️ Coloane Necesare
- `affects_business_flow` (Boolean: TRUE/FALSE)

### 💡 Exemple Practice

**Exemplu 1: Impact Moderat**
- Total tickete: 1000
- Tickete cu impact business: 200
- Calcul: `(200 / 1000) * 100 = 20%`
- Rezultat: **20%** - nivel moderat (verde)

**Exemplu 2: Impact Critic**
- Total tickete: 500
- Tickete cu impact business: 280
- Calcul: `(280 / 500) * 100 = 56%`
- Rezultat: **56%** - nivel critic (roșu)

---

## 2. Recurring Issues

### 🔄 Description
Analiza problemelor recurente și impactul lor asupra business-ului.

### 📋 Indicatori și Formule

#### 2.1 Recurring Issues (număr total)

**Cod sursa:** liniile 597
```python
recurrent_count = len(df[df['is_recurrent'] == True])
```

**Exemplu:**
- Tickete cu `is_recurrent = TRUE`: **69**
- Rezultat: **69** tickete recurente

---

#### 2.2 Percentage of Total (%)

**Cod sursa:** liniile 598-599
```python
total_count = len(df)
recurrent_pct = (recurrent_count / total_count * 100) if total_count > 0 else 0
```

**Formula:**
```
Recurrent % = (Tickete Recurente / Total Tickete) × 100
```

**Exemplu:**
- Tickete recurente: 69
- Total tickete: 1813
- Calcul: `(69 / 1813) * 100 = 3.8%`
- Rezultat: **3.8% of total**

**Interpretare:**
- < 10% = ✅ Eficiență bună
- 10-20% = ℹ️ Analiza recomandată
- \> 20% = ⚠️ Atenție - necesită îmbunătățiri

---

#### 2.3 Recurring + Business Impact

**Cod sursa:** liniile 612-614
```python
recurrent_business = len(df[
    (df['is_recurrent'] == True) &
    (df['affects_business_flow'] == True)
])
```

**Condiții:**
- `is_recurrent = TRUE` **ȘI**
- `affects_business_flow = TRUE`

**Exemplu:**
- Tickete recurente: 69
- Dintre acestea, cu impact business: **41**
- Rezultat: **41** tickete recurente care afectează business-ul

**Semnificație:**
Acestea sunt cele mai critice - probleme care se repetă ȘI afectează operațiunile clienților.

---

#### 2.4 Recurring Blockers

**Cod sursa:** liniile 617-619
```python
recurrent_blockers = len(df[
    (df['is_recurrent'] == True) &
    (df['urgency'].str.lower() == 'blocker')
])
```

**Condiții:**
- `is_recurrent = TRUE` **ȘI**
- `urgency = 'blocker'`

**Exemplu:**
- Tickete recurente: 69
- Dintre acestea, cu urgență blocker: **37**
- Rezultat: **37** blockeri recurenți

**Semnificație:**
Probleme critice care blochează utilizatorii și se repetă - prioritate maximă pentru rezolvare permanentă.

---

#### 2.5 Recurring Bugs

**Cod sursa:** liniile 622-624
```python
recurrent_bugs = len(df[
    (df['is_recurrent'] == True) &
    (df['problem_type'].str.lower() == 'bug')
])
```

**Condiții:**
- `is_recurrent = TRUE` **ȘI**
- `problem_type = 'bug'`

**Exemplu:**
- Tickete recurente: 69
- Dintre acestea, bug-uri: **29**
- Rezultat: **29** bug-uri recurente

**Semnificație:**
Bug-uri care nu au fost rezolvate definitiv și reapar - necesită fix permanent.

---

### 🗂️ Coloane Necesare
- `is_recurrent` (Boolean: TRUE/FALSE)
- `affects_business_flow` (Boolean: TRUE/FALSE)
- `urgency` (Text: blocker/mediu/scazut)
- `problem_type` (Text: bug/feature_gap/usability/documentation/performance/integration)

---

## 3. Average Time to Resolution

### ⏱️ Description
Timpul mediu de rezolvare a ticketelor, calculat DOAR în ore de business.

### 📋 Calcul Ore Business

**Cod sursa:** liniile 91-139 (funcția `calculate_business_hours`)

**Ore de lucru:**
- **Zile:** Luni - Vineri (Monday=0 to Friday=4)
- **Interval orar:** 09:00 - 18:00
- **Ore pe zi:** 9 ore
- **Weekend:** EXCLUS (Saturday=5, Sunday=6)

**Algoritm:**
1. Pentru fiecare ticket închis, se calculează timpul între `created_at` și `closed_at`
2. Se numără DOAR orele în intervalul Luni-Vineri, 9:00-18:00
3. Weekend-urile și orele din afara programului (18:00-09:00) sunt EXCLUSE

**Exemplu:**
- Ticket creat: Vineri 17:00
- Ticket închis: Luni 11:00
- Calcul:
  - Vineri 17:00-18:00 = **1 oră**
  - Sâmbătă, Duminică = **0 ore** (weekend)
  - Luni 09:00-11:00 = **2 ore**
  - **Total: 3 ore business**

---

### 📊 Filtrare Outlier-i

**Cod sursa:** liniile 155-159
```python
max_hours = 30 * 9  # 30 zile * 9 ore/zi = 270 ore
tickets_excluded = len(closed_tickets[closed_tickets['resolution_hours'] > max_hours])
closed_tickets = closed_tickets[closed_tickets['resolution_hours'] <= max_hours]
```

**Regula:**
- Ticketele cu timpul de rezolvare **> 30 zile** (270 ore business) sunt EXCLUSE din calcul
- Aceste tickete sunt contorizate separat în `excluded_count`

---

### 📈 Indicatori Calculați

#### 3.1 Median Resolution Time

**Cod sursa:** linia 165
```python
median_hours = closed_tickets['resolution_hours'].median()
```

**Format display:**
```python
# Liniile 180-189
med_days = int(median_hours // 24)
med_hours_remainder = int(median_hours % 24)
med_minutes = int((median_hours * 60) % 60)

if med_days > 0:
    median_readable = f"{med_days}d {med_hours_remainder}h {med_minutes}m"
elif med_hours_remainder > 0:
    median_readable = f"{med_hours_remainder}h {med_minutes}m"
else:
    median_readable = f"{med_minutes}m"
```

**Exemplu:**
- Median: 15.5 ore
- Display: **15h 30m**

---

#### 3.2 Average Resolution Time

**Cod sursa:** linia 164
```python
avg_hours = closed_tickets['resolution_hours'].mean()
```

**Exemplu:**
- Average: 18 ore
- Display: **18h 0m**

---

#### 3.3 Trend (% change from previous period)

**Cod sursa:** liniile 192-201
```python
# Se împarte dataset-ul în 2 perioade egale
mid_date = closed_tickets['created_at'].min() + (closed_tickets['created_at'].max() - closed_tickets['created_at'].min()) / 2

previous_period = closed_tickets[closed_tickets['created_at'] < mid_date]
current_period = closed_tickets[closed_tickets['created_at'] >= mid_date]

prev_avg = previous_period['resolution_hours'].mean()
curr_avg = current_period['resolution_hours'].mean()

change_pct = ((curr_avg - prev_avg) / prev_avg) * 100
```

**Formula:**
```
Trend % = ((Average Curent - Average Anterior) / Average Anterior) × 100
```

**Exemplu:**
- Perioada anterioară: average 20 ore
- Perioada curentă: average 16 ore
- Calcul: `((16 - 20) / 20) * 100 = -20%`
- Rezultat: **-20%** (îmbunătățire cu 20%)

**Interpretare:**
- Negativ (-) = ✅ Îmbunătățire (rezolvare mai rapidă)
- Pozitiv (+) = ⚠️ Degradare (rezolvare mai lentă)

---

### 🗂️ Coloane Necesare
- `created_at` (Datetime)
- `closed_at` (Datetime)

---

## 4. Key Performance Indicators

### 📊 Total Tickets

**Cod sursa:** linia 762
```python
total_tickets = len(df)
```

**Descriere:** Numărul total de tickete din perioada selectată.

---

### 🔴 Critical Issues

**Cod sursa:** liniile 765-766
```python
critical_issues = len(df[
    (df['urgency'].str.lower() == 'blocker') &
    (df['affects_business_flow'] == True)
])
```

**Condiții:**
- `urgency = 'blocker'` **ȘI**
- `affects_business_flow = TRUE`

**Descriere:** Tickete care sunt ATÂT blockeri CÂT ȘI afectează business-ul - cele mai critice probleme.

---

### 💼 Business Impact

**Cod sursa:** liniile 770-771
```python
business_impact_issues = len(df[df['affects_business_flow'] == True])
```

**Descriere:** Total tickete care afectează fluxurile de business ale clienților.

---

### 📈 Trend (7d)

**Cod sursa:** liniile 776-783
```python
max_date = df['created_at'].max()
last_7_days = df[df['created_at'] >= (max_date - pd.Timedelta(days=7))]
prev_7_days = df[
    (df['created_at'] >= (max_date - pd.Timedelta(days=14))) &
    (df['created_at'] < (max_date - pd.Timedelta(days=7)))
]

trend_pct = ((len(last_7_days) - len(prev_7_days)) / len(prev_7_days)) * 100
```

**Formula:**
```
Trend 7d % = ((Tickete ultimele 7 zile - Tickete 7 zile anterioare) / Tickete 7 zile anterioare) × 100
```

**Exemplu:**
- Zile 8-14 (anterior): 50 tickete
- Zile 1-7 (recent): 60 tickete
- Calcul: `((60 - 50) / 50) * 100 = +20%`
- Rezultat: **+20%** (creștere cu 20%)

**Interpretare:**
- Pozitiv (+) = Creștere volum tickete
- Negativ (-) = Scădere volum tickete

---

## 5. Health Metrics

### 📊 Resolution Rate

**Cod sursa:** liniile 808-810
```python
closed_count = len(df[df['closed_at'].notna()])
total_count = len(df)
resolution_rate = (closed_count / total_count * 100) if total_count > 0 else 0
```

**Formula:**
```
Resolution Rate % = (Tickete Închise / Total Tickete) × 100
```

**Exemplu:**
- Total tickete: 1813
- Tickete închise: 1650
- Calcul: `(1650 / 1813) * 100 = 91.0%`
- Rezultat: **91.0%**

---

### 😊 Sentiment Score

**Cod sursa:** liniile 814-824
```python
sentiment_counts = df['sentiment'].value_counts()
positive = sentiment_counts.get('pozitiv', 0)
neutral = sentiment_counts.get('neutru', 0)
negative = sentiment_counts.get('negativ', 0)

total_sentiment = sentiment_counts.sum()
sentiment_score = ((positive - negative) / total_sentiment) * 100
```

**Formula:**
```
Sentiment Score = ((Pozitive - Negative) / Total) × 100
```

**Ponderare:**
- Pozitiv: **+1**
- Neutru: **0** (nu afectează scorul)
- Negativ: **-1**

**Exemplu:**
- Pozitive: 800
- Neutre: 700
- Negative: 313
- Total: 1813
- Calcul: `((800 - 313) / 1813) * 100 = +26.9%`
- Rezultat: **+26.9%**

**Interpretare:**
- \> 0% = Sentiment pozitiv general
- = 0% = Echilibrat
- < 0% = Sentiment negativ general

---

### 🔄 Recurring Issues %

**Cod sursa:** liniile 827-829
```python
recurrent_count = len(df[df['is_recurrent'] == True])
recurrent_pct = (recurrent_count / len(df) * 100) if len(df) > 0 else 0
```

**Formula:**
```
Recurring % = (Tickete Recurente / Total Tickete) × 100
```

(Vezi detalii complete în [Secțiunea 2](#2-recurring-issues))

---

## 6. Critical Open Issues

### 🚨 Description
Tickete critice deschise care afectează business-ul clienților.

### 📋 Criterii de Selecție

**Cod sursa:** liniile 369-372
```python
critical_df = df[
    (df['urgency'].str.lower() == 'blocker') &
    (df['affects_business_flow'] == True)
]
```

**Condiții:**
- `urgency = 'blocker'` **ȘI**
- `affects_business_flow = TRUE`

---

### 📊 Indicatori

#### 6.1 Critical Issues (total)

**Cod sursa:** linia 702
```python
critical_count = len(critical_df)
```

**Descriere:** Numărul total de issue-uri critice (închise + deschise).

---

#### 6.2 Still Open

**Cod sursa:** liniile 705-706
```python
still_open = len(critical_df[critical_df['closed_at'].isna()])
```

**Descriere:** Câte issue-uri critice sunt ÎNCĂ deschise (nu au `closed_at`).

---

#### 6.3 Oldest Issue (days)

**Cod sursa:** liniile 710-713
```python
oldest_date = critical_df['created_at'].min()
max_date = df['created_at'].max()
days_old = (max_date - oldest_date).days
```

**Formula:**
```
Oldest Issue = (Data Maximă Dataset - Data Creare Cel Mai Vechi Issue).days
```

**Exemplu:**
- Cel mai vechi issue: 2025-01-15
- Data maximă în dataset: 2025-10-09
- Calcul: `(2025-10-09) - (2025-01-15) = 267 days`
- Rezultat: **267 days**

---

## 7. Sentiment Analysis

### 😊 Customer Sentiment Distribution

**Cod sursa:** liniile 206-235 (funcția `create_sentiment_chart`)

### 📋 Categorii

| Sentiment | Culoare | Semnificație |
|-----------|---------|--------------|
| **Pozitiv** | 🟢 Verde | Client mulțumit |
| **Neutru** | 🟡 Galben | Fără emoție puternică |
| **Negativ** | 🔴 Roșu | Client nemulțumit |

### 📊 Calcul Procente

**Cod sursa:**
```python
sentiment_counts = df['sentiment'].value_counts()
# Graficul Pie Chart afișează automat procentele
```

**Exemplu:**
- Pozitiv: 800 (44.1%)
- Neutru: 700 (38.6%)
- Negativ: 313 (17.3%)
- Total: 1813 (100%)

---

## 8. Platform Distribution

### 🏢 Description
Distribuția ticketelor pe platforme (facturare, gestiune, api, etc.)

### 📋 Calcul

**Cod sursa:** liniile 325-326
```python
platform_counts = df['platform'].value_counts()
```

### 📊 Breakdown Table

**Cod sursa:** liniile 665-673
```python
platform_stats = df.groupby('platform').agg({
    'platform': 'size',
    'affects_business_flow': lambda x: (x == True).sum(),
    'is_recurrent': lambda x: (x == True).sum()
}).rename(columns={
    'platform': 'total_tickets',
    'affects_business_flow': 'business_impact',
    'is_recurrent': 'recurrent'
})
```

**Coloane:**
- **Total Tickets:** Număr total tickete pe platformă
- **Business Impact:** Câte tickete afectează business-ul
- **Recurrent:** Câte tickete sunt recurente

**Exemplu:**

| Platform | Total Tickets | Business Impact | Recurrent |
|----------|---------------|-----------------|-----------|
| facturare | 850 | 180 | 32 |
| gestiune | 620 | 95 | 18 |
| api | 343 | 128 | 19 |

---

## 9. FAQ

### ❓ De ce se exclud ticketele > 30 zile din Average Resolution Time?

**Răspuns:** Ticketele cu timpul de rezolvare > 30 zile (270 ore business) sunt considerate outlier-i care pot distorsiona media. Acestea sunt:
- Tickete care au rămas deschise mult timp din motive neobișnuite
- Cazuri excepționale care nu reflectă performanța normală
- Contorizate separat în "excluded_count"

---

### ❓ Ce înseamnă "business hours only"?

**Răspuns:**
- Se numără DOAR orele Luni-Vineri, 09:00-18:00
- Weekend-urile (Sâmbătă, Duminică) sunt EXCLUSE
- Orele din afara programului (18:00-09:00) sunt EXCLUSE
- Acest calcul reflectă timpul real de lucru al echipei de support

---

### ❓ De ce "Recurring Issues %" apare în 2 locuri diferite?

**Răspuns:**
1. **Health Check tab, Recurring Issues section:** Afișează 4 metrici detaliate (total, business impact, blockers, bugs)
2. **Executive Summary tab, Health Metrics:** Afișează doar procentul total pentru overview rapid

Ambele folosesc același calcul, dar au scopuri diferite:
- Primul = analiză detaliată
- Al doilea = vedere de ansamblu executivă

---

### ❓ Cum se calculează culoarea pentru Business Flow Impact gauge?

**Răspuns:**
```python
if percentage >= 50:      # >= 50%
    color = 'red'         # 🔴 Critical
elif percentage >= 30:    # 30-49%
    color = 'yellow'      # 🟡 Significant
else:                     # < 30%
    color = 'green'       # 🟢 Moderate
```

---

### ❓ Ce înseamnă "delta_color: inverse" la Recurring Issues?

**Răspuns:**
```python
st.metric("Recurring Issues", f"{recurrent_pct:.1f}%", delta_color="inverse")
```

- `delta_color="inverse"` înseamnă că:
  - Creștere (+) = 🔴 ROȘ (rău, mai multe probleme recurente)
  - Scădere (-) = 🟢 VERDE (bun, mai puține probleme recurente)

Normal, în Streamlit, creșterea este verde (bună), dar pentru recurring issues, vrem opusul.

---

### ❓ Cum afectează filtrele de date toate calculele?

**Răspuns:**
Toate calculele se bazează pe `df` care este filtrat la începutul main():

```python
if len(date_range) == 2:
    df = df[(df['created_at'].dt.date >= date_range[0]) &
            (df['created_at'].dt.date <= date_range[1])]
```

**Rezultat:** TOȚI indicatorii reflectă DOAR perioada selectată în filtru.

---

### ❓ Care este diferența între Critical Issues și Blockers?

**Răspuns:**

| Indicator | Condiție | Descriere |
|-----------|----------|-----------|
| **Blockers** | `urgency = 'blocker'` | Orice ticket cu urgență mare |
| **Critical Issues** | `urgency = 'blocker'` ȘI `affects_business_flow = TRUE` | DOAR blockerii care afectează și business-ul |

**Critical Issues** este un subset mai strict din **Blockers**.

---

## 📚 Resurse Suplimentare

### Cod Sursa
- **Dashboard:** `pages/1_📊_DASHBOARD.py`
- **Data Processor:** `utils/data_processor.py`
- **Charts:** `utils/charts.py`

### Schema Date CSV
- Documentație: `.claude/CLAUDE.md` - secțiunea "CSV Data Schema"

### Contact
Pentru întrebări sau sugestii despre calculele indicatorilor, contactați echipa de development.

---

**Document generat:** 2025-10-09
**Aplicație:** SmartBill Support Analytics Dashboard v3.1
