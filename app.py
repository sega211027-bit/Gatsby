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
if 'v_key' not in st.session_state:
    st.session_state.v_key = "0"
if 'run_video' not in st.session_state:
    st.session_state.run_video = False

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바: 토글 및 설정] ---
    st.sidebar.header("⚙️ 컨트롤러")
    
    # 무한반복 토글 (글자 가변)
    loop_active = st.sidebar.toggle("무한 반복 모드", value=False)
    loop_status_txt = "✅ 무한 반복 ON" if loop_active else "❌ 무한 반복 OFF"
    st.sidebar.markdown(f"### {loop_status_txt}")
    
    st.sidebar.divider()

    # 구간 선택 슬라이더
    def get_opt(label, items):
        opts = sorted(list(set(items)))
        return st.sidebar.select_slider(label, options=opts, value=opts[0]) if len(opts) > 1 else opts[0]

    day = get_opt("📅 Day", [d['Day'] for d in r_data])
    rnd = get_opt("🔁 Round", [d['ROUND'] for d in r_data if d['Day'] == day])
    turn = get_opt("🔢 회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [메인 UI: 초대형 폰트] ---
    st.title("📖 Great Gatsby Audio Guide")

    # Day, Round, 회차 강조 박스
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
        
        # 버튼 스타일 (녹색 START / 빨간색 STOP)
        st.markdown("""
            <style>
                div.stButton > button[kind="primary"] { height: 100px !important; font-size: 35px !important; background-color: #28a745 !important; color: white !important; border-radius: 20px !important; }
                div.stButton > button[kind="secondary"] { height: 100px !important; font-size: 30px !important; background-color: #dc3545 !important; color: white !important; border-radius: 20px !important; }
            </style>
        """, unsafe_allow_html=True)

        if not st.session_state.run_video:
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.run_video = True
                st.session_state.v_key = str(int(time.time()))
                st.rerun()
        else:
            if st.button("⏹ STOP", use_container_width=True, type="secondary"):
                st.session_state.run_video = False
                st.rerun()

    with col2:
        if st.session_state.run_video:
            # 구간 반복 버그 해결을 위한 URL 조합 (playlist 제거 후 다시 테스트)
            loop_p = f"&playlist={v_id}&loop=1" if loop_active else "&loop=0"
            # v= 파라미터로 브라우저 캐시를 깨서 즉시 재생 유도
            final_src = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&mute=0&rel=0&enablejsapi=1{loop_p}&v={st.session_state.v_key}"
            
            components.html(f"""
                <iframe width="100%" height="450" src="{final_src}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
            """, height=460)
            
            # 무한 반복이 아닐 때만 자동 종료 타이머 작동
            if not loop_active:
                duration = e_val - s_val
                time.sleep(max(duration, 1) + 2)
                st.session_state.run_video = False # 영상 끝나면 자동으로 STOP 상태로 전환
                st.rerun()
        else:
            st.warning("대기 중... 설정을 확인하고 START를 누르세요.")

else:
    st.error("데이터 파일을 찾을 수 없습니다.")
