
import streamlit as st
from faq_data import FAQ
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="한국 주식 괴리율 기반 저평가 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

@st.cache_data
def load_data():
    df_v2    = pd.read_csv("data/output/gap_v2.csv", dtype={"Code": str, "corp_code": str})
    df_final = pd.read_csv("data/output/gap_v2_final.csv", dtype={"Code": str, "corp_code": str})
    try:
        df_fin = pd.read_csv("data/output/finance_roe.csv", dtype={"Code": str})
        df_fin["ROE_pct"] = (df_fin["ROE"] * 100).round(2)
    except:
        df_fin = pd.DataFrame()
    return df_v2, df_final, df_fin

df_v2, df_final, df_fin = load_data()

SIGNAL_V1_MAP = {
    "— 고평가": "고평가",
    "⚠️ 주의":  "주의",
    "🔥 강력":  "강력매수/매도",
}
df_v2["signal_v1_clean"] = df_v2["signal"].map(SIGNAL_V1_MAP).fillna(df_v2["signal"])

COLOR_MAP = {
    "강력매수": "#5B8DEF", "매수": "#1D9E75",
    "중립": "#888888", "매도": "#EF9F27", "강력매도": "#E24B4A"
}
SIGNAL_EMOJI = {
    "강력매수": "🔵", "매수": "🟢", "중립": "⚪", "매도": "🟡", "강력매도": "🔴"
}

# ── 사이드바 ──────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 한국 주식 괴리율 분석")
    st.markdown("**KOSPI200 + KOSDAQ100**")
    st.markdown("---")

    updated_at_side = df_v2["updated_at"].iloc[0] if "updated_at" in df_v2.columns else "N/A"
    st.markdown(f"📅 **기준일:** {updated_at_side}")
    st.markdown(f"📈 **분석 대상:** {len(df_v2)}개")
    st.markdown(f"🎯 **저평가 종목:** {len(df_final)}개")
    strong_buy = df_v2["signal_v2"].value_counts().get("강력매수", 0)
    st.markdown(f"🔵 **강력매수:** {strong_buy}개")

    st.markdown("---")
    st.markdown("### 🔍 종목 빠른 검색")
    search_name = st.text_input("종목명 입력", placeholder="예: 삼성전자")
    if search_name:
        result = df_v2[df_v2["Name"].str.contains(search_name, na=False)]
        if len(result) > 0:
            for _, row in result.iterrows():
                signal = row["signal_v2"]
                color = {"강력매수": "🔵", "매수": "🟢", "중립": "⚪",
                         "매도": "🟡", "강력매도": "🔴"}.get(signal, "⚪")
                st.markdown(f"{color} **{row['Name']}** ({signal})")
                st.markdown(f"시장괴리율: {row['gap_market_v2']*100:.1f}%")
        else:
            st.warning("종목을 찾을 수 없습니다.")

    st.markdown("---")
    st.markdown("### 📌 바로가기")
    st.markdown("- 🏆 저평가 스크리닝")
    st.markdown("- 📊 괴리율 분석")
    st.markdown("- 🔍 종목 상세")
    st.markdown("- 🤖 AI 챗봇 (Tab 8)")
    st.markdown("---")
    st.caption("⚠️ 본 대시보드는 분석 목적이며 투자 권유가 아닙니다.")

st.title("📈 한국 주식 괴리율 기반 저평가 분석 대시보드")
updated_at = df_v2["updated_at"].iloc[0] if "updated_at" in df_v2.columns else "N/A"
st.caption("KOSPI200 + KOSDAQ100 | DART Open API | PER 기반 괴리율 분석 (YoY 성장률 조정)")
st.info(f"📅 현재가 및 괴리율 기준일: **{updated_at}** | 매 영업일 09:00 자동 갱신")

with st.expander("📖 용어 설명 보기"):
    st.markdown("""
| 용어 | 설명 |
|------|------|
| **괴리율** | 현재 주가가 적정 주가 대비 얼마나 차이나는지의 비율. 음수(-)면 저평가, 양수(+)면 고평가 |
| **시장 조정괴리율** | 시장 전체 중앙값 PER 기준 괴리율에 YoY 성장률을 반영해 조정한 값 |
| **섹터 조정괴리율** | 동일 업종 평균 PER 기준 괴리율에 YoY 성장률을 반영해 조정한 값 |
| **기본괴리율** | 연간 EPS 기준, 성장률 조정 전 원래 괴리율 |
| **YoY 성장률** | 전년 동기 대비 TTM(최근 12개월) EPS 성장률 |
| **TTM** | Trailing Twelve Months — 최근 4분기 EPS 합산 (연환산) |
| **PER** | Price-to-Earnings Ratio — 주가 ÷ 주당순이익 |
| **ROE** | Return on Equity — 자기자본이익률. 금융주 핵심 지표 |
""")

st.divider()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("분석 대상", f"{len(df_v2)}개",
          help="KOSPI200 + KOSDAQ100 중 금융주·적자기업 제외 후 PER 산출 가능한 종목")
c2.metric("최종 저평가", f"{len(df_final)}개",
          help="시장·섹터 조정괴리율 모두 -15% 이하 + YoY > 0 + 부채비율 200% 이하 조건 통과")
c3.metric("YoY 수집", f"{df_v2['yoy_growth_pct'].notna().sum()}개",
          help="DART 분기보고서에서 TTM EPS 8분기 이상 수집 성공한 종목 수")
c4.metric("평균 괴리율", f"{df_final['gap_market_v2'].mean()*100:.1f}%",
          help="최종 저평가 26개 종목의 시장 조정괴리율 평균")
c5.metric("강력매수", f"{(df_v2['signal_v2']=='강력매수').sum()}개",
          help="시장·섹터 조정괴리율 평균이 -30% 이하인 종목")

