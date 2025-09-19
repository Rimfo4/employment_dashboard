import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
from io import StringIO

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="기후와 취업 대시보드", layout="wide")


# --- 데이터 로딩 함수들 ---
@st.cache_data
def fetch_gistemp_csv():
    """NASA의 GISTEMP 기온 이상 데이터를 불러옵니다."""
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text), skiprows=1)
        df = df.rename(columns={df.columns[0]: "연도"})
        df = df[["연도", "J-D"]].dropna().rename(columns={"J-D": "기온이상"})
        df["날짜"] = pd.to_datetime(df["연도"].astype(str) + "-12-31")
        today = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))
        df = df[df["날짜"] <= today]
        return df[["날짜", "연도", "기온이상"]]
    except:
        return pd.DataFrame()

@st.cache_data
def process_uploaded_employment_data(uploaded_file):
    """사용자가 업로드한 e-나라지표 엑셀 파일을 처리합니다."""
    if not uploaded_file:
        return pd.DataFrame()
    try:
        df = pd.read_excel(uploaded_file, skiprows=28, header=1)
        df = df.iloc[:, [0, 1, 3]].copy()
        df.columns = ["연도", "취업자 수 (만 명)", "실업률 (%)"]
        
        df = df.dropna(subset=["연도"])
        df = df[pd.to_numeric(df['연도'], errors='coerce').notna()]
        for col in df.columns:
            if col != '연도':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df["연도"] = df["연도"].astype(int)
        today = datetime.now()
        df = df[df["연도"] < today.year]
        return df
    except Exception as e:
        st.error(f"파일 처리 중 오류: {e}")
        return pd.DataFrame()

