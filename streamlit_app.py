import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
from io import StringIO
from streamlit_lottie import st_lottie
import time
import json # [신규] JSON 파일 처리를 위한 라이브러리

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
        st.error(f"파일 처리 중 오류: {e}. 'openpyxl' 라이브러리가 설치되었는지 확인해주세요.")
        return pd.DataFrame()

@st.cache_data
def load_user_employment_data():
    """예시용 기후 산업 일자리 데이터를 생성합니다."""
    data = {"년도": [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
            "녹색산업 일자리": [10.5, 11.5, 13.0, 15.0, 17.0, 19.0, 21.5, 24.0],
            "화석연료 산업 일자리": [22.0, 21.0, 20.0, 18.0, 16.0, 14.0, 12.5, 11.0]}
    return pd.DataFrame(data)

@st.cache_data
def load_lottieurl(url: str):
    """Lottie 애니메이션 데이터 로딩 함수 (재시도 기능 포함)"""
    for _ in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
        except requests.exceptions.RequestException:
            time.sleep(1)
    return None

# --- [신규] 메모 파일 처리 함수 ---
MEMO_FILE = "memos.json"

def load_memos():
    """memos.json 파일에서 모든 메모를 불러옵니다."""
    try:
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_memos(memos):
    """memos.json 파일에 모든 메모를 저장합니다."""
    with open(MEMO_FILE, "w", encoding="utf-8") as f:
        json.dump(memos, f, ensure_ascii=False, indent=4)


# --- 데이터 로드 ---
climate_raw = fetch_gistemp_csv()
employment_sample_df = load_user_employment_data()

# --- 사이드바 ---
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

# --- 필터링된 데이터 생성 ---
filtered_unemployment = unemployment_df[(unemployment_df["연도"] >= year_range[0]) & (unemployment_df["연도"] <= year_range[1])] if not unemployment_df.empty else pd.DataFrame()
filtered_climate = climate_raw[(climate_raw["연도"] >= year_range[0]) & (climate_raw["연도"] <= year_range[1])] if not climate_raw.empty else pd.DataFrame()

# --- 핵심 지표 카드 ---
if not filtered_unemployment.empty and not filtered_climate.empty:
    st.subheader(f"📈 {year_range[1]}년 핵심 지표 요약")
    latest_unemployment = filtered_unemployment.iloc[-1]
    prev_unemployment = filtered_unemployment.iloc[-2] if len(filtered_unemployment) > 1 else latest_unemployment
    latest_climate = filtered_climate[filtered_climate['연도'] == year_range[1]].iloc[-1] if not filtered_climate[filtered_climate['연도'] == year_range[1]].empty else filtered_climate.iloc[-1]
    prev_climate = filtered_climate[filtered_climate['연도'] == year_range[1]-1].iloc[-1] if year_range[1]-1 in filtered_climate['연도'].values else latest_climate
    
    col1, col2, col3 = st.columns(3)
    col1.metric("취업자 수", f"{latest_unemployment['취업자 수 (만 명)']} 만 명", f"{latest_unemployment['취업자 수 (만 명)'] - prev_unemployment['취업자 수 (만 명)']:.1f} 만 명")
    col2.metric("실업률", f"{latest_unemployment['실업률 (%)']}%", f"{latest_unemployment['실업률 (%)'] - prev_unemployment['실업률 (%)']:.1f}%p", delta_color="inverse")
    col3.metric("기온 이상", f"{latest_climate['기온이상']} °C", f"{latest_climate['기온이상'] - prev_climate['기온이상']:.2f} °C")
    st.markdown("---")

# --- 그래프 섹션 (생략) ---


# --- 해결방안 게임 섹션 ---
st.markdown("---")
st.header("🚀 해결방안: 나의 미래 직업 만들기 (게임)")
st.info("당신의 선택이 미래의 커리어와 환경에 어떤 영향을 미치는지 시뮬레이션 해보세요!")

lottie_study = load_lottieurl("https://lottie.host/175b5a27-63f5-4220-8374-e32a13f789e9/5N7sBfSbB6.json")
lottie_activity = load_lottieurl("https://lottie.host/97217a14-a957-41a4-9e1e-2879685a21e0/p3T5exs27n.json")
lottie_career = load_lottieurl("https://lottie.host/7e05e830-7456-4c31-b844-93b5a1b55909/Rk4yQO6fS3.json")

st.subheader("1️⃣ 당신의 선택은?")
col1, col2, col3 = st.columns(3)
with col1:
    if lottie_study: st_lottie(lottie_study, height=150, key="study")
    st.markdown("#### 학업 활동")
    edu_choice = st.radio("어떤 과목에 더 집중할까요?", ('탄소 배출량 분석 AI 모델링', '전통 내연기관 효율성 연구'), key="edu")
with col2:
    if lottie_activity: st_lottie(lottie_activity, height=150, key="activity")
    st.markdown("#### 대외 활동")
    activity_choice = st.radio("어떤 동아리에 가입할까요?", ('신재생에너지 정책 토론 동아리', '고전 문학 비평 동아리'), key="activity")
with col3:
    if lottie_career: st_lottie(lottie_career, height=150, key="career")
    st.markdown("#### 진로 탐색")
    career_choice = st.radio("어떤 기업의 인턴십에 지원할까요?", ('에너지 IT 스타트업', '안정적인 정유회사'), key="career")

base_score = 50; base_co2 = 0; skills = []
if edu_choice == '탄소 배출량 분석 AI 모델링':
    score_edu = 25; co2_edu = -15; skills.extend(["AI/머신러닝", "데이터 분석"])
else:
    score_edu = 5; co2_edu = 5; skills.append("기계 공학")
if activity_choice == '신재생에너지 정책 토론 동아리':
    score_activity = 15; co2_activity = -10; skills.extend(["정책 이해", "토론 및 설득"])
else:
    score_activity = 5; co2_activity = 0; skills.append("인문학적 소양")
if career_choice == '에너지 IT 스타트업':
    score_career = 20; co2_career = -10; skills.extend(["실무 경험", "문제 해결 능력"])
else:
    score_career = 10; co2_career = 5; skills.append("대기업 프로세스 이해")
final_score = round(base_score + score_edu + score_activity + score_career)
# --- [수정] 오타 수정 ---
final_co2 = round(base_co2 + co2_edu + co2_activity + co2_career)
final_skills = list(set(skills))

st.subheader("2️⃣ 10년 후, 당신의 모습은?")
st.markdown(f"""
<div style="background-color: #F0F2F6; border-radius: 10px; padding: 20px; display: flex; justify-content: space-around; align-items: center; color: black;">
    <div style="text-align: center;">
        <span style="font-size: 1.2em;">🎓 미래 커리어 경쟁력</span><br>
        <span style="font-size: 2.5em; font-weight: bold;">{final_score}</span><span style="font-size: 1.5em;"> 점</span>
    </div>
    <div style="text-align: center;">
        <span style="font-size: 1.2em;">🌱 환경 기여도 (CO₂)</span><br>
        <span style="font-size: 2.5em; font-weight: bold;">{-final_co2}</span><span style="font-size: 1.5em;"> 감축</span>
    </div>
    <div style="text-align: center;">
        <span style="font-size: 1.2em;">🔑 획득한 핵심 역량</span><br>
        <span style="font-size: 1.2em;">{', '.join(final_skills) if final_skills else '선택 대기중...'}</span>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
if final_score >= 100:
    st.success("🎉 **완벽한 미래 인재!** 당신은 기후 위기를 기회로 만드는 시대의 리더가 될 것입니다.", icon="🚀")
elif final_score >= 75:
    st.info("👍 **유망한 인재!** 녹색 전환 시대에 성공적으로 적응할 수 있는 뛰어난 잠재력을 갖췄습니다.", icon="🌟")
else:
    st.warning("🤔 **성장 가능성!** 변화하는 산업 트렌드에 조금 더 관심을 가진다면 당신의 미래는 더욱 밝아질 거예요.", icon="💡")

# --- 나의 실천 다짐 남기기 (파일 저장 방식) ---
st.markdown("---")
st.header("✍️ 나의 실천 다짐 남기기 (공유 방명록)")
st.write("여러분의 다짐은 이 웹사이트에 영구적으로 저장되어 모든 방문자에게 공유됩니다!")

cols = st.columns([0.7, 0.3])
with cols[0]:
    name = st.text_input("닉네임", placeholder="자신을 표현하는 멋진 닉네임을 적어주세요!", key="memo_name")
    memo = st.text_area("실천 다짐", placeholder="예) 텀블러 사용하기, 가까운 거리는 걸어다니기 등", key="memo_text")
with cols[1]:
    color = st.color_picker("메모지 색상 선택", "#FFFACD", key="memo_color")
    if st.button("다짐 남기기!", use_container_width=True):
        if name and memo:
            all_memos = load_memos()
            all_memos.insert(0, {"name": name, "memo": memo, "color": color, "timestamp": str(datetime.now())})
            save_memos(all_memos)
            st.balloons()
            st.success("소중한 다짐이 모두에게 공유되었습니다!")
            st.rerun()
        else:
            st.warning("닉네임과 다짐을 모두 입력해주세요!")

st.divider()
st.subheader("💬 우리의 다짐들")
memos_list = load_memos()

if not memos_list:
    st.info("아직 작성된 다짐이 없어요. 첫 번째 다짐을 남겨주세요!")
else:
    memo_cols = st.columns(3)
    for i, m in enumerate(memos_list):
        with memo_cols[i % 3]:
            st.markdown(f"""
            <div style="background-color:{m.get('color', '#FFFACD')}; border-left: 5px solid #FF6347; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); height: 150px;">
                <p style="font-size: 1.1em; color: black; margin-bottom: 10px;">"{m.get('memo', '')}"</p>
                <strong style="font-size: 0.9em; color: #555;">- {m.get('name', '')} -</strong>
            </div>
            """, unsafe_allow_html=True)

# --- 데이터 다운로드 및 출처 ---
st.markdown("---")
st.subheader("📥 데이터 다운로드")
if not climate_raw.empty:
    st.download_button("공식 기후 데이터 다운로드", climate_raw.to_csv(index=False).encode("utf-8-sig"), "climate_data.csv", "text/csv")
if not unemployment_df.empty:
    st.download_button("e-나라지표 데이터 다운로드", unemployment_df.to_csv(index=False).encode("utf-8-sig"), "unemployment_data.csv", "text/csv")
st.download_button("산업 구조 데이터(예시) 다운로드", employment_sample_df.to_csv(index=False).encode("utf-8-sig"), "industry_employment_sample.csv", "text/csv")
st.caption("🌐 기후 데이터: NASA GISTEMP / 📈 취업 데이터: e-나라지표 (사용자 업로드) / 📊 산업 데이터: 보고서 기반 예시")

