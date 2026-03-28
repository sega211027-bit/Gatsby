import streamlit as st
import json
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# --- [1. 실시간 종료 신호 수신부] ---
# 자바스크립트가 보낸 'trigger=reset' 신호를 받으면 즉시 버튼 상태 초기화
if st.query_params.get("trigger") == "reset":
    st.session_state.is_playing = False
    st.query_params.clear() # 신호 삭제 후
    st.rerun() # 즉시 새로고침

if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [2. 사이드바 및 데이터 추출] ---
    day = st.sidebar.select_slider("📅 Day", options=sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.select_slider("🔁 Round", options=sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.select_slider("🔢 회차", options=sorted(list(set(d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd))))

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [3. UI 복원: 초대형 정보창 & 구절] ---
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 20px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.2em; color: #666;">Day</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff;">{day}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">ROUND</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff;">{rnd}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">회차</span><br><span style="font-size: 5.5em; font-weight: 900; color: #28a745;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 25px;">
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #222; font-size: 3.5em; margin: 0;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<style>div.stButton > button { height: 100px !important; font-size: 30px !important; border-radius: 15px !important; }</style>", unsafe_allow_html=True)
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
            # [핵심] 자바스크립트 감시 엔진
            # 0.5초마다 현재 시간을 체크하여 e_val 도달 시 부모 창에 리셋 신호 전달
            js_code = f"""
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
                        playerVars: {{ 'start': {s_val}, 'end': {e_val}, 'autoplay': 1, 'controls': 1, 'enablejsapi': 1 }},
                    }});
                }}

                setInterval(function() {{
                    if (player && player.getCurrentTime) {{
                        var curr = player.getCurrentTime();
                        if (curr >= {e_val} - 0.5) {{
                            // 부모 창(Streamlit) 주소에 파라미터를 붙여 강제 리셋 신호를 보냄
                            const url = new URL(window.parent.location.href);
                            url.searchParams.set('trigger', 'reset');
                            window.parent.location.replace(url.href);
                        }}
                    }}
                }}, 500);
            </script>
            """
            components.html(js_code, height=460)
        else:
            st.warning("START를 누르면 연습이 시작됩니다.")
