import streamlit as st
import json
import os
import time
import streamlit.components.v1 as components

# --- [1. 시간 변환 함수] ---
def format_seconds(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except:
        return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# --- [2. 세션 상태 관리: 트리거 정교화] ---
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())
if 'last_selected_id' not in st.session_state:
    st.session_state.last_selected_id = None

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바 설정] ---
    st.sidebar.header("📍 제어판")
    
    # 토글은 값만 바꿀 뿐, v_key를 직접 건드리지 않습니다.
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    
    if loop_active:
        st.sidebar.markdown("🟢 **상태: 무한반복 ON**")
    else:
        st.sidebar.markdown("🔴 **상태: 무한반복 OFF**")

    st.sidebar.divider()

    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    
    # [트리거] 드롭박스 '회차'가 실제로 바뀌었을 때만 영상 리셋
    current_id = f"{day}-{rnd}-{turn}"
    if st.session_state.last_selected_id != current_id:
        st.session_state.v_key = str(time.time())
        st.session_state.last_selected_id = current_id

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # --- [메인 화면] ---
    st.title("📖 Great Gatsby Audio Guide")

    # SyntaxError 방지를 위해 문자열 끝("")을 확실히 닫았습니다.
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
            <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 이 단어가 들리면 낭독을 시작하세요</p>
            <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.5em; margin: 0;">
                "{tgt.get('phrase', '')}"
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        s_disp = format_seconds(tgt.get('start_sec', 0))
        e_disp = format_seconds(tgt.get('end_sec', 0))
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {s_disp} ~ {e_disp}")
        
        # [트리거] 버튼 클릭 시 수동 강제 리셋
        if st.button("▶️ 처음부터 재생  토글되나보자", use_container_width=True):
            st.session_state.v_key = str(time.time())
            st.rerun()

    with col2:
        s_val, e_val = str(tgt.get('start_sec', 0)), str(tgt.get('end_sec', 0))
        
        # 기존 API 파라미터 유지
        params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&rel=0"
        params += "&loop=1" if loop_active else "&loop=0"

        # v_key는 드롭박스/버튼 트리거 시에만 변하므로 토글 변경 시 영상은 유지됩니다.
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
