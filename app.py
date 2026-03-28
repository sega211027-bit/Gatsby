import streamlit as st
import json
import os
import time
import streamlit.components.v1 as components

# --- [1. 시간 변환 함수: 데이터 오류 방지] ---
def format_seconds(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except:
        return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# --- [2. 세션 상태 관리: 재생 트리거 정교화] ---
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())
if 'last_selected_id' not in st.session_state:
    st.session_state.last_selected_id = None

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바: 설정 및 선택] ---
    st.sidebar.header("📍 제어판")
    
    # 1. 무한 반복 토글 (상태값만 변경, 트리거 아님)
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    
    # 2. 상태 표시 램프
    if loop_active:
        st.sidebar.markdown("🟢 **상태: 무한반복 ON**")
    else:
        st.sidebar.markdown("🔴 **상태: 무한반복 OFF**")

    st.sidebar.divider()

    # 3. 드롭박스 선택
    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    
    # [핵심 로직] 드롭박스 값이 실제로 바뀌었을 때만 영상 리셋 트리거 발생
    current_id = f"{day}-{rnd}-{turn}"
    if st.session_state.last_selected_id != current_id:
        st.session_state.v_key = str(time.time()) # 처음부터 재생되도록 키 갱신
        st.session_state.last_selected_id = current_id

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # --- [메인 화면 영역] ---
    st.title("📖 Great Gatsby Audio Guide")

    # 시작 문구 강조 박스
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
            <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 이 단어가 들리면 낭
