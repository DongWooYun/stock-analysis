# 📅 프로젝트 타임라인

## ✅ Day 1 완료 (2026.03.23)
- DART API 연결 + KOSPI200 / KOSDAQ100 종목 수집
- 전체 재무데이터 수집: financials_v1.csv (295개)
- 금융주 / 적자기업 / 고PER 성장주 그룹 분리
- clean_data_final.csv (133개) 확정

## ✅ Day 2 완료 (2026.03.24)
- 섹터별 중앙값 PER 계산
- 시장 PER / 섹터 PER 기준 적정주가 산출
- 괴리율 v1 산출 → gap_v1_refined.csv (136개)
- signal 분류 (강력매수 / 매수 / 중립 / 매도 / 강력매도)

## ✅ Day 3 완료 (2026.03.24)
- corp_code zfill(8) 패딩 버그 수정
- 분기 EPS 수집 함수 완성 (계정명 20여 가지 변형 대응)
- 전체 수집: 133/133개 성공 (실패 0개)
- TTM YoY 성장률 계산: 100/136개

## ✅ Day 4 완료 (2026.03.25)
- 괴리율 v2 공식 확정
  - 고평가(gap>0)만 YoY 성장률로 완화
  - adjusted_gap = gap × (1 - yoy_decimal × 0.5)
  - YoY 캡: 100%
- 3중 스크리닝 조건 적용 → 최종 저평가 26개
- gap_v2.csv (136개) / gap_v2_final.csv (26개) 저장

## ✅ Day 5 완료 (2026.03.28)
- Streamlit 대시보드 6탭 제작 + 배포
  - Tab 1: 저평가 스크리닝 (TOP10 · 섹터 카드 · 버블차트)
  - Tab 2: 괴리율 분석 (기본 vs 조정 비교 · 히트맵)
  - Tab 3: YoY 성장률 분포 · 산점도
  - Tab 4: 종목 상세 (평균 조정괴리율 게이지)
  - Tab 5: 금융 섹터 ROE 분석
  - Tab 6: 업데이트 내역
- 배포: https://stock-analysis-dongwooyun.streamlit.app/

## ✅ Day 6 완료 (2026.03.29)
- README.md 한/영 병기 작성 (영문 먼저)
- Day 1~5 노트북 생성 (주석 포함)
- requirements.txt 작성
- GitHub 전체 업로드

## ✅ Day 7 완료 (2026.03.30)
- 백테스팅 기준일: 2025-03-30
- 옵션B (월말) / 옵션C (만기+5영업일) 동시 계산
- 벤치마크: KOSPI · KOSDAQ · KRX가중 · 기준금리 · CD91일 · 미국10년물
- 결과:
  - Pearson r=-0.156 (12M), p=0.070 → H0 기각불가
  - ANOVA p<0.0001 → 시그널 그룹 간 차이 유의
  - 강력매수 12M: +201.1% vs KOSPI +112.6% → 알파 +88.5%
- 저장: backtest_result.csv / backtest_stats.csv / backtest_chart.png

## ✅ Day 8 완료 (2026.03.31)
- Random Forest (n=97, CV R²=-0.131 과적합)
- 피처 중요도:
  YoY(27.5%) > 섹터괴리율(22.8%) > 섹터PER(13.8%) >
  EPS(12.9%) > 부채비율(10.7%) > 시장괴리율(6.5%) > PER(5.8%)
- SHAP 분석: YoY > 섹터PER > 섹터괴리율 순
- 저장: rf_feature_importance.csv / shap_importance.csv

## ✅ Day 9 완료 (2026.03.31)
- 자동화 파이프라인 run_pipeline() 완성
- DART 2025 사업보고서 133/133개 공시 확인
- 현재가 재수집 + 괴리율 갱신
- 시장 중앙값 PER: 19.4 → 29.22 (KOSPI +112% 반영)
- 저평가 종목: 26개 → 16개
- GitHub 자동 푸시 완료

## ✅ Day 10 완료 (2026.04.02)
- GitHub Actions 스케줄링 설정 (평일 매일 09:00 자동 실행)
- Tab 7 과거 데이터 분석 탭 추가
  - 백테스팅 결과 (시그널별 수익률 · 벤치마크 알파 · 가설검정)
  - ML 피처 중요도 (RF + SHAP)
- 노트북 Day 6~8 추가
- 타임라인 최신화
- 프로젝트 완료 🎉

---

## 🗂️ 트러블슈팅 로그

### corp_code 패딩 소실
- 원인: CSV 저장 시 숫자형으로 읽혀 앞자리 00 소실
- 해결: `dtype={'corp_code': str}` + `.str.zfill(8)` 필수

### EPS 계정명 불일치
- 원인: 기업마다 20여 가지 계정명 변형 존재
- 해결: EPS_ACCOUNT_NAMES set으로 전수 대응

### GitHub push 실패
- 원인: 토큰 자리에 한글 입력 / 원격 브랜치 충돌
- 해결: `git remote set-url` 실제 토큰값 재설정 + `--force`

### KRX 통합 지수 수집 실패
- 원인: FinanceDataReader 'KRX' 티커 미지원
- 해결: KOSPI(85%) + KOSDAQ(15%) 시총 가중 평균으로 대체

### 나눔고딕 폰트 경고
- 원인: Colab 환경에 나눔고딕 미설치
- 해결: 차트 영문화로 전환 (한글 폰트 불필요)

### Token.gdoc Git 추적 문제
- 원인: Google Drive의 .gdoc 파일이 git add에 포함
- 해결: .gitignore에 *.gdoc 추가

---

## 📁 최종 파일 현황
```
stock-analysis/
├── notebooks/
│   ├── day1_data_collection.ipynb
│   ├── day2_gap_v1.ipynb
│   ├── day3_eps_yoy.ipynb
│   ├── day4_screening.ipynb
│   ├── day5_dashboard.ipynb
│   ├── day6_backtesting.ipynb
│   ├── day7_ml_feature_importance.ipynb
│   └── day8_pipeline.ipynb
├── streamlit_app/
│   ├── app.py (7탭)
│   └── data/output/
│       ├── gap_v2.csv (136개)
│       ├── gap_v2_final.csv (16개)
│       ├── finance_roe.csv
│       ├── backtest_result.csv
│       ├── backtest_stats.csv
│       ├── rf_feature_importance.csv
│       └── shap_importance.csv
├── data/
│   ├── processed/
│   └── output/
├── docs/
│   └── timeline.md
├── .github/
│   └── workflows/
│       └── daily_update.yml
├── pipeline.py
├── README.md
├── requirements.txt
└── .gitignore
```
