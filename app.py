import streamlit as st
import json
import os
import time

st.set_page_config(page_title="Gatsby Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# 버튼 클릭 시 영상을 리셋하기 위한 세션 키
if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # 선택 UI
    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    st.title("📖 Great Gatsby Audio Guide")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **구간:** {tgt['start_time']} ~ {tgt['end_time']}")
        
        # [핵심] 처음으로 돌리는 버튼
        if st.button("▶️ 이 구간 처음부터 다시 재생", use_container_width=True):
            st.session_state.v_key = str(time.time())
            st.rerun()

    with col2:
        s_val = str(tgt['start_sec'])
        e_val = str(tgt['end_sec'])
        
        # playlist 파라미터에 본인 v_id를 넣으면 end 시점에서 다음 영상으로 넘어가지 않고 멈추는 효과가 있습니다.
        # loop=0으로 설정하여 자동으로 다시 시작되는 것을 막습니다.
        params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&loop=0&rel=0"
        
        # t={v_key}를 통해 매번 새로운 주소로 인식시켜 멈춤 설정(end)이 무시되는 것을 방지합니다.
        final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"

        st.components.v1.html(f"""
            <iframe 
                width="100%" height="450" 
                src="{final_src}" 
                frameborder="0" 
                allow="autoplay; encrypted-media" 
                allowfullscreen>
            </iframe>
        """, height=460)

else:
    st.error("데이터 파일을 찾을 수 없습니다.")