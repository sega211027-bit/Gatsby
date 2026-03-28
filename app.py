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

# --- [2. 세션 상태 관리: 재생 트리거 독립] ---
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())
if 'last_selected_id' not in st.session_state:
    st.session_state.last_selected_id = None

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바: 새로운 인터페이스] ---
    st.sidebar.header("⚙️ 컨트롤러")
    
    # 1. 무한반복 설정 (드롭박스 방식 - 상태값만 변경)
    loop_option = st.sidebar.selectbox(
        "🔄 무한 반복 설정",
        ["OFF (구간 종료 시 정지)", "ON (구간 자동 반복)"],
        index=0
    )
    loop_active = True if "ON" in loop_option else False
    
    # 시각적 램프 표시
    if loop_active:
        st.sidebar.markdown("🟢 **상태: 무한반복 ON**")
    else:
        st.sidebar.markdown("🔴 **상태: 무한반복 OFF**")

    st.sidebar.divider()

    # 2. 셀렉트 슬라이더 (데이터에 있는 값만 정확히 표시)
    def safe_select_slider(label, items):
        # 중복 제거 및 정렬
        options = sorted(list(set(items)))
        if len(options) > 1:
            # select_slider는 리스트 내의 실제 값들만 슬라이더로 연결합니다.
            return st.sidebar.select_slider(label, options=options, value=options[0])
        else:
            st.sidebar.info(f"{label}: {options[0]}")
            return options[0]

    day = safe_select_slider("📅 Day 선택", [d['Day'] for d in r_data])
    
    r_list = [d['ROUND'] for d in r_data if d['Day'] == day]
    rnd = safe_select_slider("🔁 Round 선택", r_list)
    
    t_list = [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd]
    turn = safe_select_slider("🔢 회차 선택", t_list)
    
    # [재생 트리거] 슬라이더로 선택된 ID가 바뀔 때만 영상 리셋
    current_id = f"{day}-{rnd}-{turn}"
    if st.session_state.last_selected_id != current_id:
        st.session_state.v_key = str(time.time())
        st.session_state.last_selected_id = current_id

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # --- [메인 화면] ---
    st.title("📖 Great Gatsby Audio Guide")

    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
            <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 이 단어가 들리면 낭독을 시작하세요</p>
            <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.5em; margin: 0;">
                "{tgt.get('phrase', '')}"
            </h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        s_disp = format_seconds(tgt.get('start_sec', 0))
        e_disp = format_seconds(tgt.get('end_sec', 0))
        st.info(f"👤 **낭독자:** {tgt.get('담당자', '미지정')}\n\n🕒 **구간:** {s_disp} ~ {e_disp}")
        
        if st.button("▶️ 처음부터 재생", use_container_width=True):
            st.session_state.v_key = str(time.time())
            st.rerun()

    with col2:
        s_val, e_val = str(tgt.get('start_sec', 0)), str(tgt.get('end_sec', 0))
        params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&rel=0"
        params += "&loop=1" if loop_active else "&loop=0"

        # v_key가 유지되면(무한반복 설정만 바꿀 때) 영상이 처음으로 튀지 않습니다.
        final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"

        components.html(f"""
            <iframe width="100%" height="450" src="{final_src}" 
            frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
        """, height=460)

else:
    st.error("데이터 파일을 찾을 수 없습니다. GitHub에 'final_mapping.json'이 있는지 확인해주세요.")
