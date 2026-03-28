import streamlit as st
import pandas as pd
import re
import json
import os

# --- [1. 핵심 엔진: 시간 변환] ---
def format_seconds(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours > 0 else f"{minutes}:{secs:02d}"

# --- [2. UI 설정 및 세션 초기화] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 배포 시 False로 변경하세요.
#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)
is_admin = False

if not is_admin:
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        v_id, r_data = cfg['video_id'], cfg['data']
        
        st.title("📖 Great Gatsby Audio Guide")
        
        # 사이드바 선택
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

        # 상단 안내 박스
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
                <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 이 단어가 들리면 낭독을 시작하세요</p>
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.5em;">
                    "{tgt['phrase']}"
                </h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            do_loop = st.checkbox("🔄 구간 무한 반복", value=True)
            
            # 버튼 클릭 시 페이지를 단순히 새로고침하여 영상 재시작 유도
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.rerun()

        with col2:
            # 변수를 사전에 문자열로 확정
            s_val = str(tgt['start_sec'])
            e_val = str(tgt['end_sec'])
            
            # URL 파라미터 구성
            # rel=0(관련영상방지), iv_load_policy=3(주석방지) 추가로 플레이어 부하 감소
            params = f"start={s_val}&end={e_val}&autoplay=1&cc_load_policy=1&rel=0&iv_load_policy=3"
            
            if do_loop:
                params += f"&loop=1&playlist={v_id}"
            
            final_src = f"https://www.youtube.com/embed/{v_id}?{params}"
            
            # [핵심] key를 고정된 문자열로 설정하여 TypeError 원천 차단
            st.components.v1.iframe(
                src=final_src,
                height=450,
                key="gatsby_player_static"
            )
    else:
        st.warning("데이터 파일(final_mapping.json)이 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성 엔진은 이전 코드를 유지해 주세요.")