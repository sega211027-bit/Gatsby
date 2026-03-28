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

# --- [세션 상태 관리] ---
if 'app_status' not in st.session_state:
    st.session_state.app_status = "READY"
if 'v_key' not in st.session_state:
    st.session_state.v_key = "0"

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    st.sidebar.header("⚙️ 컨트롤러")
    is_locked = st.session_state.app_status != "READY"

    # 1. 무한반복 토글 (다시 살림)
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False, disabled=is_locked)
    
    # 2. 신호등 상태 표시 (다시 살림)
    st.sidebar.divider()
    if st.session_state.app_status == "READY":
        st.sidebar.markdown("⚪ **상태: 대기 중 (READY)**")
    elif st.session_state.app_status == "PLAYING":
        st.sidebar.markdown("🔴 **상태: 재생 중 (PLAYING)**")
    else:
        st.sidebar.markdown("🟢 **상태: 연습 완료 (DONE)**")

    def safe_select_slider(label, items, disabled):
        options = sorted(list(set(items)))
        return st.sidebar.select_slider(label, options=options, value=options[0], disabled=disabled) if len(options) > 1 else options[0]

    day = safe_select_slider("📅 Day", [d['Day'] for d in r_data], is_locked)
    rnd = safe_select_slider("🔁 Round", [d['ROUND'] for d in r_data if d['Day'] == day], is_locked)
    turn = safe_select_slider("🔢 회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd], is_locked)

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val = int(float(tgt.get('start_sec', 0)))
    e_val = int(float(tgt.get('end_sec', 0)))

    # --- [메인 UI] ---
    st.title("📖 Great Gatsby Audio Guide")

    # 숫자 및 문구 표시 (모바일 최적화)
    st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 15px; border-radius: 15px; border-left: 10px solid #007bff; margin-bottom: 15px; text-align: center;">
            <span style="font-size: 1.2em; color: #555;">DAY {day} / ROUND {rnd} / 회차 {turn}</span>
        </div>
        <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; border: 3px solid #eee; text-align: center; margin-bottom: 20px;">
            <p style="color: #ff6b6b; font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">📍 시작 문구</p>
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #333; font-size: 3.2em; margin: 0;">
                "{tgt.get('phrase', '')}"
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n🕒 **구간:** {format_seconds(s_val)} ~ {format_seconds(e_val)}")
        
        # 버튼 크기 대폭 확대 (CSS 사용)
        st.markdown("""
            <style>
                div.stButton > button {
                    height: 100px !important;
                    font-size: 30px !important;
                    font-weight: bold !important;
                    border-radius: 15px !important;
                }
            </style>
        """, unsafe_allow_html=True)

        if st.session_state.app_status == "READY":
            if st.button("▶️ START", use_container_width=True, type="primary"):
                st.session_state.v_key = str(int(time.time()))
                st.session_state.app_status = "PLAYING"
                st.rerun()
        
        else:
            if st.button("⏹️ STOP / RESET", use_container_width=True):
                st.session_state.app_status = "READY"
                st.rerun()

    with col2:
        if st.session_state.app_status == "PLAYING":
            # [재생 안됨 해결] autoplay=1과 함께 mute=1을 넣어야 브라우저가 자동 재생을 허용합니다.
            # 루프를 위해 playlist={v_id}와 loop=1을 조건부로 추가
            loop_param = f"&playlist={v_id}&loop=1" if loop_active else "&loop=0"
            final_src = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&mute=0&rel=0&enablejsapi=1{loop_param}&v={st.session_state.v_key}"
            
            components.html(f"""
                <iframe width="100%" height="450" src="{final_src}" 
                frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
            """, height=460)
            
            if not loop_active:
                duration = e_val - s_val
                time.sleep(max(duration, 1) + 1)
                st.session_state.app_status = "DONE"
                st.rerun()
        
        elif st.session_state.app_status == "DONE":
            st.success("✅ 연습 완료! 다시 시작하려면 STOP/RESET을 눌러주세요.")
        else:
            st.warning("대기 중... START를 누르면 영상이 로드됩니다.")

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
