import streamlit as st
import pandas as pd
import re
import json
import os

# --- [1. 핵심 엔진: 시간 변환 로직] ---
def format_seconds(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours > 0 else f"{minutes}:{secs:02d}"

# --- [2. UI 설정 및 세션 초기화] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 세션 상태 초기화: 에러 방지를 위해 최상단에 배치
if 'count' not in st.session_state:
    st.session_state.count = 0

# 배포 시 이 줄을 False로 바꾸세요.
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

        # 시작 단어 강조 박스
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
            
            # 재생 버튼: count를 올려서 iframe을 강제로 새로고침함
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.count += 1
                st.rerun()

            st.caption("재생이 원활하지 않으면 위 버튼을 눌러주세요.")

        with col2:
            # URL 파라미터 조립
            start = tgt['start_sec']
            end = tgt['end_sec']
            
            # 가장 안정적인 임베드 주소 형식
            embed_url = f"https://www.youtube.com/embed/{v_id}?start={start}&end={end}&autoplay=1&cc_load_policy=1&rel=0"
            
            if do_loop:
                # playlist 파라미터가 있어야 loop가 정상 작동함
                embed_url += f"&loop=1&playlist={v_id}"
            
            # 에러의 원인이었던 key 부분을 가장 심플한 문자열로 처리
            # 세션 카운트를 뒤에 붙여 버튼 클릭 시마다 고유한 위젯으로 인식하게 함
            st.components.v1.iframe(
                src=f"{embed_url}&v={st.session_state.count}",
                height=450,
                key=f"player_{st.session_state.count}"
            )

    else:
        st.warning("데이터 파일(final_mapping.json)을 찾을 수 없습니다.")

else:
    # 관리자 모드 (데이터 생성용 - 기존 엔진 코드 필요 시 추가)
    st.title("Admin Mode")
    st.write("로스터와 자막을 업로드하여 데이터를 생성하세요.")