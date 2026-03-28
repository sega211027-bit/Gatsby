import streamlit as st
import json
import os
import streamlit.components.v1 as components

# 1. 시간 변환 유틸리티
def format_time(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except: return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")

# --- [수정] 세션 상태 및 쿼리 파라미터 제어 강화 ---
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# 리셋 신호가 들어오면 상태를 끄고 주소창을 완전히 비움
if st.query_params.get("trigger") == "reset":
    st.session_state.is_playing = False
    st.query_params.clear()
    st.rerun()

JSON_FILE = "final_mapping.json"
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # 사이드바 설정
    st.sidebar.header("⚙️ Settings")
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    day = st.sidebar.select_slider("📅 Day", options=sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.select_slider("🔁 Round", options=sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.select_slider("🔢 회차", options=sorted(list(set(d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd))))

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # 초대형 UI
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 20px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 15px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.2em; color: #666;">Day</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff; line-height: 1;">{day}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">ROUND</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff; line-height: 1;">{rnd}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">회차</span><br><span style="font-size: 5.5em; font-weight: 900; color: #28a745; line-height: 1;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 20px;">
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #222; font-size: 3.8em; margin: 0;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<style>div.stButton > button { height: 110px !important; font-size: 38px !important; border-radius: 15px !important; }</style>", unsafe_allow_html=True)
        
        # [수정] START 클릭 시 쿼리 파라미터를 명시적으로 비우고 실행
        if not st.session_state.is_playing:
            if st.button("▶ START", use_container_width=True, type="primary"):
                st.query_params.clear() # 이전 리셋 신호 완전 제거
                st.session_state.is_playing = True
                st.rerun()
        else:
            if st.button("⏹ STOP", use_container_width=True, type="secondary"):
                st.session_state.is_playing = False
                st.rerun()
        
        st.markdown(f"""
            <div style="margin-top: 10px; padding: 12px; background-color: #f1f1f1; border-radius: 10px; text-align: center;">
                <p style="margin: 0; font-size: 1.1em; color: #555;">Track Timestamp</p>
                <p style="margin: 5px 0 0 0; font-size: 2em; font-weight: bold; color: #333;">
                    <span style="color: #007bff;">{format_time(s_val)}</span> <span style="font-size: 0.6em; color: #999;">▶</span> <span style="color: #ff4b4b;">{format_time(e_val)}</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.session_state.is_playing:
            is_loop = "true" if loop_active else "false"
            # [수정] 유튜브 API 호출 시 캐시 방지를 위해 랜덤 키 활용 (컴포넌트 강제 리로드)
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
                        playerVars: {{ 'start': {s_val}, 'end': {e_val}, 'autoplay': 1, 'controls': 1, 'rel': 0, 'enablejsapi': 1 }}
                    }});
                }}
                var monitor = setInterval(function() {{
                    if (player && player.getCurrentTime) {{
                        var curr = player.getCurrentTime();
                        if (curr >= {e_val} - 0.4) {{
                            if ({is_loop}) {{ 
                                player.seekTo({s_val}); 
                            }} else {{ 
                                clearInterval(monitor);
                                const url = new URL(window.parent.location.href);
                                url.searchParams.set('trigger', 'reset');
                                window.parent.location.replace(url.href);
                            }}
                        }}
                    }}
                }}, 500);
            </script>
            """
            # key를 추가하여 상태가 바뀔 때마다 컴포넌트를 새로 그림
            components.html(js_code, height=460, key=f"yt_player_{turn}_{day}_{rnd}")
        else:
            st.warning("연습 준비 완료. ▶ START를 눌러주세요.")
else:
    st.error("JSON 파일을 찾을 수 없습니다.")
