import streamlit as st
import pandas as pd
import re
import json
import os
import time

# --- [1. 핵심 엔진: 기존 로직 유지] ---
def format_seconds(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours > 0 else f"{minutes}:{secs:02d}"

# --- [2. UI 및 메인 로직] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 세션 상태 초기화 (에러 방지용)
if 'refresh_count' not in st.session_state:
    st.session_state['refresh_count'] = 0

# 배포 시 이 줄을 is_admin = False 로 수정하세요!
#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드 (데이터 생성)", value=False)
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
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">
                    "{tgt['phrase']}"
                </h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            
            do_loop = st.checkbox("🔄 구간 무한 반복", value=True)
            
            # 버튼 클릭 시 카운트를 올려서 고유한 Key를 생성하게 함
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state['refresh_count'] += 1
                st.rerun()

            st.caption("※ 재생이 멈추거나 구간을 넘어가면 버튼을 눌러주세요.")

        with col2:
            # 고유 ID 생성 (TypeError 방지를 위해 문자열로 변환)
            rid = str(st.session_state['refresh_count'])
            
            # 유튜브 파라미터 구성
            # loop=1과 playlist={v_id}를 조합해야 구간 반복이 가장 잘 작동합니다.
            base_url = f"https://www.youtube.com/embed/{v_id}"
            query = f"?start={tgt['start_sec']}&end={tgt['end_sec']}&autoplay=1&cc_load_policy=1&rel=0"
            
            if do_loop:
                query += f"&loop=1&playlist={v_id}"
            
            # 캐시 방지를 위해 랜덤 쿼리 추가
            final_url = f"{base_url}{query}&t={rid}"
            
            # iframe에 동적인 key를 부여하여 버튼 클릭 시 강제로 다시 그리게 함
            st.components.v1.iframe(final_url, height=450, key=f"yt_player_{rid}")

    else:
        st.warning("데이터 파일(final_mapping.json)이 없습니다. 관리자 모드에서 먼저 생성해주세요.")
else:
    # 관리자 모드 (이전과 동일)
    st.title("🛠️ 데이터 엔진 (Admin Mode)")
    st.write("로스터와 자막을 업로드하세요.")
    # ... (데이터 생성 로직 생략 - 기존 코드 그대로 사용) ...