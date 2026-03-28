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
    
    # --- [사이드바 컨트롤러] ---
    st.sidebar.header("⚙️ 컨트롤러")
    is_locked = st.session_state.app_status != "READY"

    # 1. 무한반복 토글 & 텍스트 가변 표시
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False, disabled=is_locked)
    loop_text = "✅ 무한 반복 ON" if loop_active else "❌ 무한 반복 OFF"
    st.sidebar.markdown(f"**{loop_text}**")
    
    # 2. 신호등 상태 표시
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

    # --- [메인 UI: 폰트 크기 극대화] ---
    st.title("📖 Great Gatsby Audio Guide")

    # 숫자 강조 (제목보다 크게 설정)
    st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 25px; border-radius: 20px; border-left: 15px solid #007bff; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div style="margin: 10px;">
                    <span style="font-size: 1.5em; color: #666; font-weight: bold;">Day</span><br>
                    <span style="font-size: 5em; font-weight: 900; color: #007bff; line-height: 1;">{day}</span>
                </div>
                <div style="margin: 10px;">
                    <span style="font-size: 1.5em; color: #666; font-weight: bold;">ROUND</span><br>
                    <span style="font-size: 5em; font-weight: 900; color: #007bff; line-height: 1;">{rnd}</span>
                </div>
                <div style="margin: 10px;">
                    <span style="font-size: 1.5em; color: #666; font-weight: bold;">회차</span><br>
                    <span style="font-size: 5em; font-weight: 900; color: #28a745; line-height: 1;">{turn}</span>
                </div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 30px; border-radius: 15px; border: 4px solid #eee; text-align: center; margin-bottom: 25px;">
            <p style="color: #ff6b6b; font-size: 1.5em; font-weight: bold; margin-bottom: 10px;">📍 시작 문구</p>
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #333; font-size: 3.5em; margin: 0; line-height: 1.2;">
                "{tgt.get('phrase', '')}"
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n🕒 **구간:** {format_seconds(s_val)} ~ {format_seconds(e_val)}")
        
        # 버튼 스타일: START(녹색), STOP(빨강) + 초대형 크기
        st.markdown(f"""
            <style>
                /* START 버튼 (Primary) */
                div.stButton > button[kind="primary"] {{
                    height: 120px !important;
                    font-size: 40px !important;
                    background-color: #28a745 !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 20px !important;
                    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3) !important;
                }}
                /* STOP/RESET 버튼 (Secondary) */
                div.stButton > button[kind="secondary"] {{
                    height: 120px !important;
                    font-size: 35px !important;
                    background-color: #dc3545 !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 20px !important;
                    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3) !important;
                }}
            </style>
        """, unsafe_allow_html=True)

        if st.session_state.app_status == "READY":
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.v_key = str(int(time.time
