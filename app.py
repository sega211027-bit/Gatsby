import streamlit as st
import pandas as pd
import re
import json
import os
import time
import streamlit.components.v1 as components

# --- [1. 핵심 엔진: 시간 변환] ---
def format_seconds(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours > 0 else f"{minutes}:{secs:02d}"

# --- [2. UI 및 메인 로직] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())

#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)
is_admin = False

if not is_admin:
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        v_id, r_data = cfg['video_id'], cfg['data']
        
        st.title("📖 Great Gatsby Audio Guide")
        
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
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
            
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.v_key = str(time.time())
                st.rerun()

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            duration = (e_val - s_val) * 1000 # 밀리초 단위 계산
            
            # loop 파라미터는 제거합니다 (0초로 가는 버그 방지)
            params = f"start={s_val}&end={e_val}&autoplay=1&cc_load_policy=1&rel=0"
            final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"

            # [핵심 수정] 자바스크립트를 이용한 강제 루프 구현
            # 영상 길이만큼 시간이 지나면 자동으로 페이지를 새로고침(rerun) 하도록 유도
            loop_script = ""
            if do_loop:
                loop_script = f"""
                <script>
                    setTimeout(function() {{
                        window.parent.location.reload();
                    }}, {duration + 1000}); // 영상 길이 + 1초 뒤 새로고침
                </script>
                """

            components.html(f"""
                {loop_script}
                <iframe 
                    width="100%" 
                    height="450" 
                    src="{final_src}" 
                    frameborder="0" 
                    allow="autoplay; encrypted-media" 
                    allowfullscreen>
                </iframe>
            """, height=460)
    else:
        st.warning("데이터 파일이 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")