import streamlit as st
import json
import os
import time
import streamlit.components.v1 as components

# 1. 시간 변환 (145 -> 2:25) - 에러 방지용 예외처리 포함
def format_time(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except (ValueError, TypeError):
        return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")

# --- [상태 관리 및 쿼리 파라미터 청소] ---
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# 리셋 신호(trigger=reset)가 오면 상태를 끄고 주소창을 완전히 비움
if st.query_params.get("trigger") == "reset":
    st.session_state.is_playing = False
    for k in list(st.query_params.keys()):
        del st.query_params[k]
    st.rerun()

# 2. 데이터 로드 및 변수 설정
JSON_FILE = "final_mapping.json"
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # 사이드바 설정 (모든 값을 문자열로 관리하여 비교 오류 방지)
    st.sidebar.header("⚙️ Settings")
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    
    get_opts = lambda key, filters={}: sorted(list(set(str(d[key]) for d in r_data if all(str(d[k]) == v for k, v in filters.items()))))
    
    day = st.sidebar.select_slider("📅 Day", options=get_opts('Day'))
    rnd = st.sidebar.select_slider("🔁 Round", options=get_opts('ROUND', {'Day': day}))
    turn = st.sidebar.select_slider("🔢 회차", options=get_opts('회차', {'Day': day, 'ROUND': rnd}))

    # 타겟 데이터 추출
    tgt = next(d for d in r_data if str(d['Day']) == day and str(d['ROUND']) == rnd and str(d['회차']) == turn)
    s_val, e_val = int(float(tgt.get('start_sec',
