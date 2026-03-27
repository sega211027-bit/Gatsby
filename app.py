#"final_roaster_result.xlsx" 엑셀파일이름 변경해야함

import streamlit as st
import pandas as pd

st.set_page_config(page_title="리딩 가이드", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("final_roaster_result.xlsx")

df = load_data()

st.title("🎧 나의 리딩 구간 찾기")

# 선택 UI
c1, c2, c3 = st.columns(3)
with c1: day = st.selectbox("📅 일차 선택", df['Day'].unique())
with c2: rnd = st.selectbox("🔄 ROUND", sorted(df[df['Day']==day]['ROUND'].unique()))
with c3: ses = st.selectbox("👥 회차", sorted(df[(df['Day']==day) & (df['ROUND']==rnd)]['회차'].unique()))

row = df[(df['Day']==day) & (df['ROUND']==rnd) & (df['회차']==ses)].iloc[0]

# 시간 변환
m, s = map(int, str(row['시작시간']).split(':'))
t_sec = m * 60 + s

st.divider()

col_v, col_t = st.columns([1, 1.2])
with col_v:
    st.subheader(f"🔊 {row['담당자']} 님 순서")
    st.markdown(f"**⏰ 시작 지점:** {row['시작시간']}")
    st.video(row['URL'])
    st.write(f"🚩 **시작 문구:** {row['시작 단어(5)']}")
    st.write(f"🏁 **종료 문구:** {row['마지막 단어(5)']}")

with col_t:
    st.subheader("📄 읽으실 문단 (참고)")
    # 이미지의 '문단 첫 10단어' 열 등을 보여줌
    st.markdown(f'''
        <div style="font-size:24px; line-height:1.6; background:#f0f2f6; padding:25px; border-radius:15px;">
            {row['문단 첫 10단어']}...
        </div>
    ''', unsafe_allow_html=True)
