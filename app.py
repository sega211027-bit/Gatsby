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

# --- [상태 관리 및 종료 신호 수신] ---
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# 자바스크립트가 보낸 'finished' 파라미터 감시 (배속/빨리감기 대응 리셋)
if st.query_params.get("finished") == "true":
    st.session_state.is_playing = False
    st.query_params.clear()
    st.rerun()

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

    # --- [1. 복원된 초대형 정보창] ---
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 25px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.5em; color: #666;">Day</span><br><span style="font-size: 6.5em; font-weight: 900; color: #007bff; line-height: 1;">{day}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">ROUND</span><br><span style="font-size: 6.5em; font-weight: 900; color: #007bff; line-height: 1;">{rnd}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">회차</span><br><span style="font-size: 6.5em; font-weight: 900; color: #28a745; line-height: 1;">{turn}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- [2. 복원된 시작 구절 (Phrase)] ---
    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 30px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 25px;">
            <p style="color: #ff4b4b; font-size: 1.4em; font-weight: bold; margin-bottom: 10px;">📍 Starting Phrase</p>
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #222; font-size: 4em; margin: 0; line-height: 1.2;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.info(f"🕒 **구간:** {format_seconds(s_val)} ~ {format_seconds(e_val)}")
        st.markdown("""
            <style>
                div.stButton > button[kind="primary"] { height: 120px !important; font-size: 40px !important; background-color: #28a745 !important; border-radius: 20px !important; border: none !important; }
                div.stButton > button[kind="secondary"] { height: 120px !important; font-size: 35px !important; background-color: #dc3545 !important; color: white !important; border-radius: 20px !important; border: none !important; }
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
            # 실시간 감시 엔진 (빨리감기/배속 무관하게 e_val 도달 시 리셋)
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
                        playerVars: {{ 'start': {s_val}, 'end': {e_val}, 'autoplay': 1, 'controls': 1, 'rel': 0, 'enablejsapi': 1 }},
                        events: {{ 'onStateChange': function(event) {{
                            if (event.data == 0 && {str(not loop_active).lower()}) {{ triggerReset(); }}
                        }} }}
                    }});
                }}

                function triggerReset() {{
                    const url = new URL(window.parent.location);
                    url.searchParams.set('finished', 'true');
                    window.parent.location.href = url.href;
                }}

                setInterval(function() {{
                    if (player && player.getCurrentTime && {str(not loop_active).lower()}) {{
                        if (player.getCurrentTime() >= {e_val} - 0.5) {{ triggerReset(); }}
                    }}
                }}, 500);
            </script>
            """
            components.html(js_code, height=460)
        else:
            st.warning("설정 확인 후 START 버튼을 누르세요.")
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
