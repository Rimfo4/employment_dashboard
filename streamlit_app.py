import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from streamlit_lottie import st_lottie
import time

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="기후변화와 취업 보고서",
    page_icon="🌍",
    layout="wide",
)

# --- 안정성을 높인 Lottie 로딩 함수 ---
@st.cache_data(ttl=3600) # 1시간 동안 데이터 캐시
def load_lottieurl(url: str):
    """재시도 기능이 포함된 안정적인 Lottie 애니메이션 데이터 로딩 함수"""
    for _ in range(3): # 최대 3번 재시도
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.json()
        except requests.exceptions.RequestException as e:
            time.sleep(1) # 재시도 전 1초 대기
    return None # 모든 재시도 실패 시 None 반환

# --- 부드러운 스크롤 애니메이션을 위한 CSS ---
st.markdown("""
<style>
h1, h2, h3 {
    opacity: 0;
    animation: fadeIn 1s ease-in-out forwards;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# --- 데이터 로딩 (캐싱) ---
@st.cache_data
def get_report_data():
    """보고서를 위한 시계열 예시 데이터를 생성합니다."""
    data = []
    # 참고: 2025년 9월 16일 현재, 2030년은 미래 데이터입니다.
    # 앱의 로직상 미래 데이터는 필터링되므로, 여기서는 예시로만 포함합니다.
    for year in [2020, 2024, 2025]:
        data.extend([
            {'연도': year, '유형': '신재생에너지', '증감률': 12 + (year - 2020) * 1.8, '구분': '성장'},
            {'연도': year, '유형': '전기차 생산', '증감률': 10 + (year - 2020) * 1.5, '구분': '성장'},
            {'연도': year, '유형': '화력발전', '증감률': -9 - (year - 2020) * 1.2, '구분': '감소'},
            {'연도': year, '유형': '석유화학', '증감률': -7 - (year - 2020) * 1.0, '구분': '감소'},
            {'연도': year, '전공': '친환경·에너지', '취업률': 70 + (year - 2020) * 0.9},
            {'연도': year, '전공': '전체 평균', '취업률': 67 + (year - 2020) * 0.1}
        ])
    return pd.DataFrame(data)

# --- Plotly 그래프 폰트 설정 ---
def plot_with_font(fig):
    fig.update_layout(font_family="Pretendard") # Pretendard 폰트가 없으면 기본 폰트 사용
    return fig

# =====================================================================================
# 메인 대시보드 (싱글 페이지 스크롤)
# =====================================================================================
st.title("기후를 신경쓰면 취업이 된다고요? 🤔")
st.caption("기후변화가 청소년의 진로와 취업에 미치는 영향 분석 보고서")

# --- 데이터 로드 및 사이드바 ---
full_df = get_report_data()
st.sidebar.title("보고서 옵션 ⚙️")
selected_year = st.sidebar.selectbox(
    '기준 연도 선택',
    options=full_df['연도'].unique(),
    index=len(full_df['연도'].unique()) - 1
)
filtered_df = full_df[full_df['연도'] == selected_year].copy()

# --- 1. 서론 (문제 제기) ---
st.header("📑 서론: 기후변화, 더 이상 환경 문제만이 아닙니다")
st.markdown("""
기후변화는 단순히 환경 문제를 넘어서, **청소년 세대의 진로와 취업에도 큰 영향을 미치고 있습니다.**
기후 위기에 대응하기 위한 산업 구조 변화와 신재생에너지 확대, 탄소중립 정책은 노동시장의 수요를 빠르게 재편하고 있기 때문입니다.
고용노동부 자료에 따르면 **녹색 일자리는 최근 5년간 꾸준히 증가**했고, 반대로 화석연료 기반 산업 일자리는 감소세를 보였습니다.
> 따라서 기후변화는 **미래 사회의 취업 환경을 결정짓는 핵심 요인**으로, 청소년 세대가 반드시 주목해야 하는 문제입니다.
""")
st.divider()

# --- 2. 본론 1 (데이터 분석) ---
lottie_data = load_lottieurl("https://lottie.host/e70f61d5-9493-424a-9383-9975a6c12202/66f8p4e5Wv.json")
if lottie_data:
    st_lottie(lottie_data, speed=1, height=200, key="data_analysis")
else:
    st.warning("⚠️ 데이터 분석 애니메이션을 불러올 수 없습니다.")

st.header(f"📊 본론 1: {selected_year}년, 데이터로 보는 기후 위기와 일자리의 변화")
st.write("기후 위기는 산업 구조와 취업률의 변화를 불러오고 있습니다. 정부는 2050 탄소중립을 목표로 수십만 개의 녹색 일자리를 창출할 계획이라고 발표했으며, 아래 데이터는 그 변화의 단면을 보여줍니다.")

st.subheader("1. '녹색 전환'에 따른 산업별 일자리 전망")
col1, col2 = st.columns([0.6, 0.4])
with col1:
    industry_df = filtered_df[filtered_df['구분'].isin(['성장', '감소'])].copy()
    fig1 = go.Figure(go.Sunburst(
        labels=["녹색 전환", "성장 산업", "감소 산업", *industry_df['유형']],
        parents=["", "녹색 전환", "녹색 전환", "성장 산업", "성장 산업", "감소 산업", "감소 산업"],
        values=[0, sum(industry_df[industry_df['구분']=='성장']['증감률']), sum(abs(industry_df[industry_df['구분']=='감소']['증감률'])),
                *industry_df['증감률'].abs()],
        branchvalues="total",
        marker=dict(colors=['#2ECC71', '#E74C3C', '#2ECC71', '#2ECC71', '#E74C3C', '#E74C3C']),
        hoverinfo='label+percent parent'
    ))
    fig1.update_layout(title=f'<b>{selected_year}년 녹색 전환 영향 분석</b>', margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(plot_with_font(fig1), use_container_width=True)
with col2:
    growth_sectors = industry_df[industry_df['구분'] == '성장']
    decline_sectors = industry_df[industry_df['구분'] == '감소']
    st.markdown("<br>", unsafe_allow_html=True)
    st.metric(label=f"🟢 {growth_sectors.iloc[0]['유형']} 일자리 전망", value=f"{growth_sectors.iloc[0]['증감률']:.1f}%")
    st.metric(label=f"🟢 {growth_sectors.iloc[1]['유형']} 일자리 전망", value=f"{growth_sectors.iloc[1]['증감률']:.1f}%")
    st.metric(label=f"🔴 {decline_sectors.iloc[0]['유형']} 일자리 전망", value=f"{decline_sectors.iloc[0]['증감률']:.1f}%")
    st.metric(label=f"🔴 {decline_sectors.iloc[1]['유형']} 일자리 전망", value=f"{decline_sectors.iloc[1]['증감률']:.1f}%")

st.subheader("2. 친환경 관련 전공, 취업 시장의 '블루칩'으로 부상")
major_df = filtered_df[filtered_df['전공'].isin(['친환경·에너지', '전체 평균'])].copy()
major_rate = major_df.loc[major_df['전공'] == '친환경·에너지', '취업률'].iloc[0]
avg_rate = major_df.loc[major_df['전공'] == '전체 평균', '취업률'].iloc[0]

fig2 = go.Figure(go.Indicator(
    mode="gauge+number+delta", value=major_rate,
    title={'text': f"<b>친환경·에너지 전공 취업률 ({selected_year}년)</b>"},
    delta={'reference': avg_rate, 'suffix': '%p', 'relative': False},
    gauge={'axis': {'range': [60, 90]}, 'bar': {'color': "#27AE60"},
           'steps': [{'range': [60, 70], 'color': "lightgray"}, {'range': [70, 80], 'color': "gray"}],
           'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': avg_rate}}))
fig2.update_layout(height=400)
st.plotly_chart(plot_with_font(fig2), use_container_width=True)
st.info("ypec 청소년 통계 포털 데이터에 따르면, 친환경·에너지 관련 전공자의 취업률은 전체 평균보다 높게 나타나며, 이는 기후 변화가 유망 전공의 지형도를 바꾸고 있음을 시사합니다.")
st.divider()

# --- 3. 본론 2 (원인과 영향) ---
lottie_cause = load_lottieurl("https://lottie.host/1f7a93a3-1191-42ea-a0d0-55b634860010/89a5p8M6pI.json")
if lottie_cause:
    st_lottie(lottie_cause, speed=1, height=200, key="cause_effect")
else:
    st.warning("⚠️ 원인 분석 애니메이션을 불러올 수 없습니다.")

st.header("🔍 본론 2: 기후 위기는 어떻게 취업 시장을 바꾸는가?")
st.markdown("""
### 원인: 거스를 수 없는 흐름, '녹색 전환(Green Transition)'
기후 위기가 취업에 영향을 주는 원인은 ‘녹색 전환’입니다. 기업과 사회가 기후 대응을 위해 친환경 기술을 도입하고, 새로운 직무를 만들어내기 때문입니다.
- **기업의 변화**: 기사 보도에 따르면 대기업들은 **ESG 경영**을 확대하며 환경·에너지 분야 인재를 적극적으로 채용하고 있습니다.
- **새로운 시장**: 기후·환경 스타트업도 빠르게 성장하면서 청년들의 진입 기회가 넓어지고 있습니다.
### 영향: 위험과 기회의 공존
> 결국 기후 위기는 청년들에게 **‘위험’과 ‘기회’를 동시에** 던져주고 있으며, 변화에 어떻게 준비하느냐가 미래 취업의 성패를 좌우하게 됩니다.
""")
st.divider()

# --- 4. 결론 (제언) ---
lottie_conclusion = load_lottieurl("https://lottie.host/7e05e830-7456-4c31-b844-93b5a1b55909/Rk4yQO6fS3.json")
if lottie_conclusion:
    st_lottie(lottie_conclusion, speed=1, height=200, key="conclusion_idea")
else:
    st.warning("⚠️ 결론 애니메이션을 불러올 수 없습니다.")

st.header("🚀 결론: 기후 위기를 기회로, 미래를 준비하는 청소년의 자세")
st.markdown("우리는 다음 세 가지 실천을 제안합니다.")
c1, c2, c3 = st.columns(3)
with c1:
    st.success("#### 제언 1: 기후 데이터 탐사대", icon="🕵️")
    st.write("기후 데이터와 산업 통계를 직접 찾아 분석하며, 변화하는 취업 환경을 탐구합니다.")
with c2:
    st.success("#### 제언 2: 그린 IT 프로젝트", icon="💻")
    st.write("소프트웨어과 학생으로서 기후 데이터를 분석하는 프로그램을 만들거나, 에너지 절약을 위한 앱 아이디어를 구상합니다.")
with c3:
    st.success("#### 제언 3: 청소년의 목소리", icon="📣")
    st.write("학생회나 지역 청소년 기구를 통해, ‘기후 위기 대응이 곧 청년 고용 창출’임을 알리고 정책 제안을 할 수 있습니다.")
st.divider()

# --- 5. 참고 자료 ---
st.header("📚 참고 자료")
st.markdown("""
- **대학진학률 및 취업률 그래프**, 여성가족부 (ypec 청소년 통계 포털)
- **기후변화 4대지표**, 탄소중립 정책포털
- **향후 10년 사라질 직업 1위는?**, 포켓뉴스 다음채널
- **주요 업종 일자리 그래프**, 고용노동부
""")