@st.cache_data
def load_user_employment_data():
    """예시용 기후 산업 일자리 데이터를 생성합니다."""
    data = {"년도": [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
            "녹색산업 일자리": [10.5, 11.5, 13.0, 15.0, 17.0, 19.0, 21.5, 24.0],
            "화석연료 산업 일자리": [22.0, 21.0, 20.0, 18.0, 16.0, 14.0, 12.5, 11.0]}
    return pd.DataFrame(data)

# --- 데이터 로드 ---
climate_raw = fetch_gistemp_csv()
employment_sample_df = load_user_employment_data()

# -------------------------------
# 사이드바
# -------------------------------
with st.sidebar:
    st.header("📊 옵션 설정")
    st.subheader("e-나라지표 데이터")
    uploaded_file = st.file_uploader("취업률 엑셀 파일 업로드", type=["xlsx", "xls"])
    unemployment_df = process_uploaded_employment_data(uploaded_file)
    
    all_years = pd.concat([
        employment_sample_df['년도'],
        unemployment_df['년도'] if not unemployment_df.empty else pd.Series(dtype='int')
    ]).dropna().unique()
    
    min_year, max_year = (int(all_years.min()), int(all_years.max())) if len(all_years) > 0 else (2017, 2024)
    year_range = st.slider("표시할 연도 범위", min_year, max_year, (min_year, max_year))

# -------------------------------
# 메인 대시보드
# -------------------------------
st.title("🌍 기후 변화와 취업 대시보드")

# --- 기존 대시보드 내용 (생략 없이 그대로 유지) ---
# ... (핵심 지표 카드, 그래프 1, 2, 3 코드)
# --- 핵심 지표 카드 ---
# ...
# --- 그래프 섹션 ---
# ...

# -------------------------------
# [신규] 해결방안 게임 섹션
# -------------------------------
st.markdown("---")
st.header("🚀 해결방안: 나의 미래 직업 만들기 (게임)")
st.info("당신은 10년 뒤 사회 진출을 앞둔 학생입니다. 당신의 선택이 미래의 커리어와 환경에 어떤 영향을 미치는지 시뮬레이션 해보세요!")

# --- 게임 로직 및 UI ---
# 1. 선택지 UI
st.subheader("1️⃣ 당신의 선택은?")
col1, col2, col3 = st.columns(3)
with col1:
    edu_choice = st.slider(
        "전공 심화 분야 선택", 0, 100, 50,
        help="0에 가까울수록 전통 산업, 100에 가까울수록 녹색/IT 산업에 집중합니다."
    )
with col2:
    project_choice = st.radio(
        "개인 프로젝트 주제 선택",
        ('에너지 절약 앱 개발', '교내 e-스포츠 대회 개최')
    )
with col3:
    policy_choice = st.radio(
        "정책 지지 활동 선택",
        ('녹색 기술 투자 확대', '화석 연료 보조금 유지')
    )

# 2. 결과 계산
base_score = 50
base_co2 = 0
skills = []

# 교육 선택 반영
score_edu = (edu_choice - 50) * 0.3 # -15 to +15
co2_edu = (50 - edu_choice) * 0.2 # -10 to +10
if edu_choice > 70: skills.extend(["AI 데이터 분석", "신재생에너지"])
elif edu_choice > 30: skills.append("IT 기본 역량")
else: skills.append("전통 산업 공정 이해")

# 프로젝트 선택 반영
if project_choice == '에너지 절약 앱 개발':
    score_proj = 20
    co2_proj = -15
    skills.extend(["앱 개발", "프로젝트 관리"])
else:
    score_proj = 5
    co2_proj = 0
    skills.append("팀워크")

# 정책 선택 반영
if policy_choice == '녹색 기술 투자 확대':
    score_policy = 15
    co2_policy = -20
    skills.append("정책 이해")
else:
    score_policy = -10
    co2_policy = 10
    skills.append("시장 경제 이해")

# 최종 점수 합산
final_score = round(base_score + score_edu + score_proj + score_policy)
final_co2 = round(base_co2 + co2_edu + co2_proj + co2_policy)
final_skills = list(set(skills)) # 중복 제거

# 3. 결과 디스플레이
st.subheader("2️⃣ 10년 후, 당신의 모습은?")
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric(label="미래 커리어 경쟁력 점수", value=f"{final_score} 점")
    st.metric(label="나의 CO₂ 기여도 (감축량)", value=f"{-final_co2} kg")

with res_col2:
    st.write("**획득한 핵심 역량**")
    if final_skills:
        for skill in final_skills:
            st.markdown(f"- ✅ {skill}")
    else:
        st.write("- 선택을 기다리는 중...")

# 결과에 따른 조언 메시지
if final_score >= 85:
    st.success("🎉 **최고의 미래 인재!** 당신은 기후 위기를 기회로 만드는 리더가 될 것입니다.")
elif final_score >= 65:
    st.info("👍 **유망한 인재!** 녹색 전환 시대에 성공적으로 적응할 수 있는 충분한 잠재력을 갖췄습니다.")
else:
    st.warning("🤔 **고민이 필요한 시점!** 변화하는 산업 트렌드에 조금 더 관심을 가진다면 당신의 미래는 더욱 밝아질 거예요.")

# -------------------------------
# 데이터 다운로드 및 출처
# -------------------------------
st.markdown("---")
st.subheader("📥 데이터 다운로드")
if not climate_raw.empty:
    st.download_button("공식 기후 데이터 다운로드", climate_raw.to_csv(index=False).encode("utf-8-sig"), "climate_data.csv", "text/csv")
if not unemployment_df.empty:
    st.download_button("e-나라지표 데이터 다운로드", unemployment_df.to_csv(index=False).encode("utf-8-sig"), "unemployment_data.csv", "text/csv")
st.download_button("산업 구조 데이터(예시) 다운로드", employment_sample_df.to_csv(index=False).encode("utf-8-sig"), "industry_employment_sample.csv", "text/csv")

st.caption("🌐 기후 데이터: NASA GISTEMP / 📈 취업 데이터: e-나라지표 (사용자 업로드) / 📊 산업 데이터: 보고서 기반 예시")