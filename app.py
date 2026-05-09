import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="수원화성문화제 성과 대시보드", layout="wide", page_icon="🏯")

NAVY = "#1a2744"
BLUE = "#185FA5"
BLUE_L = "#B5D4F4"
TEAL = "#0F6E56"
AMBER = "#854F0B"
AMBER_L = "#FAC775"
RED = "#A32D2D"
RED_L = "#F7C1C1"
GREEN = "#3B6D11"
GREEN_L = "#C0DD97"
GRAY = "#888780"
GRAY_L = "#D3D1C7"
ACCENT = "#EF9F27"
PURPLE = "#7F47B2"
PURPLE_L = "#C9A5E8"
MAGENTA = "#C2185B"
MAGENTA_L = "#F48FB1"

st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; max-width: 1200px; }
    div[data-testid="stMetric"] { background: #f8f7f4; border-radius: 10px; padding: 12px 16px; border: 1px solid #e8e6e1; }
    div[data-testid="stMetric"] label { font-size: 12px !important; }
    h1, h2, h3 { color: #1a2744; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 20px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 데이터 로드
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    from pathlib import Path
    BASE = Path(__file__).parent
    
    kpi = pd.read_csv(BASE / "01_축제_관광소비_KPI.csv", encoding='utf-8-sig')
    monthly = pd.read_csv(BASE / "02_팔달구_월별_관광총소비.csv", encoding='utf-8-sig')
    yearly = pd.read_csv(BASE / "03_팔달구_연간_관광소비_요약.csv", encoding='utf-8-sig')
    oct_cat = pd.read_csv(BASE / "04_10월_업종별_관광소비.csv", encoding='utf-8-sig')
    compare = pd.read_csv(BASE / "05_KPI_실제금액_대조.csv", encoding='utf-8-sig')
    
    kpi_full = pd.read_csv(BASE / "수원화성문화제_문화관광축제_주요_지표.csv", encoding='utf-8-sig')
    local_full = pd.read_csv(BASE / "수원시팔달구_관광소비_전체_202001-202512.csv", encoding='utf-8-sig')
    
    return kpi, monthly, yearly, oct_cat, compare, kpi_full, local_full

kpi, monthly, yearly, oct_cat, compare, kpi_full, local_full = load_data()

# ──────────────────────────────────────────────
# 파생 데이터
# ──────────────────────────────────────────────
# FSI 데이터
fsi_data = pd.DataFrame({
    '연도': [2018, 2019, 2022, 2023, 2024, 2025],
    'FSI': [57.2, 84.0, 53.6, 84.8, 74.0, 77.6],
    'FSI_등급': ['C', 'A', 'C', 'A', 'B', 'A'],
    '축제기간_일': [3, 4, 3, 3, 3, 8],
    '총방문자': [173238, 248223, 198550, 259054, 248819, 567010],
    '일평균': [57746, 62056, 66183, 86351, 82940, 70876],
    'FPI': [60.9, 75.04, 64.5, 77.5, 73.06, 64.26],
    'FLI': [13.45, 36.29, 8.95, 42.41, 31.73, 21.06],
    '방문자_점수': [17, 22, 14, 19, 13, 25],
    'FPI_점수': [12, 17, 13, 18, 16, 13],
    'FLI_점수': [5, 15, 3, 18, 13, 8],
    '유입력_점수': [10, 15, 13, 15, 15, 12],
    '소비_점수': [13, 15, 11, 15, 17, 20],
})
fsi_data['핵심3일환산'] = fsi_data['일평균'] * 3
fsi_data['기간확대효과'] = fsi_data['총방문자'] - fsi_data['핵심3일환산']
fsi_data['1인당소비_만원'] = [None, None, 5.4, 4.2, 4.4, 5.0]

# KPI 히트맵 데이터
kpi_heatmap = kpi_full.pivot_table(index='구분명', columns=['개최년도'], values='지표값')
kpi_heatmap = kpi_heatmap.reindex(['현지인방문자 유입', '축제지 집중률', '외부방문자 유입', '내비게이션 검색량', '관광소비'])
fest_kpi = kpi_full[kpi_full['그룹명'] == '축제기간'].pivot_table(index='구분명', columns='개최년도', values='지표값')

# CCI 데이터
cci_data = pd.DataFrame({
    '연도': [2019, 2020, 2021, 2022, 2023, 2024, 2025],
    '팔달구': [73, 72, 71, 73, 74, 75, 76],
    '전국평균': [68, 68, 68, 68, 68, 69, 69],
    'CCI_Gap': [5.42, 3.93, 3.66, 4.93, 5.61, 6.46, 6.75],
})

# 팔달구 월별 전처리
local_total = local_full[local_full['중분류'] == '관광총소비'].copy()
local_total['기준년월_int'] = local_total['기준년월'].astype(float).astype('Int64')
local_total = local_total[local_total['기준년월_int'].notna()].copy()
local_total['연도'] = (local_total['기준년월_int'] // 100).astype(int)
local_total['월'] = (local_total['기준년월_int'] % 100).astype(int)

# 업종별 대분류
cat_map = {
    '호텔': '숙박업', '캠핑장/펜션': '숙박업', '기타숙박': '숙박업',
    '여행업': '여행업', '렌터카': '운송업', '육상운송': '운송업',
    '대형쇼핑몰': '쇼핑업', '레저용품쇼핑': '쇼핑업', '기타관광쇼핑': '쇼핑업',
    '관광유원시설': '여가서비스업', '기타레저': '여가서비스업', '문화서비스': '여가서비스업', '골프장': '여가서비스업',
    '의료관광': '의료웰니스', '뷰티': '의료웰니스',
    '일반외식업': '식음료업', '제과음료업': '식음료업', '면세점': '쇼핑업',
}

# CV 데이터
cv_data = pd.DataFrame({
    '지표명': ['현지인방문자 유입', '축제지 집중률', '외부방문자 유입', '내비게이션 검색량', '관광소비'],
    'CV_퍼센트': [7.2, 10.8, 15.7, 22.4, 26.8],
})

# ──────────────────────────────────────────────
# 헤더
# ──────────────────────────────────────────────
st.markdown(f"""
<div style="background:{NAVY}; padding:20px 28px; border-radius:12px; border-bottom:4px solid {ACCENT}; margin-bottom:20px;">
    <div style="font-size:11px; color:{ACCENT}; letter-spacing:0.15em; font-weight:500;">DATA-DRIVEN FESTIVAL ANALYSIS</div>
    <div style="font-size:22px; font-weight:700; color:white; margin-top:4px;">수원화성문화제 성과 대시보드</div>
    <div style="font-size:12px; color:rgba(255,255,255,0.5); margin-top:4px;">공공데이터 기반 종합 분석 · 2018~2025 (6개 회차)</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 탭 구성
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 종합 성과", "🔥 KPI 히트맵", "👥 방문자 구조",
    "💰 관광소비 심층", "📈 검색·전환·경쟁력", "🏪 업종별 구조"
])

# ══════════════════════════════════════════════
# TAB 1: 종합 성과
# ══════════════════════════════════════════════
with tab1:
    st.subheader("2025 핵심 성과 스냅샷")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 방문자", "567,010명", "+127.9%")
    c2.metric("일평균 방문자", "70,876명", "-14.5%", delta_color="inverse")
    c3.metric("FPI 점수", "64.26", "-12.0%", delta_color="inverse")
    c4.metric("FLI 효과", "21.06%", "-33.6%", delta_color="inverse")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("##### FSI 등급 시계열")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=fsi_data['연도'].astype(str), y=fsi_data['방문자_점수'] + fsi_data['FPI_점수'] + fsi_data['FLI_점수'] + fsi_data['유입력_점수'] + fsi_data['소비_점수'], name='방문자 점수', marker_color=MAGENTA_L), secondary_y=True)
        fig.add_trace(go.Scatter(x=fsi_data['연도'].astype(str), y=fsi_data['FSI'], name='FSI', line=dict(color=PURPLE, width=3), mode='lines+markers'), secondary_y=False)
        fig.add_hline(y=80, line_dash="dash", line_color=TEAL, annotation_text="A등급", secondary_y=False)
        fig.add_hline(y=60, line_dash="dash", line_color=AMBER, annotation_text="B등급", secondary_y=False)
        fig.add_hline(y=50, line_dash="dash", line_color=RED, annotation_text="C등급", secondary_y=False)
        fig.update_layout(height=350, margin=dict(t=30, b=30), legend=dict(orientation="h", y=1.12))
        fig.update_yaxes(title_text="FSI", secondary_y=False)
        fig.update_yaxes(title_text="점수 합계", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        # 등급 테이블
        st.dataframe(
            fsi_data[['연도', 'FSI_등급', 'FSI']].set_index('연도'),
            use_container_width=True, height=250
        )

    with col_r:
        st.markdown("##### 방문자 vs FPI / FLI")
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(x=fsi_data['연도'].astype(str), y=fsi_data['총방문자'], name='총방문자', marker_color=BLUE_L), secondary_y=False)
        fig2.add_trace(go.Scatter(x=fsi_data['연도'].astype(str), y=fsi_data['FPI'], name='FPI', line=dict(color=ACCENT, width=3), mode='lines+markers+text', text=fsi_data['FPI'].round(1), textposition='top center', textfont=dict(size=10)), secondary_y=True)
        fig2.add_trace(go.Scatter(x=fsi_data['연도'].astype(str), y=fsi_data['FLI'], name='FLI', line=dict(color=GREEN, width=2, dash='dot'), mode='lines+markers+text', text=fsi_data['FLI'].round(1), textposition='bottom center', textfont=dict(size=10)), secondary_y=True)
        fig2.update_layout(height=350, margin=dict(t=30, b=30), legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("##### 8일 착시 분해")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(y=fsi_data['연도'].astype(str), x=fsi_data['핵심3일환산'], name='핵심3일 환산', orientation='h', marker_color=BLUE))
        fig3.add_trace(go.Bar(y=fsi_data['연도'].astype(str), x=fsi_data['기간확대효과'].clip(lower=0), name='기간확대 효과', orientation='h', marker_color=ACCENT))
        fig3.update_layout(barmode='stack', height=250, margin=dict(t=10, b=10), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 연도별 종합지표")
    st.dataframe(
        fsi_data[['연도', '축제기간_일', '총방문자', '일평균', 'FPI', 'FLI', 'FSI_등급', 'FSI']].set_index('연도'),
        use_container_width=True
    )

# ══════════════════════════════════════════════
# TAB 2: KPI 히트맵
# ══════════════════════════════════════════════
with tab2:
    st.subheader("축제기간 KPI 히트맵")

    fest_only = kpi_full[kpi_full['그룹명'] == '축제기간'].copy()
    hm = fest_only.pivot_table(index='구분명', columns='개최년도', values='지표값')
    hm = hm.reindex(['현지인방문자 유입', '축제지 집중률', '외부방문자 유입', '내비게이션 검색량', '관광소비'])

    fig_hm = px.imshow(
        hm.values, x=[str(c) for c in hm.columns], y=hm.index.tolist(),
        color_continuous_scale=[[0, '#f5f0ff'], [0.5, MAGENTA_L], [1, PURPLE]],
        text_auto='.2f', aspect='auto'
    )
    fig_hm.update_layout(height=300, margin=dict(t=20, b=20), coloraxis_colorbar=dict(title="KPI"))
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("---")
    st.subheader("축제 vs 비축제 비교")
    
    selected_year = st.selectbox("연도 선택", sorted(kpi_full['개최년도'].unique(), reverse=True), key='kpi_year')
    
    yr_data = kpi_full[kpi_full['개최년도'] == selected_year]
    fest_vals = yr_data[yr_data['그룹명'] == '축제기간'].set_index('구분명')['지표값']
    nfest_vals = yr_data[yr_data['그룹명'] == '비축제기간'].set_index('구분명')['지표값']
    
    indicators = ['현지인방문자 유입', '축제지 집중률', '외부방문자 유입', '내비게이션 검색량', '관광소비']
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(y=indicators, x=[fest_vals.get(i, 0) for i in indicators], name='축제기간', orientation='h', marker_color=BLUE))
    fig_comp.add_trace(go.Bar(y=indicators, x=[nfest_vals.get(i, 0) for i in indicators], name='비축제기간', orientation='h', marker_color=GRAY_L))
    fig_comp.update_layout(barmode='group', height=300, margin=dict(t=20, b=20, l=120), legend=dict(orientation="h", y=1.08), xaxis=dict(range=[0, 1]))
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")
    st.subheader("지표명별 변동계수(CV)")
    st.caption("CV가 높을수록 연도별 편차가 커서 지표 안정성이 낮음")
    
    fig_cv = go.Figure()
    fig_cv.add_trace(go.Bar(y=cv_data['지표명'], x=cv_data['CV_퍼센트'], orientation='h', marker_color=PURPLE_L))
    fig_cv.add_vline(x=15, line_dash="dash", line_color=GREEN, annotation_text="안정 기준")
    fig_cv.add_vline(x=25, line_dash="dash", line_color=RED, annotation_text="불안정 기준")
    fig_cv.update_layout(height=250, margin=dict(t=20, b=20, l=120), xaxis_title="CV (%)")
    st.plotly_chart(fig_cv, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 3: 방문자 구조
# ══════════════════════════════════════════════
with tab3:
    st.subheader("일평균 vs 총방문자")
    fig_daily = make_subplots(specs=[[{"secondary_y": True}]])
    fig_daily.add_trace(go.Bar(x=fsi_data['연도'].astype(str), y=fsi_data['총방문자'], name='총방문자', marker_color=BLUE_L), secondary_y=False)
    fig_daily.add_trace(go.Scatter(x=fsi_data['연도'].astype(str), y=fsi_data['일평균'], name='일평균', line=dict(color=ACCENT, width=3), mode='lines+markers'), secondary_y=True)
    fig_daily.update_layout(height=320, margin=dict(t=30, b=20), legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig_daily, use_container_width=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("##### 방문자 및 1인당 추정소비")
        vis_data = fsi_data[fsi_data['1인당소비_만원'].notna()].copy()
        fig_spend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_spend.add_trace(go.Bar(x=vis_data['연도'].astype(str), y=vis_data['총방문자'], name='방문자', marker_color=PURPLE_L), secondary_y=False)
        fig_spend.add_trace(go.Scatter(x=vis_data['연도'].astype(str), y=vis_data['1인당소비_만원'], name='1인당 소비(만원)', line=dict(color=RED, width=3), mode='lines+markers+text', text=vis_data['1인당소비_만원'], textposition='top center'), secondary_y=True)
        fig_spend.update_layout(height=300, margin=dict(t=20, b=20), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_spend, use_container_width=True)

    with col_b:
        st.markdown("##### 연령대·성별 분포")
        age_data = pd.DataFrame({
            '연령대': ['0~9세', '10~19세', '20~29세', '30~39세', '40~49세', '50~59세', '60~69세', '70세 이상'],
            '남성': [0.3, 2.2, 8.1, 8.8, 8.1, 9.0, 8.4, 4.0],
            '여성': [0.4, 2.7, 11.2, 8.7, 7.4, 9.1, 7.7, 3.7],
        })
        fig_age = go.Figure()
        fig_age.add_trace(go.Bar(y=age_data['연령대'], x=-age_data['남성'], name='남성', orientation='h', marker_color=BLUE))
        fig_age.add_trace(go.Bar(y=age_data['연령대'], x=age_data['여성'], name='여성', orientation='h', marker_color=MAGENTA))
        fig_age.update_layout(barmode='overlay', height=300, margin=dict(t=20, b=20, l=80), xaxis=dict(tickvals=[-10,-5,0,5,10], ticktext=['10%','5%','0','5%','10%']), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_age, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 외국인 방문자 국가별 분포 (2025)")
    foreign = pd.DataFrame({
        '국가': ['중국', '일본', '대만', '인도', '미국', '필리핀', '베트남', '홍콩', '인도네시아', '기타'],
        '비율': [28.0, 12.1, 8.5, 5.9, 5.5, 4.0, 3.4, 3.3, 3.0, 26.3],
    })
    fig_foreign = px.bar(foreign, x='비율', y='국가', orientation='h', color_discrete_sequence=[TEAL])
    fig_foreign.update_layout(height=300, margin=dict(t=10, b=10, l=80), yaxis=dict(categoryorder='total ascending'), xaxis_title="비율 (%)")
    st.plotly_chart(fig_foreign, use_container_width=True)

    ca, cb, cc = st.columns(3)
    ca.metric("20~50대 비중", "70.4%", "핵심 관람층")
    cb.metric("MZ 세대(20~30대)", "36.8%", "SNS·체험형 타겟")
    cc.metric("외국인 비중", "1.11%", "성장 여지")

# ══════════════════════════════════════════════
# TAB 4: 관광소비 심층
# ══════════════════════════════════════════════
with tab4:
    st.subheader("KPI +72%의 실체")
    c1, c2, c3 = st.columns(3)
    c1.metric("축제기간 KPI", "0.659", "+72.1% (vs 2023)")
    c2.metric("비축제기간 KPI", "0.591", "+64.6% (vs 2023)")
    c3.metric("10월 실제소비", "1,131억원", "-9.9% (vs 2024)", delta_color="inverse")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("##### 축제기간 vs 비축제기간 관광소비 KPI")
        fig_kpi = go.Figure()
        fig_kpi.add_trace(go.Bar(x=kpi['연도'].astype(str), y=kpi['축제기간_KPI'], name='축제기간', marker_color=BLUE))
        fig_kpi.add_trace(go.Bar(x=kpi['연도'].astype(str), y=kpi['비축제기간_KPI'], name='비축제기간', marker_color=GRAY_L))
        fig_kpi.update_layout(barmode='group', height=300, margin=dict(t=20, b=20), yaxis=dict(range=[0, 0.8]), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_kpi, use_container_width=True)

    with col_r:
        st.markdown("##### 축제기간 리프트 효과 (%)")
        fig_lift = px.line(kpi, x=kpi['연도'].astype(str), y='리프트_퍼센트', markers=True, color_discrete_sequence=[TEAL])
        fig_lift.update_layout(height=300, margin=dict(t=20, b=20), yaxis=dict(range=[0, 15]))
        st.plotly_chart(fig_lift, use_container_width=True)

    st.warning("⚠️ 비축제기간 KPI도 +69% 급등 → KPI 상승의 대부분은 정규화 기저 변화. 축제 효과로 단정 불가.", icon="⚠️")

    st.markdown("---")
    st.markdown("##### 2025년 월별 전년대비 관광소비 증감률")
    m2025 = monthly[monthly['연도'] == 2025].copy()
    m2025['색상'] = m2025.apply(lambda r: '축제월' if r['축제월여부'] == 'Y' else ('증가' if r['전년대비_증감률'] >= 0 else '감소'), axis=1)
    color_map = {'축제월': RED, '증가': GREEN, '감소': GRAY_L}
    fig_monthly = px.bar(m2025, x=m2025['월'].astype(str) + '월', y='전년대비_증감률', color='색상', color_discrete_map=color_map, text='전년대비_증감률')
    fig_monthly.update_traces(texttemplate='%{text:.1f}%', textposition='outside', textfont_size=10)
    fig_monthly.update_layout(height=350, margin=dict(t=20, b=20), showlegend=True, legend=dict(orientation="h", y=1.08), yaxis_title="증감률 (%)", xaxis_title="")
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.error("🔴 축제월(9·10월)이 −9.9%로 12개월 중 최대 하락. 축제 기간 확대가 소비 증가로 이어지지 않음.")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("##### 10월 실제 관광소비 추이 (억원)")
        oct_real = pd.DataFrame({
            '연도': ['2020', '2021', '2022', '2023', '2024', '2025'],
            '소비': [1071, 1049, 1305, 1172, 1255, 1131],
        })
        colors = [AMBER]*5 + [RED]
        fig_oct = go.Figure(go.Bar(x=oct_real['연도'], y=oct_real['소비'], marker_color=colors, text=oct_real['소비'], textposition='outside'))
        fig_oct.update_layout(height=280, margin=dict(t=20, b=20), yaxis=dict(range=[900, 1400]))
        st.plotly_chart(fig_oct, use_container_width=True)

    with col_b:
        st.markdown("##### 축제월 vs 비축제월 구조 비교")
        fig_struct = go.Figure()
        fig_struct.add_trace(go.Bar(x=yearly['연도'].astype(str), y=yearly['비축제월_소비_억원'], name='비축제월', marker_color=GRAY_L))
        fig_struct.add_trace(go.Bar(x=yearly['연도'].astype(str), y=yearly['축제월_소비_억원'], name='축제월(9~10월)', marker_color=ACCENT))
        fig_struct.update_layout(barmode='stack', height=280, margin=dict(t=20, b=20), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_struct, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 축제월 vs 비축제월 증감률 비교")
    yr_with = yearly[yearly['축제월_전년대비'].notna()].copy()
    fig_yoy = make_subplots(specs=[[{"secondary_y": True}]])
    fig_yoy.add_trace(go.Bar(x=yr_with['연도'].astype(str), y=yr_with['연간_총소비_억원'], name='연간 총소비(억원)', marker_color=BLUE_L), secondary_y=False)
    fig_yoy.add_trace(go.Scatter(x=yr_with['연도'].astype(str), y=yr_with['축제월_전년대비'], name='축제월 증감률', line=dict(color=RED, width=3), mode='lines+markers'), secondary_y=True)
    fig_yoy.add_trace(go.Scatter(x=yr_with['연도'].astype(str), y=yr_with['비축제월_전년대비'], name='비축제월 증감률', line=dict(color=GRAY, width=2, dash='dot'), mode='lines+markers'), secondary_y=True)
    fig_yoy.add_hline(y=0, line_dash="dash", line_color=GRAY, secondary_y=True)
    fig_yoy.update_layout(height=300, margin=dict(t=20, b=20), legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig_yoy, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5: 검색·전환·경쟁력
# ══════════════════════════════════════════════
with tab5:
    st.subheader("검색 수요 분리 해석")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("##### 팔달구 관광경쟁력(CCI) — 전국평균 대비 우위")
        fig_cci = make_subplots(specs=[[{"secondary_y": True}]])
        fig_cci.add_trace(go.Scatter(x=cci_data['연도'].astype(str), y=cci_data['팔달구'], name='팔달구', line=dict(color=PURPLE, width=2), mode='lines+markers'), secondary_y=False)
        fig_cci.add_trace(go.Scatter(x=cci_data['연도'].astype(str), y=cci_data['전국평균'], name='전국평균', line=dict(color=GRAY, width=1, dash='dot'), mode='lines'), secondary_y=False)
        fig_cci.add_trace(go.Bar(x=cci_data['연도'].astype(str), y=cci_data['CCI_Gap'], name='CCI Gap', marker_color=PURPLE_L, opacity=0.5), secondary_y=True)
        fig_cci.update_layout(height=300, margin=dict(t=20, b=20), legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_cci, use_container_width=True)

    with col_r:
        st.markdown("##### 월별 방문자·검색 시계열")
        monthly_vis = local_total[['연도', '월', '소비액(천원)']].copy()
        monthly_vis['연월'] = monthly_vis['연도'].astype(str) + '-' + monthly_vis['월'].astype(str).str.zfill(2)
        monthly_vis['소비_억원'] = monthly_vis['소비액(천원)'] / 1e5
        fig_ts = px.line(monthly_vis, x='연월', y='소비_억원', color_discrete_sequence=[PURPLE])
        fig_ts.update_layout(height=300, margin=dict(t=20, b=20), xaxis=dict(dtick=6), yaxis_title="관광소비 (억원)")
        st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 연도별 10월(축제월) 검색건수")
    search_data = pd.DataFrame({
        '연도': ['2020', '2021', '2022', '2023', '2024', '2025'],
        '10월_검색': [225, 293, 375, 373, 304, 423],
    })
    fig_search = px.bar(search_data, x='연도', y='10월_검색', color_discrete_sequence=[AMBER_L], text='10월_검색')
    colors_s = [AMBER_L]*5 + [RED_L]
    fig_search.update_traces(marker_color=colors_s, textposition='outside')
    fig_search.update_layout(height=280, margin=dict(t=20, b=20), yaxis_title="검색건수 (만)")
    st.plotly_chart(fig_search, use_container_width=True)

    st.info("💡 연간 검색은 약화(395만→325만, −17.7%) / 10월 축제월 검색은 오히려 최고치(423) → '연간 관심 약화 vs 축제월 집중'으로 분리 해석 필요")

    st.markdown("---")
    st.markdown("##### 10월 성과 종합 테이블")
    perf = pd.DataFrame({
        '연도': [2021, 2022, 2023, 2024, 2025],
        '검색건수': [293142, 375276, 373362, 304450, 423800],
        '전체방문자': [7812532, 9341588, 9629025, 10313233, 10656429],
        '검색대비방문전환율': [26.65, 24.89, 25.79, 33.88, 25.15],
        '1인당평균소비_원': [13424, 13964, 12174, 12170, 10615],
    })
    st.dataframe(perf.set_index('연도'), use_container_width=True)

# ══════════════════════════════════════════════
# TAB 6: 업종별 구조
# ══════════════════════════════════════════════
with tab6:
    st.subheader("10월 업종별 소비 구조")

    year_sel = st.selectbox("연도 선택", sorted(oct_cat['연도'].unique(), reverse=True), key='oct_year')
    oct_yr = oct_cat[oct_cat['연도'] == year_sel].copy()

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("##### 중분류별 전년대비 증감률 (%)")
        oct_sorted = oct_yr.sort_values('전년대비_증감률', ascending=True)
        colors_bar = [GREEN if v >= 0 else RED for v in oct_sorted['전년대비_증감률']]
        fig_cat = go.Figure(go.Bar(
            y=oct_sorted['중분류'], x=oct_sorted['전년대비_증감률'],
            orientation='h', marker_color=colors_bar,
            text=oct_sorted['전년대비_증감률'].apply(lambda v: f"{v:+.1f}%"),
            textposition='outside', textfont_size=10
        ))
        fig_cat.add_vline(x=0, line_color=GRAY)
        fig_cat.update_layout(height=max(350, len(oct_sorted)*28), margin=dict(t=10, b=10, l=100))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        st.markdown("##### 대분류별 소비 규모 (억원)")
        group_sum = oct_yr.groupby('대분류')['소비액_억원'].sum().reset_index().sort_values('소비액_억원', ascending=False)
        fig_tree = px.treemap(oct_yr, path=['대분류', '중분류'], values='소비액_억원', color='전년대비_증감률',
                              color_continuous_scale=[[0, RED_L], [0.5, '#f5f5f5'], [1, GREEN_L]],
                              color_continuous_midpoint=0)
        fig_tree.update_layout(height=400, margin=dict(t=10, b=10))
        st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 대분류별 지출 비율 추이")
    
    local_cat = local_full[(local_full['분석유형'] == '업종별 지출액') & (local_full['대분류'].notna())].copy()
    local_cat['기준년월_int'] = local_cat['기준년월'].astype(float).astype('Int64')
    local_cat = local_cat[local_cat['기준년월_int'].notna()]
    local_cat['연도'] = (local_cat['기준년월_int'] // 100).astype(int)
    
    cat_yearly = local_cat.groupby(['연도', '대분류'])['소비액(천원)'].sum().reset_index()
    cat_total = cat_yearly.groupby('연도')['소비액(천원)'].sum().reset_index()
    cat_total.columns = ['연도', '총합']
    cat_yearly = cat_yearly.merge(cat_total, on='연도')
    cat_yearly['비율'] = (cat_yearly['소비액(천원)'] / cat_yearly['총합'] * 100).round(1)

    cat_colors = {'쇼핑업': BLUE, '식음료업': PURPLE_L, '의료웰니스업': GREEN_L, '운송업': BLUE_L, '여가서비스업': AMBER_L, '숙박업': MAGENTA_L, '여행업': RED_L}
    fig_area = px.area(cat_yearly, x='연도', y='비율', color='대분류', color_discrete_map=cat_colors)
    fig_area.update_layout(height=350, margin=dict(t=20, b=20), legend=dict(orientation="h", y=1.12), yaxis_title="비율 (%)")
    st.plotly_chart(fig_area, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 업종별 상세 테이블")
    st.dataframe(
        oct_yr[['대분류', '중분류', '소비액_억원', '전년대비_증감률']].sort_values('소비액_억원', ascending=False).reset_index(drop=True),
        use_container_width=True, height=400
    )

# ──────────────────────────────────────────────
# 푸터
# ──────────────────────────────────────────────
st.markdown("---")
st.caption("데이터: 한국관광 데이터랩 (축제기간 KPI) · 수원시 팔달구 관광소비 월별 데이터 (2020~2025) · 2025 문화관광축제 종합평가보고서")
