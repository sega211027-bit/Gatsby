import streamlit as st
import json
import os
import time
import streamlit.components.v1 as components

# 시간 변환 함수
def format_seconds(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except: return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# --- [세션 상태 관리] ---
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'v_key' not in st.session_state:
    st.session_state.v_key = "0"

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바 컨트롤] ---
    st.sidebar.header("⚙️ 컨트롤러")
    loop_active = st.sidebar.toggle("🔄 무한 반복", value=False)
    
    # 선택 도구
    def get_opt(label, items):
        opts = sorted(list(set(items)))
        return st.sidebar.select_slider(label, options=opts) if len(opts) > 1 else opts[0]

    day = get_opt("📅 Day", [d['Day'] for d in r_data])
    rnd = get_opt("🔁 Round", [d['ROUND'] for d in r_data if d['Day'] == day])
    turn = get_opt("🔢 회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [메인 UI: 초대형 가독성] ---
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 25px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.5em; color: #666;">Day</span><br><span style="font-size: 6em; font-weight: 900; color: #007bff;">{day}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">ROUND</span><br><span style="font-size: 6em; font-weight: 900; color: #007bff;">{rnd}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">회차</span><br><span style="font-size: 6em; font-weight: 900; color: #28a745;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 30px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 25px;">
            <p style="color: #ff4b4b; font-size: 1.4em; font-weight: bold; margin-bottom: 10px;">📍 Starting Phrase</p>
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #222; font-size: 4em; margin: 0; line-height: 1.2;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"🕒 **구간:** {format_seconds(s_val)} ~ {format_seconds(e_val)}")
        
        # 버튼 디자인: START(초록), STOP(빨강)
        st.markdown("""
            <style>
                div.stButton > button[kind="primary"] { height: 120px !important; font-size: 40px !important; background-color: #28a745 !important; border-radius: 20px !important; border: none !important; }
                div.stButton > button[kind="secondary"] { height: 120px !important; font-size: 35px !important; background-color: #dc3545 !important; color: white !important; border-radius: 20px !important; border: none !important; }
            </style>
        """, unsafe_allow_html=True)

        if not st.session_state.is_playing:
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.is_playing = True
                st.session_state.v_key = str(int(time.time()))
                st.rerun()
        else:
            if st.button("⏹ STOP", use_container_width=True, type="secondary"):
                st.session_state.is_playing = False
                st.rerun()

    with col2:
        if st.session_state.is_playing:
            loop_p = f"&playlist={v_id}&loop=1" if loop_active else "&loop=0"
            final_src = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&mute=0&rel=0&enablejsapi=1{loop_p}&v={st.session_state.v_key}"
            
            components.html(f'<iframe width="100%" height="480" src="{final_src}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', height=490)
            
            # [가속화 리셋 로직]
            if not loop_active:
                duration = e_val - s_val
                # 영상이 완전히 멈추기 1.5초 전에 버튼을 녹색으로 미리 리셋
                time.sleep(max(duration - 1.5, 0.5)) 
                st.session_state.is_playing = False
                st.rerun()
        else:
            st.warning("설정 확인 후 START 버튼을 누르세요.")
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
