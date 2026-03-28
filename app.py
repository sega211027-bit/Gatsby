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
    # PLAYING 상태일 때만 설정을 잠금
    is_locked = st.session_state.app_status == "PLAYING"

    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False, disabled=is_locked)
    loop_label = "✅ 무한 반복 ON" if loop_active else "❌ 무한 반복 OFF"
    st.sidebar.markdown(f"### {loop_label}")
    
    st.sidebar.divider()
    status_map = {"READY": "⚪ 대기 중", "PLAYING": "🔴 재생 중", "DONE": "🟢 완료"}
    st.sidebar.markdown(f"### 상태: {status_map.get(st.session_state.app_status)}")

    def safe_select_slider(label, items, disabled):
        options = sorted(list(set(items)))
        return st.sidebar.select_slider(label, options=options, value=options[0], disabled=disabled) if len(options) > 1 else options[0]

    day = safe_select_slider("📅 Day", [d['Day'] for d in r_data], is_locked)
    rnd = safe_select_slider("🔁 Round", [d['ROUND'] for d in r_data if d['Day'] == day], is_locked)
    turn = safe_select_slider("🔢 회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd], is_locked)

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [메인 UI: 초대형 숫자 및 문구] ---
    st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 20px; border-radius: 20px; border-left: 15px solid #007bff; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div><span style="font-size: 1.5em; color: #666;">Day</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff;">{day}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">ROUND</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff;">{rnd}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">회차</span><br><span style="font-size: 5.5em; font-weight: 900; color: #28a745;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 4px solid #eee; text-align: center; margin-bottom: 20px;">
            <p style="color: #ff6b6b; font-size: 1.5em; font-weight: bold; margin-bottom: 5px;">📍 시작 문구</p>
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #333; font-size: 3.5em; margin: 0;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"👤 **담당:** {tgt.get('담당자', '미지정')}\n🕒 **구간:** {format_seconds(s_val)} ~ {format_seconds(e_val)}")
        
        st.markdown(f"""
            <style>
                div.stButton > button[kind="primary"] {{ height: 120px !important; font-size: 40px !important; background-color: #28a745 !important; color: white !important; border-radius: 20px !important; }}
                div.stButton > button[kind="secondary"] {{ height: 120px !important; font-size: 35px !important; background-color: #dc3545 !important; color: white !important; border-radius: 20px !important; }}
            </style>
        """, unsafe_allow_html=True)

        if st.session_state.app_status != "PLAYING":
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.v_key = str(int(time.time()))
                st.session_state.app_status = "PLAYING"
                st.rerun()
        else:
            if st.button("⏹ STOP", use_container_width=True, type="secondary"):
                st.session_state.app_status = "READY"
                st.rerun()

    with col2:
        if st.session_state.app_status == "PLAYING":
            # [구간 반복 핵심 해결]
            # 무한 반복 시 playlist 파라미터를 쓰면 0초로 가버리는 버그가 있습니다. 
            # loop=1을 빼고, 대신 iframe 내부에서 '영상 끝=시작점으로 이동' 하도록 강제하는 것이 좋으나
            # URL 방식에서는 playlist={v_id}&loop=1이 공식입니다. 
            # 단, start와 end를 주소 뒤에 한 번 더 확실히 명시합니다.
            loop_p = f"&playlist={v_id}&loop=1" if loop_active else "&loop=0"
            final_src = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&mute=0&rel=0&enablejsapi=1{loop_p}&v={st.session_state.v_key}"
            
            components.html(f"""
                <iframe width="100%" height="450" src="{final_src}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
            """, height=460)
            
            # [자동 리셋 기능]
            if not loop_active:
                duration = e_val - s_val
                st.write(f"⏳ **연습 종료 후 자동 리셋까지: {int(duration)}초**")
                time.sleep(max(duration, 1) + 2) # 로딩시간 고려 2초 여유
                st.session_state.app_status = "READY" # DONE 대신 READY로 바로 돌려보냄
                st.rerun()
        else:
            st.warning("대기 중... 설정을 확인하고 START를 누르세요.")

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
