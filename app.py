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
# is_broadcasting이 True면 영상 재생(빨간 버튼), False면 대기(초록 버튼)
if 'is_broadcasting' not in st.session_state:
    st.session_state.is_broadcasting = False
if 'v_key' not in st.session_state:
    st.session_state.v_key = "0"

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바 설정] ---
    st.sidebar.header("⚙️ 컨트롤러")
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    
    # 설정 잠금 (재생 중에는 슬라이더 조작 방지)
    is_locked = st.session_state.is_broadcasting

    def get_opt(label, items):
        opts = sorted(list(set(items)))
        return st.sidebar.select_slider(label, options=opts, disabled=is_locked) if len(opts) > 1 else opts[0]

    day = get_opt("📅 Day", [d['Day'] for d in r_data])
    rnd = get_opt("🔁 Round", [d['ROUND'] for d in r_data if d['Day'] == day])
    turn = get_opt("🔢 회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [메인 UI: 신호등 및 대형 폰트] ---
    
    # 1. 신호등 표시 (상태를 시각화하여 초기화 여부 확인)
    if st.session_state.is_broadcasting:
        signal_color, signal_text, signal_shadow = "#ff4b4b", "ON AIR (재생 중)", "0 0 15px #ff4b4b"
    else:
        signal_color, signal_text, signal_shadow = "#888", "READY (대기 중)", "none"

    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; background: #222; padding: 10px; border-radius: 50px; width: 280px; margin: 0 auto 20px; border: 2px solid {signal_color};">
            <div style="width: 18px; height: 18px; background: {signal_color}; border-radius: 50%; margin-right: 12px; box-shadow: {signal_shadow};"></div>
            <span style="color: {signal_color}; font-weight: bold; font-size: 1.1em; letter-spacing: 1px;">{signal_text}</span>
        </div>
    """, unsafe_allow_html=True)

    # 2. 초대형 숫자 및 시작 문구
    st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 20px; border-radius: 20px; border-left: 15px solid #007bff; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
                <div><span style="font-size: 1.5em; color: #666;">Day</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff; line-height: 1;">{day}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">ROUND</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff; line-height: 1;">{rnd}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">회차</span><br><span style="font-size: 5.5em; font-weight: 900; color: #28a745; line-height: 1;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 4px solid #eee; text-align: center; margin-bottom: 20px;">
            <p style="color: #ff6b6b; font-size: 1.5em; font-weight: bold; margin-bottom: 5px;">📍 시작 문구</p>
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #333; font-size: 3.5em; margin: 0;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"🕒 **구간:** {format_seconds(s_val)} ~ {format_seconds(e_val)}")
        
        # 버튼 스타일 정의
        st.markdown("""
            <style>
                div.stButton > button[kind="primary"] { height: 110px !important; font-size: 38px !important; background-color: #28a745 !important; color: white !important; border-radius: 20px !important; }
                div.stButton > button[kind="secondary"] { height: 110px !important; font-size: 32px !important; background-color: #dc3545 !important; color: white !important; border-radius: 20px !important; }
            </style>
        """, unsafe_allow_html=True)

        if not st.session_state.is_broadcasting:
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.is_broadcasting = True
                st.session_state.v_key = str(int(time.time()))
                st.rerun()
        else:
            if st.button("⏹ STOP", use_container_width=True, type="secondary"):
                st.session_state.is_broadcasting = False
                st.rerun()

    with col2:
        if st.session_state.is_broadcasting:
            # 유튜브 재생 주소 설정
            loop_p = f"&playlist={v_id}&loop=1" if loop_active else "&loop=0"
            final_src = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&mute=0&rel=0&enablejsapi=1{loop_p}&v={st.session_state.v_key}"
            
            components.html(f'<iframe width="100%" height="450" src="{final_src}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', height=460)
            
            # [핵심 로직] 무한 반복이 아닐 때, 영상 종료 시점에 버튼을 자동 리셋
            if not loop_active:
                duration = e_val - s_val
                # 영상 재생 시간만큼 기다린 후 상태를 강제로 False로 변경
                time.sleep(max(duration, 1) + 2) 
                st.session_state.is_broadcasting = False # 여기서 버튼이 다시 START(초록)로 바뀝니다.
                st.rerun()
        else:
            st.warning("설정 확인 후 START 버튼을 누르세요.")

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
