import streamlit as st
import json
import os
import time
import streamlit.components.v1 as components

# --- [1. 시간 변환 함수: KeyError 방지용] ---
def format_seconds(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except:
        return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# 세션 상태 초기화 (강제 리로딩용)
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())

# --- [2. 메인 실행 블록] ---
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # [사이드바 설정]
    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    st.title("📖 Great Gatsby Audio Guide")

    # [A. 시작 문구 박스] - image_389ee3 스타일 복구
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
            <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 이 단어가 들리면 낭독을 시작하세요</p>
            <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.5em;">
                "{tgt.get('phrase', '')}"
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # [B. 메인 레이아웃: 정보와 플레이어]
    col1, col2 = st.columns([1, 2])
    
    with col1:
        s_disp = format_seconds(tgt.get('start_sec', 0))
        e_disp = format_seconds(tgt.get('end_sec', 0))
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {s_disp} ~ {e_disp}")
        
        # [복구] 다시 시작 버튼
        if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
            st.session_state.v_key = str(time.time())
            st.rerun()
        
        st.caption("※ 구간 종료 시 위 버튼을 눌러주세요.")

    with col2:
        # [복구] 유튜브 플레이어 기능
        s_val = str(tgt.get('start_sec', 0))
        e_val = str(tgt.get('end_sec', 0))
        
        # playlist 파라미터를 포함하여 end 시점 정지 보장
        params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&rel=0"
        final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"

        components.html(f"""
            <iframe 
                width="100%" height="450" 
                src="{final_src}" 
                frameborder="0" 
                allow="autoplay; encrypted-media" 
                allowfullscreen>
            </iframe>
        """, height=460)

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
