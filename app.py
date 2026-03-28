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

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
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
    
    # 사이드바 설정
    st.sidebar.header("⚙️ 컨트롤러")
    is_locked = st.session_state.app_status != "READY"

    loop_option = st.sidebar.selectbox("🔄 무한 반복", ["OFF (정지)", "ON (반복)"], index=0, disabled=is_locked)
    loop_active = "ON" in loop_option

    def safe_select_slider(label, items, disabled):
        options = sorted(list(set(items)))
        return st.sidebar.select_slider(label, options=options, value=options[0], disabled=disabled) if len(options) > 1 else options[0]

    day = safe_select_slider("📅 Day", [d['Day'] for d in r_data], is_locked)
    rnd = safe_select_slider("🔁 Round", [d['ROUND'] for d in r_data if d['Day'] == day], is_locked)
    turn = safe_select_slider("🔢 회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd], is_locked)

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val = int(float(tgt.get('start_sec', 0)))
    e_val = int(float(tgt.get('end_sec', 0)))

    # --- [메인 UI: 모바일 최적화 및 폰트 확대] ---
    st.title("📖 Great Gatsby Audio Guide")

    # 1. Day/Round/회차 숫자 (초대형)
    st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 15px; border-radius: 15px; border-left: 10px solid #007bff; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div style="text-align: center; margin: 5px;">
                    <span style="font-size: 1.1em; color: #555;">DAY</span><br>
                    <span style="font-size: 3.8em; font-weight: 900; color: #007bff;">{day}</span>
                </div>
                <div style="text-align: center; margin: 5px;">
                    <span style="font-size: 1.1em; color: #555;">ROUND</span><br>
                    <span style="font-size: 3.8em; font-weight: 900; color: #007bff;">{rnd}</span>
                </div>
                <div style="text-align: center; margin: 5px;">
                    <span style="font-size: 1.1em; color: #555;">회차</span><br>
                    <span style="font-size: 3.8em; font-weight: 900; color: #28a745;">{turn}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. 시작 문구 (초대형 및 강조 색상)
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 3px solid #eee; text-align: center; margin-bottom: 20px;">
            <p style="color: #ff6b6b; font-size: 1.3em; font-weight: bold; margin-bottom: 8px;">📍 이 단어가 들리면 낭독을 시작하세요</p>
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #333; font-size: 3em; margin: 0; line-height: 1.1;">
                "{tgt.get('phrase', '')}"
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {format_seconds(s_val)} ~ {format_seconds(e_val)}")
        
        # 버튼 로직
        if st.session_state.app_status == "READY":
            if st.button("▶️ START", use_container_width=True, type="primary"):
                st.session_state.v_key = str(int(time.time()))
                st.session_state.app_status = "PLAYING"
                st.rerun()
        
        elif st.session_state.app_status == "PLAYING":
            if st.button("⏹️ STOP", use_container_width=True):
                st.session_state.app_status = "READY"
                st.rerun()
            
            # 타이머 안내 (무한 반복 아닐 때만)
            if not loop_active:
                duration = e_val - s_val
                st.write(f"⏳ **연습 종료까지 {int(duration)}초**")
        
        elif st.session_state.app_status == "DONE":
            if st.button("🔄 다시 준비 (READY)", use_container_width=True):
                st.session_state.app_status = "READY"
                st.rerun()

    with col2:
        if st.session_state.app_status == "PLAYING":
            # [구간 해결] playlist를 제거하여 start/end가 확실히 동작하게 함
            final_src = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&rel=0&v={st.session_state.v_key}"
            
            components.html(f"""
                <iframe width="100%" height="400" src="{final_src}" 
                frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
            """, height=410)
            
            if not loop_active:
                duration = e_val - s_val
                time.sleep(max(duration, 1) + 1)
                st.session_state.app_status = "DONE"
                st.rerun()
        
        elif st.session_state.app_status == "DONE":
            # DONE 화면에도 시작 문구를 보여줌
            st.success(f"✅ DONE! 오늘의 '{tgt.get('phrase', '')}' 연습이 완료되었습니다.")
        else:
            # READY 화면
            st.warning("설정 확인 후 START 버튼을 눌러주세요")

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
