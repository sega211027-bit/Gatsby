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

# 배포 시 이 줄을 is_admin = False 로 수정하세요!
is_admin = st.sidebar.checkbox("🛠️ 관리자 모드 (데이터 생성)", value=False)

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
            
            # [수정] 무한 반복 체크박스
            do_loop = st.checkbox("🔄 구간 무한 반복 (추천)", value=True)
            
            # [수정] 버튼 클릭 시 고유 ID를 생성해 주소를 강제로 갱신함
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state['refresh_key'] = time.time() # 버튼 누를 때마다 다른 값 생성
                st.rerun()

            st.caption("※ 구간 무한 반복이 작동하지 않으면 버튼을 눌러주세요.")

        with col2:
            # [핵심 수정] 
            # 1. playlist 파라미터에 현재 비디오 ID를 넣어 loop가 동작하게 함
            # 2. t(timestamp) 값을 주소에 섞어서 Streamlit이 주소가 바뀌었다고 인식하게 함
            refresh_id = st.session_state.get('refresh_key', time.time())
            
            base_url = f"https://www.youtube.com/embed/{v_id}"
            params = [
                f"start={tgt['start_sec']}",
                f"end={tgt['end_sec']}",
                f"autoplay=1",
                f"cc_load_policy=1",
                f"rel=0", # 관련 영상 방지
                f"t={refresh_id}" # 강제 갱신용
            ]
            
            if do_loop:
                params.append(f"loop=1")
                params.append(f"playlist={v_id}") # loop=1을 위해 필수
            
            embed_url = f"{base_url}?{'&'.join(params)}"
            
            # iframe에 key를 부여하여 위젯이 완전히 다시 그려지도록 함
            st.components.v1.iframe(embed_url, height=450, key=f"yt_player_{refresh_id}")

    else:
        st.warning("데이터 파일이 없습니다.")
else:
    # 관리자 모드는 이전과 동일 (생략)
    st.title("Admin Mode")
    st.write("데이터 생성은 이전 코드를 참고해 주세요.")