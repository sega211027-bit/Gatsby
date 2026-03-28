import streamlit as st
import json
import os
import time
import streamlit.components.v1 as components

def format_seconds(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except: return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# [핵심] 재생 시작 트리거: v_key가 바뀌면 유튜브는 무조건 처음(start_sec)부터 다시 로드됩니다.
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바: 트리거 및 상태 설정] ---
    st.sidebar.header("📍 제어판")
    
    # 1. 토글 상태값 (종료 시 행동 결정 기준)
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    
    # 2. 램프 색상 구분 (상태값에 따름)
    if loop_active:
        st.sidebar.markdown("🟢 **상태: 무한반복 ON** (구간 끝 도달 시 자동 리셋)")
    else:
        st.sidebar.markdown("🔴 **상태: 무한반복 OFF** (구간 끝 도달 시 정지)")

    st.sidebar.divider()

    # 3. 드롭박스 활성화 (값이 바뀌거나 선택되는 행위 자체가 트리거)
    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    
    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # --- [메인 화면] ---
    st.title("📖 Great Gatsby Audio Guide")

    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
            <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 시작 큐 사인</p>
            <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.5em;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        s_disp = format_seconds(tgt.get('start_sec', 0))
        e_disp = format_seconds(tgt.get('end_sec', 0))
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {s_disp} ~ {e_disp}")
        
        # 4. 재생 버튼 활성화 (눌리는 순간 v_key 갱신 트리거 발생)
        if st.button("▶️ 이 구간 처음부터 다시 재생", use_container_width=True):
            st.session_state.v_key = str(time.time())
            st.rerun()

    with col2:
        s_val, e_val = str(tgt.get('start_sec', 0)), str(tgt.get('end_sec', 0))
        
        # [기존 API 활용] loop 파라미터는 토글 상태값(loop_active)에 따라 결정
        # playlist={v_id}가 있어야만 loop=1이 정상 작동합니다.
        params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&rel=0"
        
        if loop_active:
            params += "&loop=1"  # 토글 ON: 구간 끝에서 자동 리셋 루틴 활성화
        else:
            params += "&loop=0"  # 토글 OFF: 활성화 루틴 없이 그대로 재생 멈춤

        # 최종 URL (트리거 발생 시 v_key가 바뀌어 영상이 새로 시작됨)
        final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"

        components.html(f"""
            <iframe width="100%" height="450" src="{final_src}" 
            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
        """, height=460)
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
