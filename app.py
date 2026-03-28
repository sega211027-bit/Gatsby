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

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# 세션 상태 초기화
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바 영역] ---
    st.sidebar.header("📍 설정")
    
    # 1. 무한 반복 토글 (기본값: False)
    loop_active = st.sidebar.toggle("🔄 구간 무한 반복", value=False)
    
    # 2. 상태 표시 램프 (빨강/초록)
    if loop_active:
        st.sidebar.markdown("🔴 **현재 상태: 무한 반복 ON**")
        # 토글이 켜지는 순간 처음으로 돌아가기 위해 v_key 갱신 (기존 루틴 재활용)
        # 단, 매번 갱신되면 루프에 빠지므로 상태 변화 시점에만 작동하도록 구성 권장
    else:
        st.sidebar.markdown("🟢 **현재 상태: 무한 반복 OFF**")

    st.sidebar.divider()
    
    # 3. 데이터 선택 UI
    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # --- [메인 화면 영역] ---
    st.title("📖 Great Gatsby Audio Guide")

    # 시작 문구 강조 박스
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
            <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 이 단어가 들리면 낭독을 시작하세요</p>
            <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.5em;">
                "{tgt.get('phrase', '')}"
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        s_disp = format_seconds(tgt.get('start_sec', 0))
        e_disp = format_seconds(tgt.get('end_sec', 0))
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {s_disp} ~ {e_disp}")
        
        # [기존 루틴] 처음부터 다시 재생 버튼
        if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
            st.session_state.v_key = str(time.time())
            st.rerun()
        
        st.caption("※ 구간 종료 시 위 버튼을 눌러주세요.")

    with col2:
        s_val = str(tgt.get('start_sec', 0))
        e_val = str(tgt.get('end_sec', 0))
        
        # 무한 반복 여부에 따른 파라미터 구성
        # playlist={v_id}와 loop=1을 조합하면 유튜브 서버가 해당 구간을 반복합니다.
        params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&rel=0"
        if loop_active:
            params += "&loop=1"
        
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
