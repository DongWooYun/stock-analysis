# 📈 Korean Stock Undervaluation Analysis Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stock-analysis-dongwooyun.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Overview

This project originated from manually calculating valuation gaps in Excel during finance-related coursework (Investment Theory, Securities Analysis, etc.) at Inha University.
While developing data analysis skills, I revisited that experience and wanted to build an automated, improved version using Python.

It targets approximately 300 stocks from KOSPI200 + KOSDAQ100, using DART Open API and FinanceDataReader
to automatically calculate PER-based valuation gaps and screen for undervalued stocks using YoY growth-adjusted gaps.

---

## 🚀 Live Demo

👉 **[https://stock-analysis-dongwooyun.streamlit.app/](https://stock-analysis-dongwooyun.streamlit.app/)**

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.10+ |
| Data Collection | DART Open API, FinanceDataReader |
| Data Processing | pandas, numpy |
| Visualization | Plotly, Streamlit |
| Deployment | Streamlit Cloud, GitHub |
| Environment | Google Colab, Google Drive |

---

## 📊 Methodology

### 1. Data Collection
- DART Open API → Annual EPS, Financial Statements (revenue, operating income, net income, debt ratio, etc.)
- FinanceDataReader → Current stock price, market capitalization
- Quarterly EPS collection → YoY growth rate based on TTM (Trailing Twelve Months)

### 2. Gap Calculation
```python
Market Gap   = (Current PER - Market Median PER) / Market Median PER
Sector Gap   = (Current PER - Sector Average PER) / Sector Average PER

# Adjusted Gap (applied to overvalued stocks only)
adjusted_gap = gap - (gap × yoy_decimal × 0.5)
# YoY cap: 100% (to prevent outlier distortion)
```

### 3. Screening Criteria

| Condition | Threshold |
|-----------|-----------|
| Adjusted Market Gap | ≤ -15% |
| Adjusted Sector Gap | ≤ -15% |
| YoY Growth Rate | > 0% or N/A |
| Debt Ratio | < 200% |

### 4. Signal Classification

| Signal | Criteria (Avg of Market & Sector Adjusted Gap) |
|--------|------------------------------------------------|
| 🔵 Strong Buy | ≤ -30% |
| 🟢 Buy        | ≤ -15% |
| ⚪ Neutral    | -15% ~ +15% |
| 🟡 Sell       | ≥ +15% |
| 🔴 Strong Sell| ≥ +30% |

### 5. Financial Sector
- Banks, securities, insurance → analyzed separately using **ROE**

---

## 📁 Project Structure
```
stock-analysis/
├── notebooks/
│   ├── day1_data_collection.ipynb
│   ├── day2_gap_v1.ipynb
│   ├── day3_eps_collection.ipynb
│   ├── day4_gap_v2_screening.ipynb
│   └── day5_dashboard.ipynb
├── streamlit_app/
│   ├── app.py
│   ├── requirements.txt
│   └── data/output/
│       ├── gap_v2.csv
│       ├── gap_v2_final.csv
│       └── finance_roe.csv
├── data/
│   ├── processed/
│   └── output/
├── docs/
│   ├── troubleshooting_log.md
│   └── timeline.md
└── README.md
```

---

## 📈 Key Results

| Item | Value |
|------|-------|
| Analysis Target | 136 stocks |
| YoY Data Available | 100 stocks |
| Final Screened | **26 stocks** |
| Strong Buy Signal | 42 stocks |
| Data Reference | DART 2024 Annual Financials |

---

## ⚠️ Disclaimer

This project is for portfolio purposes only and does not constitute investment advice.
Gap thresholds (±15%, ±30%) are arbitrarily set and require backtesting validation.

---

## 🔜 Roadmap

- [ ] Backtesting (DART disclosure date + 5 business days)
- [ ] ML feature importance (Random Forest + SHAP)
- [ ] DART 2025 auto-sync pipeline (daily API check)
- [ ] Airflow DAG automation (Astronomer.io)
- [ ] Cloud DB migration (Snowflake / BigQuery)

---

## 👤 Author

**Dongwoo Yun (윤동우)**
- GitHub: [@DongWooYun](https://github.com/DongWooYun)
- Email: sjdy0104@gmail.com

---

*Data basis: DART 2024 Annual Financial Statements | YoY based on TTM EPS*

---

<br>

---

# 📈 한국 주식 괴리율 기반 저평가 종목 분석 대시보드

## 📌 프로젝트 개요

인하대 글로벌금융학과 재학 중 투자론·증권분석 등 전공 수업에서
종목 분석 시 괴리율을 Excel로 수작업 산출하던 경험에서 출발했습니다.
데이터 분석 역량을 기르는 과정에서 그 경험이 떠올라,
Python으로 자동화된 개선 버전을 만들어보고 싶어 착수한 프로젝트입니다.

KOSPI200 + KOSDAQ100 약 300개 종목을 대상으로 DART Open API와 FinanceDataReader를 활용해
PER 기반 괴리율을 자동 산출하고, YoY 성장률을 반영한 조정괴리율로 저평가 종목을 스크리닝합니다.

## 🚀 배포 주소

👉 **[https://stock-analysis-dongwooyun.streamlit.app/](https://stock-analysis-dongwooyun.streamlit.app/)**

## 📊 분석 방법론

### 괴리율 산출
```python
시장 괴리율 = (현재 PER - 시장 중앙값 PER) / 시장 중앙값 PER
섹터 괴리율 = (현재 PER - 섹터 평균 PER) / 섹터 평균 PER

# 조정괴리율 (고평가 구간만 적용)
adjusted_gap = gap - (gap × yoy_decimal × 0.5)
```

### 스크리닝 조건
| 조건 | 기준 |
|------|------|
| 시장 조정괴리율 | ≤ -15% |
| 섹터 조정괴리율 | ≤ -15% |
| YoY 성장률 | > 0% 또는 N/A |
| 부채비율 | < 200% |

## 📈 주요 결과

| 항목 | 수치 |
|------|------|
| 분석 대상 | 136개 |
| YoY 수집 | 100개 |
| 최종 저평가 스크리닝 | **26개** |
| 강력매수 시그널 | 42개 |

## ⚠️ 주의사항

본 프로젝트는 데이터 분석 포트폴리오 목적으로 제작되었습니다.
분석 결과는 투자 권유가 아니며, 괴리율 기준값은 백테스팅을 통한 검증이 필요합니다.

## 🔜 향후 계획
- [ ] 백테스팅: DART 공시일 + 5영업일 기준 수익률 검증
- [ ] ML 피처 중요도 분석 (Random Forest + SHAP)
- [ ] DART 2025 사업보고서 자동 감지 및 동기화
- [ ] Airflow DAG 기반 자동화 파이프라인

*데이터 기준: DART 2024 연간 재무제표 | TTM EPS 기준 YoY 성장률*
