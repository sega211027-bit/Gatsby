import streamlit as st
import json
import os

# 1. 설정 및 기본 함수
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")

def format_time(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except: return "0:00"

# 2. 데이터 로드
JSON_FILE = "final_mapping.json"
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # 사이드바 설정
    st.sidebar.header("⚙️ Settings")
    day_opts = sorted(list(set(str(d['Day']) for d in r_data)))
    day = st.sidebar.select_slider("📅 Day", options=day_opts)
    
    rnd_opts = sorted(list(set(str(d['ROUND']) for d in r_data if str(d['Day']) == day)))
    rnd = st.sidebar.select_slider("🔁 Round", options=rnd_opts)
    
    turn_opts = sorted(list(set(str(d['회차']) for d in r_data if str(d['Day']) == day and str(d['ROUND']) == rnd)))
    turn = st.sidebar.select_slider("🔢 회차", options=turn_opts)

    tgt = next(d for d in r_data if str(d['Day']) == day and str(d['ROUND']) == rnd and str(d['회차']) == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # 3. UI 대시보드 (디자인 유지)
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 20px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 15px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.2em; color: #666;">Day</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff;">{day}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">ROUND</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff;">{rnd}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">회차</span><br><span style="font-size: 5.5em; font-weight: 900; color: #28a745;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 20px;">
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; font-size: 3.2em; margin: 0;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"📍 구간: {format_time(s_val)} ~ {format_time(e_val)}")
        st.write("슬라이더를 조작하면 아래 영상이 자동으로 해당 구간으로 설정됩니다.")
        st.markdown("---")
        st.caption("주의: 자동 반복/자동 종료 기능은 현재 파이썬 버전과의 충돌로 인해 수동 조작으로 대체되었습니다.")

    with col2:
        # [핵심 변경] 에러를 유발하는 자바스크립트 대신 표준 iframe 주소 방식 사용
        # 이 방식은 자바스크립트 엔진을 직접 건드리지 않아 TypeError가 발생하지 않습니다.
        yt_url = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&rel=0"
        
        st.markdown(f"""
            <iframe width="100%" height="450" src="{yt_url}" 
            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>
            </iframe>
        """, unsafe_allow_html=True)

else:
    st.error("JSON 파일을 찾을 수 없습니다.")
