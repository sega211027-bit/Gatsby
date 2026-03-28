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

# --- [2. 세션 상태 관리] ---
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    st.sidebar.header("⚙️ 컨트롤러")
    lock = st.session_state.is_playing

    # 1. 무한반복 설정
    loop_option = st.sidebar.selectbox("🔄 무한 반복 설정", ["OFF (정지)", "ON (반복)"], index=0, disabled=lock)
    loop_active = "ON" in loop_option

    st.sidebar.divider()

    # 2. 구간 선택 (Select Slider)
    def safe_select_slider(label, items, disabled):
        options = sorted(list(set(items)))
        if len(options) > 1:
            return st.sidebar.select_slider(label, options=options, value=options[0], disabled=disabled)
        else:
            st.sidebar.info(f"{label}: {options[0]}")
            return options[0]

    day = safe_select_slider("📅 Day 선택", [d['Day'] for d in r_data], lock)
    r_list = [d['ROUND'] for d in r_data if d['Day'] == day]
    rnd = safe_select_slider("🔁 Round 선택", r_list, lock)
    t_list = [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd]
    turn = safe_select_slider("🔢 회차 선택", t_list, lock)

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # --- [메인 UI: 폰트 크기 대폭 확대] ---
    st.title("📖 Great Gatsby Audio Guide")

    # 모바일 가독성을 위한 대형 숫자 헤더
    st.markdown(f"""
        <div style="background-color: #f0f7ff; padding: 20px; border-radius: 15px; border-left: 10px solid #007bff; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
                <div style="text-align: center; margin: 10px;">
                    <span style="font-size: 1.2em; color: #555;">DAY</span><br>
                    <span style="font-size: 3.5em; font-weight: 900; color: #007bff;">{day}</span>
                </div>
                <div style="text-align: center; margin: 10px;">
                    <span style="font-size: 1.2em; color: #555;">ROUND</span><br>
                    <span style="font-size: 3.5em; font-weight: 900; color: #007bff;">{rnd}</span>
                </div>
                <div style="text-align: center; margin: 10px;">
                    <span style="font-size: 1.2em; color: #555;">회차</span><br>
                    <span style="font-size: 3.5em; font-weight: 900; color: #28a745;">{turn}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 시작 문구 강조 박스
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #eee; text-align: center; margin-bottom: 20px;">
            <p style="color: #888; margin-bottom: 5px;">📍 이 소리가 들리면 시작하세요</p>
            <h2 style="font-family: 'Times New Roman', serif; font-style: italic; color: #333; font-size: 2em; margin: 0;">
                "{tgt.get('phrase', '')}"
            </h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {format_seconds(tgt.get('start_sec', 0))} ~ {format_seconds(tgt.get('end_sec', 0))}")
        
        if not st.session_state.is_playing:
            if st.button("🚀 낭독 시작 (잠금)", use_container_width=True, type="primary"):
                st.session_state.is_playing = True
                st.session_state.v_key = str(time.time())
                st.rerun()
        else:
            if st.button("⏹️ 연습 중단", use_container_width=True):
                st.session_state.is_playing = False
                st.rerun()
            
            if not loop_active:
                duration = float(tgt.get('end_sec', 0)) - float(tgt.get('start_sec', 0))
                st.write(f"⏳ **자동 종료까지 {int(duration)}초**")
                time.sleep(duration + 1)
                st.session_state.is_playing = False
                st.rerun()

    with col2:
        if st.session_state.is_playing:
            params = f"start={tgt.get('start_sec', 0)}&end={tgt.get('end_sec', 0)}&autoplay=1&playlist={v_id}&loop={'1' if loop_active else '0'}"
            final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"
            components.html(f'<iframe width="100%" height="400" src="{final_src}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', height=410)
        else:
            # 영상이 사라진 후의 안내 화면 (치워버리기 로직)
            st.markdown(f"""
                <div style="height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #f8f9fa; border-radius: 15px; border: 2px dashed #cbd5e0;">
                    <h2 style="color: #28a745;">✅ 연습 완료!</h2>
                    <p style="color: #718096; font-size: 1.1em;">다음 구간을 선택하거나 다시 시작하세요.</p>
                    <div style="margin-top: 20px; padding: 10px 20px; background: white; border-radius: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        📖 Great Gatsby Reading Cycle
                    </div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
