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

# --- [2. 세션 상태 관리: 앱의 현재 '단계' 정의] ---
# 상태 종류: "READY" (준비), "PLAYING" (재생 중), "DONE" (완료)
if 'app_status' not in st.session_state:
    st.session_state.app_status = "READY"
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바 설정] ---
    st.sidebar.header("⚙️ 컨트롤러")
    
    # 재생 중이거나 완료 상태일 때는 설정 변경 불가
    is_locked = st.session_state.app_status != "READY"

    loop_option = st.sidebar.selectbox("🔄 무한 반복", ["OFF (정지)", "ON (반복)"], index=0, disabled=is_locked)
    loop_active = "ON" in loop_option

    st.sidebar.divider()

    def safe_select_slider(label, items, disabled):
        options = sorted(list(set(items)))
        return st.sidebar.select_slider(label, options=options, value=options[0], disabled=disabled) if len(options) > 1 else options[0]

    day = safe_select_slider("📅 Day", [d['Day'] for d in r_data], is_locked)
    rnd = safe_select_slider("🔁 Round", [d['ROUND'] for d in r_data if d['Day'] == day], is_locked)
    turn = safe_select_slider("🔢 회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd], is_locked)

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # --- [메인 UI: 모바일 최적화 숫자] ---
    st.title("📖 Great Gatsby Audio Guide")

    st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 20px; border-radius: 15px; border-left: 10px solid #007bff; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div style="text-align: center;"><span style="font-size: 1.1em; color: #555;">DAY</span><br><span style="font-size: 3.5em; font-weight: 900; color: #007bff;">{day}</span></div>
                <div style="text-align: center;"><span style="font-size: 1.1em; color: #555;">ROUND</span><br><span style="font-size: 3.5em; font-weight: 900; color: #007bff;">{rnd}</span></div>
                <div style="text-align: center;"><span style="font-size: 1.1em; color: #555;">회차</span><br><span style="font-size: 3.5em; font-weight: 900; color: #28a745;">{turn}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {format_seconds(tgt.get('start_sec', 0))} ~ {format_seconds(tgt.get('end_sec', 0))}")
        
        # --- [버튼 로직: START / STOP] ---
        if st.session_state.app_status == "READY":
            if st.button("▶️ START", use_container_width=True, type="primary"):
                st.session_state.app_status = "PLAYING"
                st.session_state.v_key = str(time.time())
                st.rerun()
        
        elif st.session_state.app_status == "PLAYING":
            if st.button("⏹️ STOP", use_container_width=True):
                st.session_state.app_status = "READY"
                st.rerun()
            
            # 자동 종료 타이머 (무한 반복이 아닐 때만)
            if not loop_active:
                duration = float(tgt.get('end_sec', 0)) - float(tgt.get('start_sec', 0))
                st.write(f"⏳ **연습 종료까지 {int(duration)}초**")
                # 영상을 먼저 보여주기 위해 타이머를 뒤로 배치하거나 처리
        
        elif st.session_state.app_status == "DONE":
            if st.button("🔄 처음으로 (READY)", use_container_width=True):
                st.session_state.app_status = "READY"
                st.rerun()

    with col2:
        # 상태에 따른 화면 전환
        if st.session_state.app_status == "PLAYING":
            params = f"start={tgt.get('start_sec', 0)}&end={tgt.get('end_sec', 0)}&autoplay=1&playlist={v_id}&loop={'1' if loop_active else '0'}"
            final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"
            
            components.html(f'<iframe width="100%" height="400" src="{final_src}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', height=410)
            
            # 여기서 타이머를 돌리면 영상이 먼저 뜹니다.
            if not loop_active:
                duration = float(tgt.get('end_sec', 0)) - float(tgt.get('start_sec', 0))
                time.sleep(duration + 1)
                st.session_state.app_status = "DONE"
                st.rerun()

        elif st.session_state.app_status == "DONE":
            st.markdown(f"""
                <div style="height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #f8f9fa; border-radius: 15px; border: 2px dashed #28a745;">
                    <h1 style="color: #28a745; font-size: 3em;">✅ DONE</h1>
                    <p style="color: #718096; font-size: 1.2em;">오늘의 연습이 끝났습니다!</p>
                </div>
            """, unsafe_allow_html=True)
        
        else: # READY 상태
            st.markdown(f"""
                <div style="height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #ffffff; border-radius: 15px; border: 2px solid #eee;">
                    <h2 style="color: #007bff;">READY</h2>
                    <p style="color: #999;">설정 확인 후 START 버튼을 눌러주세요</p>
                    <div style="font-family: serif; font-style: italic; font-size: 1.5em; margin-top: 20px;">"{tgt.get('phrase', '')}"</div>
                </div>
            """, unsafe_allow_html=True)

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
