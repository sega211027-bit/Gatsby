import streamlit as st
import json
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# --- [상태 관리] ---
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# 자바스크립트가 보내는 종료 신호를 받기 위한 처리
# (컴포넌트의 반환값을 이용해 새로고침 없이 상태 변경)
def on_video_end():
    st.session_state.is_playing = False

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [사이드바 컨트롤] ---
    st.sidebar.header("⚙️ 컨트롤러")
    loop_active = st.sidebar.toggle("🔄 무한 반복", value=False)
    
    day = st.sidebar.select_slider("📅 Day", options=sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.select_slider("🔁 Round", options=sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.select_slider("🔢 회차", options=sorted(list(set(d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd))))

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [메인 UI] ---
    # (Day, Round 표시 박스 생략 - 기존과 동일)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 버튼 스타일
        st.markdown("""
            <style>
                div.stButton > button[kind="primary"] { height: 120px !important; font-size: 40px !important; background-color: #28a745 !important; border-radius: 20px !important; }
                div.stButton > button[kind="secondary"] { height: 120px !important; font-size: 35px !important; background-color: #dc3545 !important; color: white !important; border-radius: 20px !important; }
            </style>
        """, unsafe_allow_html=True)

        if not st.session_state.is_playing:
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.session_state.is_playing = True
                st.rerun()
        else:
            if st.button("⏹ STOP", use_container_width=True, type="secondary"):
                st.session_state.is_playing = False
                st.rerun()

    with col2:
        if st.session_state.is_playing:
            # HTML/JS 감시 엔진 (가장 가벼운 방식)
            html_watcher = f"""
            <div id="player"></div>
            <script>
                var tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = document.getElementsByTagName('script')[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

                var player;
                function onYouTubeIframeAPIReady() {{
                    player = new YT.Player('player', {{
                        height: '450', width: '100%', videoId: '{v_id}',
                        playerVars: {{ 'start': {s_val}, 'end': {e_val}, 'autoplay': 1, 'controls': 1, 'rel': 0, 'enablejsapi': 1 }},
                        events: {{ 'onStateChange': function(event) {{
                            if (event.data == 0 && {str(not loop_active).lower()}) {{ sendEndSignal(); }}
                        }} }}
                    }});
                }}

                function sendEndSignal() {{
                    // Streamlit에 종료 신호를 보냄 (URL 조작 대신 메시지 방식)
                    window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'ended'}}, '*');
                }}

                // 빨리감기/배속 감시 (0.5초마다)
                setInterval(function() {{
                    if (player && player.getCurrentTime && {str(not loop_active).lower()}) {{
                        if (player.getCurrentTime() >= {e_val} - 0.5) {{ sendEndSignal(); }}
                    }}
                }}, 500);
            </script>
            """
            # 자바스크립트의 신호를 파이썬 변수(res)로 받음
            res = components.html(html_watcher, height=460)
            
            # 신호가 들어오면 새로고침 없이 상태 업데이트
            if res == "ended":
                st.session_state.is_playing = False
                st.rerun()
        else:
            st.warning("START 버튼을 누르면 연습이 시작됩니다.")
