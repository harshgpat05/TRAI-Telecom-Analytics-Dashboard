# 📡 TRAI India Telecom Market Analysis

> Wireless Subscriber Trends, Market Share & Broadband Intelligence — Jan 2025 to Aug 2026

---

## 📋 Project Description

This project performs a comprehensive **data analysis of India's telecom market** using official datasets published by the **Telecom Regulatory Authority of India (TRAI)**. It covers 6 national wireless operators across 23 Licensed Service Areas (LSAs) over 19 months (January 2025 – August 2026).

The analysis delivers insights across five key dimensions:

| Dimension | What's Analysed |
|-----------|----------------|
| 📈 **Subscriber Growth** | National wireless subscriber trajectory and net monthly additions |
| 🥧 **Market Share** | Operator share evolution — Jio, Airtel, Vi, BSNL |
| 🗺️ **Regional (LSA)** | Operator dominance per telecom circle across India |
| 🌐 **Broadband** | Total broadband penetration and top-5 provider breakdown |
| 🔀 **MNP & Churn** | Mobile Number Portability trends as a proxy for competition |

---

## 📂 Repository Structure

```
├── Harshwardhanpatil_TRAI_Telecom_Analysis.ipynb   # Main Jupyter Notebook (complete analysis)
├── requirements.txt                        # Python dependencies
├── HarshwardhanPatil_ProjectReport.docx            # Full project report (Word)
├── README.md                               # This file
│
├── TRAI_Wireless_LSA_Long.csv             # Raw dataset 1 — LSA-level wireless subs
├── TRAI_Telecom_Analytics_Dataset.xlsx    # Raw dataset 2 — National + broadband + MNP
│
└── (Generated on notebook run)
    ├── cleaned_lsa_wireless.csv
    ├── cleaned_national_operator_monthly.csv
    ├── cleaned_national_summary.csv
    ├── cleaned_broadband_top5.csv
    ├── fig1_national_growth.png
    ├── fig2_operator_trends.png
    ├── fig3_market_share_stacked.png
    ├── fig4_market_share_pie.png
    ├── fig5_mom_additions.png
    ├── fig6_jio_airtel_gap.png
    ├── fig7_lsa_heatmap.png
    ├── fig8_lsa_share.png
    ├── fig9_broadband.png
    ├── fig10_mnp.png
    ├── fig11_urban_rural.png
    ├── fig12_correlation.png
    └── fig13_summary_dashboard.png
```

---

## 📊 Dataset

| File | Description | Rows | Key Fields |
|------|-------------|------|-----------|
| `TRAI_Wireless_LSA_Long.csv` | Monthly wireless subscribers per operator per LSA | 1,764 | month, lsa, operator, wireless_mobile_subscribers, value_status |
| `TRAI_Telecom_Analytics_Dataset.xlsx` | 8 sheets covering national summary, operator monthly, broadband top-5, data quality | 1,765+ | broadband_total_million, mnp_requests_million, market_share_pct, month_over_month_change |

**Source:** Telecom Regulatory Authority of India (TRAI)  
**Official Website:** [https://www.trai.gov.in](https://www.trai.gov.in)(https://docs.google.com/spreadsheets/d/1TFgy3lWbGknU_lDYMIDV7U3vLdiNo6h-/edit?usp=drivesdk&ouid=118056269244685114086&rtpof=true&sd=true)(https://drive.google.com/file/d/1r4lwnG84zrkdIQlVpI0s_t_4DoWu3Fx-/view?usp=drivesdk)
**Coverage:** January 2025 – August 2026 (14 monthly snapshots, 5-month data gap Sep 2025–Jan 2026)

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core language |
| pandas | 2.0+ | Data manipulation and cleaning |
| numpy | 1.24+ | Numerical operations |
| matplotlib | 3.7+ | Charts and visualisations |
| seaborn | 0.12+ | Heatmaps and statistical plots |
| openpyxl | 3.1+ | Reading Excel (.xlsx) files |
| Jupyter Notebook | 7.0+ | Interactive analysis environment |

---

## ⚙️ Setup & Run Instructions

### 1. Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Place Dataset Files

Ensure both dataset files are in the **same directory** as the notebook:
```
TRAI_Wireless_LSA_Long.csv
TRAI_Telecom_Analytics_Dataset.xlsx
```

### 4. Launch Jupyter Notebook

```bash
jupyter notebook Harshwardhanpatil_TRAI_Telecom_Analysis.ipynb
```

### 5. Run All Cells

In Jupyter: **Kernel → Restart & Run All**

All 13 chart PNG files and 4 cleaned CSV exports will be generated automatically in the same directory.

---

## 🔑 Key Findings

1. **Airtel's Remarkable Surge** — Added 104M subscribers (+27%) in 19 months; closed the Jio gap from 78.8M to 16.8M
2. **Jio's Share Erosion** — Despite +42.6M subs, market share fell from 40.5% → 39.3%
3. **Vi Stabilising** — Consistent losses through 2025 turned near-flat in 2026 post-fundraising
4. **India crossed 1 billion broadband subscribers** between Oct 2025 and Feb 2026
5. **MNP requests up 31.3%** — Record competitive churn in the market
6. **Widening urban-rural divide** — Urban subs +18.1% vs rural +3.7% (Aug 2025–Aug 2026)
7. **BSNL reversed decline** — Government 4G rollout producing measurable subscriber gains

---

## 📁 Submitted Files

| File | Format | Description |
|------|--------|-------------|
| `Harshwardhanpatil_TRAI_Telecom_Analysis.ipynb` | `.ipynb` | Complete Jupyter Notebook |
| `requirements.txt` | `.txt` | Python library dependencies |
| `HarshwardhanPatil_ProjectReport.docx` | `.docx` | Full project report |
| `README.md` | `.md` | This file |

---

## ⚠️ Data Limitations

- **5 missing months** (Sep 2025–Jan 2026): Source PDFs not available; MoM comparisons bridge the gap
- **299 blank-in-source rows**: Mainly MTNL (no licence outside Delhi/Mumbai); intentionally kept as NaN
- **Oct 2025 LSA data excluded**: PDF column-shift corrupted operator assignments for that month
- **Early broadband figures**: TRAI's own footnotes flag Feb/Apr 2025 Jio/Airtel broadband data as Nov 2024 vintage

---

## 👤 Author

**Name:** Harshwardhan Patil
**Course:** Data Analytics / Data Science
**Institution:** Bharati Vidyapeeth College of Engineering, Navi Mumbai
**Year:** 2025

---

*Data Source: Telecom Regulatory Authority of India (TRAI) — trai.gov.in*
