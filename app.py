import streamlit as st
import json
import os
import time

# --- [UI 설정] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 세션 상태로 재생 버전 관리
if 'v_key' not in st.session_state:
    st.session_state.v_key = 0

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

        # 문장 안내 박스
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
                <p style="color: #666; font-size: 1.1em;">📍 이 단어가 들리면 낭독을 시작하세요</p>
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">"{tgt['phrase']}"</h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            
            # [수정] 무한 반복 체크박스 (세션에 저장하여 상태 유지)
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.v_key += 1
                st.rerun()

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            duration = e_val - s_val
            
            # URL 생성 (매번 미세하게 다르게 하여 캐시 방지)
            final_url = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&mute=0&rel=0&v={st.session_state.v_key}_{turn}"

            # [핵심] st.components.v1.html 대신 st.video를 써보거나, 
            # 가장 표준적인 iframe 방식을 사용합니다.
            st.components.v1.iframe(src=final_url, height=450)

            # [핵심 루프 로직] 
            # 영상이 재생되는 동안 Streamlit이 대기하다가 시간이 다 되면 스스로 새로고침합니다.
            if do_loop:
                # 영상 길이 + 로딩 여유시간(2초)만큼 기다린 후 새로고침 트리거
                time.sleep(duration + 2)
                st.session_state.v_key += 1
                st.rerun()
            
    else:
        st.warning("데이터 파일이 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")