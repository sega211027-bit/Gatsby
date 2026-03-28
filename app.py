import streamlit as st
import json
import os
import time

# --- [1. 시간 변환 함수: KeyError 근본 해결] ---
def format_seconds(seconds):
    try:
        seconds = int(seconds)
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    except:
        return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 세션 키 설정 (리로딩용)
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    st.title("📖 Great Gatsby Audio Guide")
    
    # 데이터 선택
    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    # [수정] KeyError 방지: 직접 계산 방식 사용
    s_time_disp = format_seconds(tgt['start_sec'])
    e_time_disp = format_seconds(tgt['end_sec'])

    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
            <p style="color: #666; font-size: 1.1em; margin-bottom: 10px;">📍 이 단어가 들리면 낭독을 시작하세요</p>
            <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">"{tgt['phrase']}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **구간:** {s_time_disp} ~ {e_time_disp}")
        
        # [수정] 버튼 클릭 시 타임스탬프를 갱신하여 iframe 리로드 강제
        if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
            st.session_state.v_key = str(time.time())
            st.rerun()
        
        st.caption("※ 구간이 끝나고 영상이 멈추면 위 버튼을 눌러주세요.")

    with col2:
        s_val = str(tgt['start_sec'])
        e_val = str(tgt['end_sec'])
        
        # [핵심] 멈춤(end) 파라미터가 가장 잘 먹히는 파라미터 조합
        # playlist를 함께 주어야 end 시점에서 다음 영상으로 넘어가지 않고 멈춥니다.
        params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&rel=0&iv_load_policy=3"
        final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"

        import streamlit.components.v1 as components
        components.html(f"""
            <iframe 
                width="100%" height="450" 
                src="{final_src}" 
                frameborder="0" 
                allow="autoplay; encrypted-media; picture-in-picture" 
                allowfullscreen>
            </iframe>
        """, height=460)
else:
    st.error("데이터 파일이 없습니다.")