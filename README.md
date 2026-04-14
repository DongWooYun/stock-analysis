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
| ML | scikit-learn (Random Forest), SHAP |
| Automation | GitHub Actions |
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
stock-analysis/
├── notebooks/
│   ├── day1_data_collection.ipynb
│   ├── day2_gap_v1.ipynb
│   ├── day3_eps_yoy.ipynb
│   ├── day4_gap_v2_screening.ipynb
│   ├── day5_dashboard.ipynb
│   ├── day6_backtesting.ipynb
│   ├── day7_ml_feature_importance.ipynb
│   └── day8_pipeline.ipynb
├── streamlit_app/
│   ├── app.py                  # 8-tab dashboard
│   ├── requirements.txt
│   └── data/output/
│       ├── gap_v2.csv          # Full 136 stocks
│       ├── gap_v2_final.csv    # Screened 16 stocks
│       ├── finance_roe.csv
│       ├── backtest_result.csv
│       ├── backtest_stats.csv
│       ├── rf_feature_importance.csv
│       └── shap_importance.csv
├── .github/
│   └── workflows/
│       └── daily_update.yml    # Auto pipeline (weekdays 09:00 KST)
├── pipeline.py
├── README.md
├── requirements.txt
└── .gitignore

---

## 📈 Key Results

| Item | Value |
|------|-------|
| Analysis Target | 136 stocks |
| YoY Data Available | 100 stocks |
| Final Screened | **16 stocks** (as of 2026-03-31) |
| Strong Buy Signal | 43 stocks |
| Backtesting Base Date | 2025-03-30 |
| Strong Buy 12M Return | +201.1% |
| vs KOSPI Alpha | +88.5% |
| ANOVA p-value | < 0.0001 |
| Top SHAP Feature | YoY Growth Rate (27.5%) |

---

## 🤖 AI Chatbot (Tab 8)
- Powered by **Groq API (LLaMA3-70B)** — Free & Public
- FAQ section (instant answers, no API call)
- Free-form questions grounded in gap_v2.csv data
- Example: "삼성전자 왜 강력매수야?" → Data-based AI analysis

---

## ⚠️ Disclaimer

This project is for portfolio purposes only and does not constitute investment advice.
Gap thresholds (±15%, ±30%) are arbitrarily set and require further backtesting validation.

---

## 🔜 Roadmap

- [ ] Foreign/institutional buying pressure indicator
- [ ] Multi-year backtesting (2023~2026)
- [ ] Cloud DB migration (Snowflake / BigQuery)

---

## 👤 Author

**Dongwoo Yun (윤동우)**
- GitHub: [@DongWooYun](https://github.com/DongWooYun)
- Email: sjdy0104@gmail.com

---

*Data basis: DART 2024 Annual Financial Statements | YoY based on TTM EPS | Auto-updated every weekday 09:00 KST*

---

<br>

---

# 📈 한국 주식 괴리율 기반 저평가 종목 분석 대시보드

---

## 📌 프로젝트 개요

인하대 글로벌금융학과 재학 중 투자론·증권분석 등 전공 수업에서
종목 분석 시 괴리율을 Excel로 수작업 산출하던 경험에서 출발했습니다.
데이터 분석 역량을 기르는 과정에서 그 경험이 떠올라,
Python으로 자동화된 개선 버전을 만들어보고 싶어 착수한 프로젝트입니다.

---

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

---

## 📈 주요 결과

| 항목 | 수치 |
|------|------|
| 분석 대상 | 136개 |
| 최종 저평가 | **16개** (2026-03-31 기준) |
| 강력매수 시그널 | 43개 |
| 백테스팅 기준일 | 2025-03-30 |
| 강력매수 12M 수익률 | +201.1% |
| vs KOSPI 알파 | +88.5% |
| ANOVA p값 | < 0.0001 |
| SHAP 1위 피처 | YoY 성장률 (27.5%) |

---

## 🤖 AI 챗봇 (Tab 8)
- **Groq API (LLaMA3-70B)** 기반 — 무료 공개
- FAQ 즉시 답변 섹션
- gap_v2.csv 데이터 기반 자유 질문
- 예시: "삼성전자 왜 강력매수야?" → 데이터 기반 AI 분석

---

## ⚠️ 주의사항

본 프로젝트는 데이터 분석 포트폴리오 목적으로 제작되었습니다.
분석 결과는 투자 권유가 아니며, 괴리율 기준값은 백테스팅을 통한 검증이 필요합니다.

---

## 🔜 향후 계획
- [ ] 외국인·기관 순매수 지표 추가
- [ ] 멀티연도 백테스팅 (2023~2026)
- [ ] 클라우드 DB 전환 (Snowflake / BigQuery)

---

*데이터 기준: DART 2024 연간 재무제표 | TTM EPS 기준 YoY 성장률 | 매 영업일 09:00 자동 갱신*