st.caption("""
ℹ️ **수치 해석 가이드**
- **분석 대상 136개**: 전체 295개 → 금융주 27개·적자기업 49개·고PER 성장주 13개·데이터 부족 70개 제외
- **최종 저평가 26개**: 136개 중 괴리율·YoY·부채비율 3가지 조건 동시 충족 종목
- **YoY 수집 100개**: 나머지 36개는 DART 분기보고서 데이터 부족으로 YoY 미산출
""")
st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏆 저평가 스크리닝",
    "📊 괴리율 분석",
    "📈 YoY 성장률",
    "🔍 종목 상세",
    "🏦 금융 섹터",
    "📋 업데이트 내역", "📉 과거 데이터 분석", "🤖 AI 챗봇"
])

# ── Tab 1 ─────────────────────────────────────────────
with tab1:
    st.subheader("최종 스크리닝 결과")
    st.caption("조건: 시장·섹터 조정괴리율 모두 -15% 이하 | YoY > 0 or 데이터 없음 | 부채비율 200% 이하")

    # 저평가 TOP 10 세로 막대그래프 (시그널별 색상)
    st.subheader("📌 저평가 TOP 10")
    df_top10 = df_v2[df_v2["signal_v2"] == "강력매수"].sort_values("gap_market_v2").head(10).copy()
    df_top10["gap_abs"] = df_top10["gap_market_v2"].abs()
    df_top10["color"]   = df_top10["signal_v2"].map(COLOR_MAP)

    fig_top10 = go.Figure()
    for _, row in df_top10.iterrows():
        fig_top10.add_trace(go.Bar(
            x=[row["Name"]],
            y=[row["gap_abs"]],
            marker_color=COLOR_MAP.get(row["signal_v2"], "#888"),
            text=f"{row['gap_abs']*100:.1f}%",
            textposition="outside",
            name=row["signal_v2"],
            showlegend=False
        ))
    fig_top10.update_layout(
        template="plotly_dark", height=440,
        yaxis_title="저평가 정도 (%)",
        yaxis_tickformat=".0%",
        xaxis_tickangle=-20,
        margin=dict(l=20, r=20, t=40, b=80),
    )
    st.plotly_chart(fig_top10, use_container_width=True)

    # 섹터별 저평가 TOP3 카드 (순수 Streamlit)
    st.subheader("📌 섹터별 저평가 TOP 3")
    df_sector_top = (df_v2[df_v2["signal_v2"].isin(["강력매수", "매수"])]
                     .sort_values("gap_market_v2")
                     .groupby("Sector")
                     .head(3)).copy()
    df_sector_top["rank"] = df_sector_top.groupby("Sector")["gap_market_v2"].rank(
        method="first").astype(int)
    df_sector_top = df_sector_top.sort_values(["Sector", "rank"])
    sectors = df_sector_top["Sector"].unique()

    for i in range(0, len(sectors), 3):
        cols = st.columns(3)
        for j, sector in enumerate(sectors[i:i+3]):
            group = df_sector_top[df_sector_top["Sector"] == sector]
            with cols[j]:
                with st.container(border=True):
                    st.markdown(f"**{sector}**")
                    for _, row in group.iterrows():
                        emoji = SIGNAL_EMOJI.get(row["signal_v2"], "⚪")
                        yoy = f"{row['yoy_growth_pct']:.1f}%" if pd.notna(row["yoy_growth_pct"]) else "N/A"
                        st.markdown(
                            f"{emoji} **{row['rank']}위** {row['Name']}",
                        )
                        st.caption(f"PER {row['PER']:.1f} | YoY {yoy}")

    st.caption("🔵 강력매수: 시장·섹터 조정괴리율 평균 -30% 이하 &nbsp;&nbsp;|&nbsp;&nbsp; 🟢 매수: -15% 이하")
    st.divider()

    # 시그널 필터 테이블
    st.markdown("**📌 시그널 필터**")
    signal_order = ["강력매수", "매수", "중립", "매도", "강력매도", "전체"]
    SIGNAL_COLOR_LABEL = {
        "강력매수": "🔵 강력매수",
        "매수":     "🟢 매수",
        "중립":     "⚪ 중립",
        "매도":     "🟡 매도",
        "강력매도": "🔴 강력매도",
        "전체":     "📋 전체"
    }
    selected_signal = st.selectbox(
        label="시그널을 선택하세요",
        options=signal_order,
        format_func=lambda x: SIGNAL_COLOR_LABEL.get(x, x),
        index=0,
        key="signal_filter"
    )

    df_filtered = df_v2.copy() if selected_signal == "전체" else df_v2[df_v2["signal_v2"] == selected_signal].copy()

    cols_sel = ["Name", "Sector", "gap_market_v2", "gap_sector_v2",
                "yoy_growth_pct", "debt_ratio", "PER", "price", "signal_v2"]
    df_show = df_filtered[cols_sel].copy()
    df_show.columns = ["종목명", "섹터", "시장 조정괴리율", "섹터 조정괴리율",
                       "YoY성장률(%)", "부채비율(%)", "PER", "현재가", "시그널"]
    df_show["PER"]            = df_show["PER"].round(1)
    df_show["시장 조정괴리율"] = (df_filtered["gap_market_v2"] * 100).round(1).astype(str) + "%"
    df_show["섹터 조정괴리율"] = (df_filtered["gap_sector_v2"] * 100).round(1).astype(str) + "%"
    df_show["YoY성장률(%)"]   = df_filtered["yoy_growth_pct"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    df_show["부채비율(%)"]    = df_filtered["debt_ratio"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    df_show["현재가"]         = df_filtered["price"].apply(lambda x: f"{int(x):,}원" if pd.notna(x) else "N/A")
    df_show = df_show.reset_index(drop=True)

    # 시그널 컬럼 색상 적용
    SIGNAL_FONT = {
        "강력매수": "color: #5B8DEF; font-weight: 600",
        "매수":     "color: #1D9E75; font-weight: 600",
        "중립":     "color: #888888",
        "매도":     "color: #EF9F27; font-weight: 600",
        "강력매도": "color: #E24B4A; font-weight: 600",
    }

    def style_signal(val):
        return SIGNAL_FONT.get(val, "")

    def style_all(df):
        # 전체 왼쪽 정렬
        styled = pd.DataFrame("text-align: left", index=df.index, columns=df.columns)
        # 시그널 컬럼 색상
        styled["시그널"] = df["시그널"].map(lambda v: SIGNAL_FONT.get(v, ""))
        return styled

    styled_df = df_show.style.apply(style_all, axis=None)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    st.caption(f"총 {len(df_show)}개 종목")

    with st.expander("📖 시그널 기준 설명"):
        st.markdown("""
| 시그널 | 기준 (시장·섹터 조정괴리율 평균) |
|--------|----------------------------------|
| 🔵 **강력매수** | 평균 조정괴리율 ≤ -30% (심각한 저평가) |
| 🟢 **매수** | 평균 조정괴리율 ≤ -15% (저평가) |
| ⚪ **중립** | -15% < 평균 조정괴리율 < +15% |
| 🟡 **매도** | 평균 조정괴리율 ≥ +15% (고평가) |
| 🔴 **강력매도** | 평균 조정괴리율 ≥ +30% (심각한 고평가) |
> ⚠️ 기준값(±15%, ±30%)은 분석 목적의 임의 기준이며, 백테스팅 검증이 필요합니다.
""")

    st.subheader("전체 종목 괴리율 버블차트")
    st.caption("X축: 시장 조정괴리율 | Y축: 섹터 조정괴리율 | 버블크기: YoY성장률 | 색상: 시그널")
    df_bubble = df_v2.copy()
    df_bubble["bubble_size"] = df_bubble["yoy_growth_pct"].fillna(10).clip(0, 200) + 10
    fig_bubble = px.scatter(
        df_bubble, x="gap_market_v2", y="gap_sector_v2",
        size="bubble_size", color="signal_v2", text="Name",
        color_discrete_map=COLOR_MAP,
        hover_data={"Name": True, "PER": ":.1f", "yoy_growth_pct": ":.1f", "bubble_size": False},
        labels={"gap_market_v2": "시장 조정괴리율", "gap_sector_v2": "섹터 조정괴리율", "signal_v2": "시그널"},
        size_max=50
    )
    fig_bubble.add_hline(y=0, line_dash="dash", line_color="#555")
    fig_bubble.add_vline(x=0, line_dash="dash", line_color="#555")
    fig_bubble.add_hline(y=-0.15, line_dash="dot", line_color="#5B8DEF",
                         annotation_text="-15% 기준선", annotation_position="right")
    fig_bubble.add_vline(x=-0.15, line_dash="dot", line_color="#5B8DEF")
    fig_bubble.update_traces(textposition="top center", textfont_size=9)
    fig_bubble.update_layout(template="plotly_dark", height=600,
                              margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_bubble, use_container_width=True)

# ── Tab 2 ─────────────────────────────────────────────
with tab2:
    st.subheader("기본괴리율 vs 조정괴리율 비교 — 전체 136개")
    st.caption("기본괴리율: 연간 EPS 기준 | 조정괴리율: YoY 성장률 반영 (고평가 구간만 완화)")

    df_cmp = df_v2[["Name", "gap_market", "gap_market_v2", "yoy_growth_pct"]].copy()
    df_cmp = df_cmp.sort_values("gap_market_v2")

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        y=df_cmp["Name"], x=df_cmp["gap_market"] * 100,
        orientation="h", marker_color="#888888", name="기본괴리율", opacity=0.85
    ))
    fig_cmp.add_trace(go.Bar(
        y=df_cmp["Name"], x=df_cmp["gap_market_v2"] * 100,
        orientation="h", marker_color="#5B8DEF", name="조정괴리율"
    ))
    fig_cmp.update_layout(
        template="plotly_dark", barmode="group", height=2500,
        xaxis_title="괴리율 (%)", legend=dict(orientation="h", y=1.005),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    st.subheader("괴리율 조정폭 Top 15")
    df_delta = df_cmp.copy()
    df_delta["delta"] = df_delta["gap_market_v2"] - df_delta["gap_market"]
    df_delta = df_delta[df_delta["delta"] < 0].sort_values("delta").head(15)
    fig_delta = px.bar(
        df_delta, x="delta", y="Name", orientation="h",
        color="delta", color_continuous_scale=["#5B8DEF", "#1D9E75"],
        labels={"delta": "괴리율 조정폭 (조정 후 - 기본)", "Name": ""},
        title="괴리율 조정폭 Top 15"
    )
    fig_delta.update_layout(template="plotly_dark", height=450, coloraxis_showscale=False)
    st.plotly_chart(fig_delta, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        sig_counts = df_v2["signal_v2"].value_counts()
        fig_pie = px.pie(
            values=sig_counts.values, names=sig_counts.index,
            title="시그널 분포 (136개)",
            color=sig_counts.index, color_discrete_map=COLOR_MAP, hole=0.45
        )
        fig_pie.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.write("**시그널 변화: 성장률 조정 전 → 후**")
        st.caption("행: 조정 전 분류 | 열: 조정 후 시그널 | 숫자: 종목 수")
        signal_v2_order = ["강력매수", "매수", "중립", "매도", "강력매도"]
        ct = pd.crosstab(df_v2["signal_v1_clean"], df_v2["signal_v2"]).reindex(
            columns=signal_v2_order, fill_value=0)
        fig_heat = px.imshow(
            ct, text_auto=True,
            color_continuous_scale=["#1a1a2e", "#5B8DEF"],
            labels={"x": "조정 후 시그널", "y": "조정 전 분류", "color": "종목 수"},
            title="시그널 변화 히트맵"
        )
        fig_heat.update_layout(template="plotly_dark", height=300,
                                coloraxis_showscale=False,
                                margin=dict(l=20, r=20, t=40, b=20))
        fig_heat.update_traces(textfont_size=14)
        st.plotly_chart(fig_heat, use_container_width=True)

    # 섹터별 평균 조정괴리율 — 수치 직접 표시
    st.subheader("섹터별 평균 조정괴리율")
    sector_avg = df_v2.groupby("Sector")["gap_market_v2"].mean().sort_values()
    fig_sec = px.bar(
        x=sector_avg.values * 100,
        y=sector_avg.index,
        orientation="h",
        color=sector_avg.values,
        color_continuous_scale=["#5B8DEF", "#888888", "#E24B4A"],
        text=[f"{v*100:.1f}%" for v in sector_avg.values],
        labels={"x": "평균 조정괴리율 (%)", "y": "섹터", "color": "괴리율 (%)"},
        title="섹터별 평균 조정괴리율",
        range_color=[sector_avg.min()*100, sector_avg.max()*100]
    )
    fig_sec.update_traces(textposition="outside")
    fig_sec.update_layout(
        template="plotly_dark", height=500,
        coloraxis_colorbar=dict(title="괴리율(%)", tickformat=".0f", ticksuffix="%"),
        margin=dict(l=20, r=80, t=40, b=20)
    )
    st.plotly_chart(fig_sec, use_container_width=True)

    with st.expander("📌 조정 전 분류 기준"):
        st.markdown("""
| 조정 전 분류 | 의미 |
|-------------|------|
| **고평가** | 현재가 > 적정가 (기본괴리율 양수) |
| **주의** | 고평가이나 일부 긍정 지표 혼재 |
| **강력매수/매도** | 괴리율이 극단적으로 큰 종목 |
""")

# ── Tab 3 ─────────────────────────────────────────────
with tab3:
    st.subheader("YoY 성장률 분포")
    df_yoy = df_v2.dropna(subset=["yoy_growth_pct"]).copy()
    df_yoy["yoy_capped"] = df_yoy["yoy_growth_pct"].clip(-200, 500)

    fig_hist = px.histogram(
        df_yoy, x="yoy_capped", nbins=20,
        title=f"YoY 성장률 분포 ({len(df_yoy)}개)",
        labels={"yoy_capped": "YoY 성장률 (%)", "count": "종목 수"},
        color_discrete_sequence=["#5B8DEF"],
        text_auto=True
    )
    fig_hist.add_vline(x=0, line_dash="dash", line_color="#E24B4A",
                       annotation_text="0% 기준선", annotation_position="top right")
    fig_hist.update_traces(textfont_size=12, textangle=0,
                           textposition="outside", cliponaxis=False)
    fig_hist.update_layout(
        template="plotly_dark", height=420, yaxis_title="종목 수",
        uniformtext_minsize=12, uniformtext_mode="hide"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("YoY 성장률 vs 시장 조정괴리율 산점도")
    st.caption("**시장 조정괴리율**: 현재 PER과 시장 중앙값 PER의 차이 비율에 YoY 성장률을 반영한 값. 음수(-) = 저평가 / 양수(+) = 고평가")
    fig_scatter = px.scatter(
        df_yoy, x="yoy_growth_pct", y="gap_market_v2",
        text="Name", color="signal_v2",
        color_discrete_map=COLOR_MAP,
        title="YoY 성장률 vs 시장 조정괴리율",
        labels={"yoy_growth_pct": "YoY 성장률 (%)", "gap_market_v2": "시장 조정괴리율", "signal_v2": "시그널"}
    )
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="#888")
    fig_scatter.add_vline(x=0, line_dash="dash", line_color="#888")
    fig_scatter.update_traces(textposition="top center", textfont_size=10)
    fig_scatter.update_layout(template="plotly_dark", height=550)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Tab 4 ─────────────────────────────────────────────
with tab4:
    st.subheader("종목 상세 조회")
    st.markdown("**📌 종목 선택**")
    selected = st.selectbox(
        label="분석할 종목을 선택하세요",
        options=df_v2["Name"].sort_values().tolist(),
        key="stock_select"
    )
    row = df_v2[df_v2["Name"] == selected].iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("현재가", f"{int(row['price']):,}원" if pd.notna(row['price']) else "N/A")
    c2.metric("PER", f"{row['PER']:.1f}x" if pd.notna(row['PER']) else "N/A")
    with c3:
        signal_val  = row["signal_v2"]
        signal_hex  = {"강력매수": "#5B8DEF", "매수": "#1D9E75",
                       "중립": "#888888", "매도": "#EF9F27", "강력매도": "#E24B4A"}.get(signal_val, "#888")
        signal_icon = SIGNAL_EMOJI.get(signal_val, "⚪")
        st.markdown("시그널")
        st.markdown(
            f"<p style='font-size:28px; font-weight:600; color:{signal_hex}; margin:0;'>"
            f"{signal_icon} {signal_val}</p>",
            unsafe_allow_html=True
        )

    c4, c5, c6 = st.columns(3)
    c4.metric("시장 조정괴리율", f"{row['gap_market_v2']*100:.1f}%")
    c5.metric("섹터 조정괴리율", f"{row['gap_sector_v2']*100:.1f}%")
    c6.metric("YoY 성장률", f"{row['yoy_growth_pct']:.1f}%" if pd.notna(row['yoy_growth_pct']) else "N/A")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.write("**재무 데이터**")
        def fmt_억(v):
            if pd.isna(v): return "N/A"
            return f"{v/1e8:,.0f}억원"
        fin = {
            "매출액":   fmt_억(row["revenue"]),
            "영업이익": fmt_억(row["op_income"]),
            "순이익":   fmt_억(row["net_income"]),
            "총자산":   fmt_억(row["total_assets"]),
            "자기자본": fmt_억(row["equity"]),
            "부채비율": f"{row['debt_ratio']:,.1f}%" if pd.notna(row["debt_ratio"]) else "N/A",
            "EPS":      f"{row['EPS']:,.0f}원"       if pd.notna(row["EPS"]) else "N/A",
        }
        st.table(pd.DataFrame.from_dict(fin, orient="index", columns=["값"]))
    with col2:
        signal_val = row["signal_v2"]
        bar_color  = {"강력매수": "#5B8DEF", "매수": "#1D9E75",
                      "중립": "#888888", "매도": "#EF9F27", "강력매도": "#E24B4A"}.get(signal_val, "#888")

        gap_market = row["gap_market_v2"] * 100
        gap_sector = row["gap_sector_v2"] * 100
        gap_avg    = (gap_market + gap_sector) / 2

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gap_avg,
            title={"text": "평균 조정괴리율 (시장+섹터) / 2"},
            number={
                "suffix": "%",
                "font": {"color": bar_color, "size": 28}
            },
            gauge={
                "axis": {
                    "range": [-100, 100],
                    "tickvals": [-100, -30, -15, 0, 15, 30, 100],
                    "ticktext": ["-100%", "-30%", "-15%", "0%", "+15%", "+30%", "+100%"],
                    "tickfont": {"size": 10}
                },
                "bar": {"color": bar_color, "thickness": 0.3},
                "steps": [
                    {"range": [-100, -30], "color": "#0d2a4a"},
                    {"range": [-30,  -15], "color": "#0d3a2a"},
                    {"range": [-15,    0], "color": "#1a1a2e"},
                    {"range": [  0,   15], "color": "#2a1a1a"},
                    {"range": [ 15,   30], "color": "#3a2a0a"},
                    {"range": [ 30,  100], "color": "#3a0a0a"},
                ],
                "threshold": {
                    "line": {"color": "#ffffff", "width": 2},
                    "value": 0
                }
            }
        ))
        fig_gauge.update_layout(
            template="plotly_dark", height=300,
            margin=dict(l=20, r=20, t=50, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        g1, g2 = st.columns(2)
        g1.metric("시장 조정괴리율", f"{gap_market:.1f}%")
        g2.metric("섹터 조정괴리율", f"{gap_sector:.1f}%")
        st.caption(
            "🔵 -100~-30%: 강력매수 &nbsp;|&nbsp; "
            "🟢 -30~-15%: 매수 &nbsp;|&nbsp; "
            "⚪ -15~+15%: 중립 &nbsp;|&nbsp; "
            "🟡 +15~+30%: 매도 &nbsp;|&nbsp; "
            "🔴 +30~+100%: 강력매도"
        )

# ── Tab 5 ─────────────────────────────────────────────
with tab5:
    st.subheader("금융 섹터 — ROE 기반 분석")
    st.caption("금융주(은행·증권·보험)는 PER 기반 분석이 부적합하여 ROE 지표로 별도 분석합니다.")

    with st.expander("📖 금융주를 별도 분석하는 이유"):
        st.markdown("""
- 금융주는 **레버리지(부채)로 수익을 창출**하는 구조라 PER이 다른 섹터와 비교 불가
- 대신 **ROE(자기자본이익률)** 가 핵심 지표: 자본 대비 얼마나 효율적으로 수익을 내는지
- ROE가 높을수록 자본 활용 효율이 좋은 금융주
""")

    if df_fin.empty:
        st.warning("finance_roe.csv 파일이 없습니다.")
    else:
        df_fin_show = df_fin[["Name", "Market", "ROE_pct", "EPS", "op_income", "equity"]].copy()
        df_fin_show.columns = ["종목명", "시장", "ROE(%)", "EPS(원)", "영업이익", "자기자본"]
        df_fin_show["ROE(%)"]   = df_fin_show["ROE(%)"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        df_fin_show["EPS(원)"]  = df_fin_show["EPS(원)"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
        df_fin_show["영업이익"] = df_fin["op_income"].apply(lambda x: f"{x/1e8:,.0f}억원" if pd.notna(x) else "N/A")
        df_fin_show["자기자본"] = df_fin["equity"].apply(lambda x: f"{x/1e8:,.0f}억원" if pd.notna(x) else "N/A")
        st.dataframe(df_fin_show, use_container_width=True, hide_index=True)

        fig_roe = px.bar(
            df_fin.sort_values("ROE_pct", ascending=False),
            x="Name", y="ROE_pct",
            color="ROE_pct",
            color_continuous_scale=["#888", "#5B8DEF"],
            title="금융 섹터 ROE 비교 (%)",
            labels={"ROE_pct": "ROE (%)", "Name": "종목명"},
            text=df_fin.sort_values("ROE_pct", ascending=False)["ROE_pct"].apply(lambda x: f"{x:.1f}%")
        )
        fig_roe.update_traces(textposition="outside")
        fig_roe.update_layout(
            template="plotly_dark", height=450,
            coloraxis_showscale=False,
            xaxis_tickangle=-45, yaxis_title="ROE (%)"
        )
        st.plotly_chart(fig_roe, use_container_width=True)

# ── Tab 6: 업데이트 내역 ──────────────────────────────
with tab6:
    st.subheader("📋 업데이트 내역")

    st.markdown("""
### v1.0 — 2026.03.28

**🚀 배포 개요**
- KOSPI200 + KOSDAQ100 (~300개) 대상 PER 기반 괴리율 분석 대시보드
- DART Open API 연간 EPS 수집 + 분기 TTM YoY 성장률 반영
- 최종 저평가 스크리닝 26개 종목 산출
- Streamlit Cloud 배포

---

**1탭 — 저평가 스크리닝**
- 저평가 TOP 10 세로 막대그래프 (시그널별 색상 + 범례 설명)
- 섹터별 저평가 TOP 3 카드 형태 (3열 그리드)
- 시그널 드롭다운 필터 (DEFAULT: 강력매수, 색상 이모지 포함)
- 테이블 시그널 컬럼 폰트 색상 적용 + 전체 왼쪽 정렬 통일
- PER 소수점 1자리 반올림
- 전체 종목 괴리율 버블차트 (-15% 기준선 표시)
- 시그널 기준 설명 expander

**2탭 — 괴리율 분석**
- 기본괴리율(연간 EPS) / 조정괴리율(YoY 반영) 명칭 정립
- 기본 vs 조정 전체 136개 비교 막대그래프
- 괴리율 조정폭 TOP 15 차트
- 시그널 변화 히트맵 (조정 전 → 후)
- 섹터별 평균 조정괴리율 수치 직접 표시 + 컬러스케일 바

**3탭 — YoY 성장률**
- 히스토그램 구간별 count 직접 표시
- YoY vs 시장 조정괴리율 산점도 (시그널별 색상)

**4탭 — 종목 상세**
- 재무데이터 xxx,xxx억원 포맷 적용
- 평균 조정괴리율 게이지 차트 (시장·섹터 개별 수치 보조 표시)

**5탭 — 금융 섹터**
- PER 부적합 금융주 별도 ROE 기반 분석
- 정제된 테이블 (ROE%, 영업이익, 자기자본 억원 포맷)
- ROE 막대그래프 수치 직접 표시

**공통**
- 용어 전면 통일: 시장 조정괴리율 / 섹터 조정괴리율 / 기본괴리율
- 상단 지표 5개 + 부연 설명 (help 툴팁 + 캡션)
- 용어 설명 expander (괴리율, TTM, PER, ROE 등)
- 금융주 별도 분석 이유 설명 expander

---

> 💡 **향후 계획**
>
> **데이터 자동화**
> - DART 2025 사업보고서 자동 감지 및 동기화
>   (2026년 3~4월 공시 시점 기준, 일 1회 DART API 체크 →
>   신규 공시 감지 시 자동 수집·갱신)
> - 현재가 실시간 수집 + 수집 날짜 자동 표시
>
> **파이프라인 자동화**
> - Airflow DAG 구성: DART 수집 → EPS 계산 → 괴리율 산출 → 대시보드 갱신
> - Astronomer.io 클라우드 Airflow로 브라우저 기반 스케줄링
>
> **분석 고도화**
> - 백테스팅: DART 공시일 + 5영업일 기준 수익률 검증
> - ML 피처 중요도 분석 (Random Forest + SHAP)
> - Snowflake / BigQuery 연동으로 CSV → 클라우드 DB 전환
""")

st.divider()
st.caption("📌 데이터 기준: DART 2024 연간 재무제표 | TTM(최근 12개월) EPS 기준 YoY 성장률 | 분석 목적용, 투자 권유 아님")

with tab7:
    st.subheader("📉 과거 데이터 분석", "🤖 AI 챗봇")
    st.caption("기준일: 2025-03-30 | 2024 연간 재무제표 기준 | 분석 목적용, 투자 권유 아님")

    # ── 데이터 로드 ───────────────────────────────────────
    @st.cache_data
    def load_backtest():
        bt  = pd.read_csv("data/output/backtest_result.csv", dtype={"Code": str})
        rf  = pd.read_csv("data/output/rf_feature_importance.csv")
        shp = pd.read_csv("data/output/shap_importance.csv")
        return bt, rf, shp

    try:
        df_bt, df_rf, df_shap = load_backtest()
    except:
        st.error("백테스팅 데이터를 찾을 수 없습니다. data/output/ 폴더를 확인해주세요.")
        st.stop()

    # ── 상단 요약 지표 ────────────────────────────────────
    strong_buy_ret = df_bt[df_bt["signal_v2"] == "강력매수"]["ret_B_12m"].mean()
    kospi_ret      = 112.6
    alpha          = strong_buy_ret - kospi_ret

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("기준일",        "2025-03-30")
    m2.metric("분석 종목",     f"{len(df_bt)}개")
    m3.metric("강력매수 12M",  f"{strong_buy_ret:.1f}%",
              help="2025.03.30 기준 강력매수 신호 종목 평균 수익률")
    m4.metric("vs KOSPI 알파", f"+{alpha:.1f}%",
              delta=f"+{alpha:.1f}%",
              help="KOSPI 12개월 수익률 +112.6% 대비 초과수익")

    st.divider()

    # ── 섹션 1: 백테스팅 결과 ─────────────────────────────
    st.markdown("### 📊 백테스팅 결과")

    col_left, col_right = st.columns(2)

    with col_left:
        # 시그널별 수익률 비교 (막대)
        signal_order = ["강력매수", "매수", "중립", "매도", "강력매도"]
        signal_colors = {
            "강력매수": "#5B8DEF", "매수": "#1D9E75",
            "중립": "#888888", "매도": "#EF9F27", "강력매도": "#E24B4A"
        }
        periods = ["ret_B_3m", "ret_B_6m", "ret_B_9m", "ret_B_12m"]
        period_labels = ["3개월", "6개월", "9개월", "12개월"]

        fig_bar = go.Figure()
        for signal in signal_order:
            grp = df_bt[df_bt["signal_v2"] == signal]
            if len(grp) == 0:
                continue
            vals = [grp[p].mean() for p in periods]
            fig_bar.add_trace(go.Bar(
                name=signal,
                x=period_labels,
                y=vals,
                marker_color=signal_colors[signal],
                opacity=0.85,
                text=[f"{v:.1f}%" for v in vals],
                textposition="outside"
            ))

        fig_bar.update_layout(
            title="시그널 그룹별 평균 수익률",
            barmode="group",
            template="plotly_dark",
            height=400,
            yaxis_title="수익률 (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        # 벤치마크 대비 알파
        bm_names = ["KOSPI", "KOSDAQ", "KRX 가중", "기준금리", "CD 91일", "미국 10년물"]
        bm_rets  = [112.6, 64.5, 105.4, 2.8, 3.1, 4.2]
        alphas   = [strong_buy_ret - r for r in bm_rets]

        fig_alpha = go.Figure()
        fig_alpha.add_trace(go.Bar(
            x=bm_names, y=bm_rets,
            name="벤치마크",
            marker_color="#555555", opacity=0.7
        ))
        fig_alpha.add_hline(
            y=strong_buy_ret,
            line_color="#5B8DEF", line_width=2.5,
            line_dash="dash",
            annotation_text=f"강력매수 {strong_buy_ret:.1f}%",
            annotation_position="top right"
        )
        fig_alpha.update_layout(
            title="강력매수 vs 벤치마크 (12개월)",
            template="plotly_dark",
            height=400,
            yaxis_title="수익률 (%)"
        )
        st.plotly_chart(fig_alpha, use_container_width=True)

    # 가설검정 결과 + 산점도
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown("**📋 가설검정 결과 요약**")
        st.markdown("""
| 검정 | 결과 | 해석 |
|------|------|------|
| Pearson r (12M) | -0.156 | 방향성 존재, 유의하지 않음 |
| p값 | 0.070 | H0 기각 불가 (p > 0.05) |
| ANOVA (12M) | p < 0.0001 | ✅ 그룹 간 차이 유의 |
""")
        st.caption("""
**H0:** 괴리율과 수익률 간 상관관계 없음  
**결론:** 괴리율 단독 예측력은 약하나, 시그널 분류 효과는 통계적으로 유의
""")

    with col_r2:
        # 괴리율 vs 수익률 산점도
        fig_scatter = go.Figure()
        for signal in signal_order:
            grp = df_bt[df_bt["signal_v2"] == signal]
            if len(grp) == 0:
                continue
            fig_scatter.add_trace(go.Scatter(
                x=grp["gap_market_B"],
                y=grp["ret_B_12m"],
                mode="markers",
                name=signal,
                marker=dict(
                    color=signal_colors[signal],
                    size=8, opacity=0.75
                ),
                text=grp["Name"],
                hovertemplate="%{text}<br>괴리율: %{x:.3f}<br>수익률: %{y:.1f}%"
            ))
        fig_scatter.update_layout(
            title="괴리율 vs 12개월 수익률 (r = -0.156)",
            template="plotly_dark",
            height=350,
            xaxis_title="시장 괴리율",
            yaxis_title="12개월 수익률 (%)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # ── 섹션 2: ML 피처 중요도 ────────────────────────────
    st.markdown("### 🤖 ML 피처 중요도 분석")
    st.caption("Random Forest (n=97) + SHAP | CV R² = -0.131 (과적합) → 피처 중요도 해석에 집중")

    col_ml1, col_ml2 = st.columns(2)

    FEATURE_KO = {
        "yoy_growth_pct": "YoY 성장률",
        "gap_sector_B":   "섹터 괴리율",
        "sector_per_B":   "섹터 PER",
        "EPS":            "EPS",
        "debt_ratio":     "부채비율",
        "gap_market_B":   "시장 괴리율",
        "per_B":          "PER"
    }

    with col_ml1:
        df_rf["feature_ko"] = df_rf["feature"].map(FEATURE_KO)
        df_rf_sorted = df_rf.sort_values("importance")
        colors_rf = ["#5B8DEF" if i == len(df_rf_sorted)-1
                     else "#aaaaaa"
                     for i in range(len(df_rf_sorted))]
        fig_rf = go.Figure(go.Bar(
            x=df_rf_sorted["importance"],
            y=df_rf_sorted["feature_ko"],
            orientation="h",
            marker_color=colors_rf,
            text=[f"{v:.1%}" for v in df_rf_sorted["importance"]],
            textposition="outside"
        ))
        fig_rf.update_layout(
            title="Random Forest 피처 중요도",
            template="plotly_dark",
            height=350,
            xaxis_title="Importance"
        )
        st.plotly_chart(fig_rf, use_container_width=True)

    with col_ml2:
        df_shap["feature_ko"] = df_shap["feature"].map(FEATURE_KO)
        df_shap_sorted = df_shap.sort_values("mean_shap")
        colors_shap = ["#5B8DEF" if i == len(df_shap_sorted)-1
                       else "#aaaaaa"
                       for i in range(len(df_shap_sorted))]
        fig_shap = go.Figure(go.Bar(
            x=df_shap_sorted["mean_shap"],
            y=df_shap_sorted["feature_ko"],
            orientation="h",
            marker_color=colors_shap,
            text=[f"{v:.2f}" for v in df_shap_sorted["mean_shap"]],
            textposition="outside"
        ))
        fig_shap.update_layout(
            title="SHAP Mean |value|",
            template="plotly_dark",
            height=350,
            xaxis_title="Mean |SHAP value|"
        )
        st.plotly_chart(fig_shap, use_container_width=True)

    # 인사이트 박스
    st.info("""
**💡 ML 분석 주요 인사이트**

- **YoY 성장률**이 수익률 예측에 가장 큰 영향 (27.5%)
- **섹터 괴리율**이 시장 괴리율보다 중요 → 섹터 내 상대 비교가 더 유효한 신호
- 괴리율 단독보다 **YoY + 섹터 조합**이 더 강한 예측력 보유
- 향후 개선 방향: YoY 성장률 가중치 강화, 섹터 조정괴리율 기준 고도화
""")

    with st.expander("⚠️ 분석 한계 및 주의사항"):
        st.markdown("""
- 백테스팅 기간: 단일 연도 (2025-03-30 ~ 2026-03-28)
- 2025~2026년은 반도체/AI 붐으로 인한 대세 상승장 (KOSPI +112%)
- 하락장·횡보장에서의 별도 검증 필요
- ML 모델 CV R² = -0.131 → 수익률 예측보다 피처 중요도 해석 목적
- 본 분석은 포트폴리오 목적이며 투자 권유가 아님
""")

with tab8:
    st.subheader("🤖 AI 종목 분석 챗봇")
    st.caption("KOSPI200 + KOSDAQ100 괴리율 데이터 기반 | Groq AI (LLaMA3) | 무료 공개")

    # ── Groq API 설정 ─────────────────────────────────
    import requests as req

    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

    if not GROQ_API_KEY:
        st.warning("⚠️ Groq API 키가 설정되지 않았습니다. Streamlit Secrets에 GROQ_API_KEY를 추가해주세요.")
        st.stop()

    # ── 데이터 컨텍스트 준비 ──────────────────────────
    def get_stock_context(query: str) -> str:
        """쿼리에서 종목명 추출 후 데이터 컨텍스트 생성"""
        context_rows = []

        # 종목명 매칭
        for _, row in df_v2.iterrows():
            if row["Name"] in query:
                context_rows.append(row)
                break

        # 종목명 없으면 강력매수 상위 5개
        if not context_rows:
            top5 = df_v2[df_v2["signal_v2"] == "강력매수"].head(5)
            for _, row in top5.iterrows():
                context_rows.append(row)

        context = f"""
현재 분석 데이터 (기준일: {df_v2["updated_at"].iloc[0] if "updated_at" in df_v2.columns else "N/A"}):
- 분석 대상: {len(df_v2)}개 종목 (KOSPI200 + KOSDAQ100)
- 저평가 종목: {len(df_final)}개
- 시그널 분포: {df_v2["signal_v2"].value_counts().to_dict()}

관련 종목 상세:
"""
        for row in context_rows:
            context += f"""
종목명: {row["Name"]} ({row.get("Sector", "N/A")})
- 시그널: {row["signal_v2"]}
- 시장 조정괴리율: {row["gap_market_v2"]*100:.1f}%
- 섹터 조정괴리율: {row["gap_sector_v2"]*100:.1f}%
- PER: {row["PER"]:.1f}
- YoY 성장률: {f"{row['yoy_growth_pct']:.1f}%" if pd.notna(row.get("yoy_growth_pct")) else "N/A"}
- 부채비율: {f"{row['debt_ratio']:.1f}%" if pd.notna(row.get("debt_ratio")) else "N/A"}
- 현재가: {f"{int(row['price']):,}원" if pd.notna(row.get("price")) else "N/A"}
"""
        return context

    def ask_groq(question: str, context: str) -> str:
        """Groq API 호출"""
        system_prompt = """당신은 한국 주식 시장 전문 AI 분석가입니다.
PER 기반 괴리율 분석 데이터를 바탕으로 종목을 분석합니다.
항상 한국어로 답변하고, 데이터 기반으로 설명합니다.
마지막에 반드시 "본 분석은 투자 권유가 아니며 참고용입니다." 라고 명시합니다."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{context}\n\n질문: {question}"}
        ]

        try:
            response = req.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-70b-8192",
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.3
                },
                timeout=30
            )
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"오류가 발생했습니다: {str(e)}"

    # ── FAQ 섹션 ──────────────────────────────────────
    st.markdown("### 📌 자주 묻는 질문")
    st.caption("버튼 클릭 시 즉시 답변 (API 호출 없음)")

    faq_cols = st.columns(3)
    faq_keys = list(FAQ.keys())
    for i, key in enumerate(faq_keys):
        with faq_cols[i % 3]:
            if st.button(key, key=f"faq_{i}", use_container_width=True):
                st.session_state["faq_answer"] = FAQ[key]
                st.session_state["faq_question"] = key

    if "faq_answer" in st.session_state:
        st.markdown(f"**Q. {st.session_state['faq_question']}**")
        st.markdown(st.session_state["faq_answer"])

    st.divider()

    # ── 자유 질문 ─────────────────────────────────────
    st.markdown("### 💬 AI 자유 질문")
    st.caption("종목명 포함 시 해당 종목 데이터 기반으로 답변합니다")

    # 대화 히스토리
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # 이전 대화 표시
    for chat in st.session_state["chat_history"]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # 질문 입력
    if prompt := st.chat_input("예: 삼성전자 왜 강력매수야? / 저평가 종목 추천해줘"):
        # 사용자 메시지
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 답변
        with st.chat_message("assistant"):
            with st.spinner("분석 중..."):
                context = get_stock_context(prompt)
                answer  = ask_groq(prompt, context)
            st.markdown(answer)
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": answer}
            )

    # 대화 초기화
    if st.button("🗑️ 대화 초기화"):
        st.session_state["chat_history"] = []
        st.rerun()
