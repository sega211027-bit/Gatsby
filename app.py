import streamlit as st
import json
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

# --- [1. 종료 신호 수신부] ---
if st.query_params.get("trigger") == "reset":
    st.session_state.is_playing = False
    st.query_params.clear()
    st.rerun()

if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # --- [2. 사이드바 컨트롤] ---
    st.sidebar.header("⚙️ 컨트롤러")
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    
    day = st.sidebar.select_slider("📅 Day", options=sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.select_slider("🔁 Round", options=sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.select_slider("🔢 회차", options=sorted(list(set(d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd))))

    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [3. UI 복원] ---
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 25px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.5em; color: #666;">Day</span><br><span style="font-size: 6.5em; font-weight: 900; color: #007bff; line-height: 1;">{day}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">ROUND</span><br><span style="font-size: 6.5em; font-weight: 900; color: #007bff; line-height: 1;">{rnd}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">회차</span><br><span style="font-size: 6.5em; font-weight: 900; color: #28a745; line-height: 1;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 30px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 25px;">
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #222; font-size: 4em; margin: 0; line-height: 1.2;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<style>div.stButton > button { height: 120px !important; font-size: 40px !important; border-radius: 20px !important; }</style>", unsafe_allow_html=True)
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
            # 핵심 로직 분기
            is_loop_js = "true" if loop_active else "false"

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
                        playerVars: {{ 
                            'start': {s_val}, 'end': {e_val}, 
                            'autoplay': 1, 'controls': 1, 'rel': 0, 'enablejsapi': 1
                        }},
                        events: {{
                            'onStateChange': onPlayerStateChange
                        }}
                    }});
                }}

                // 상태 변화 감지 (영상이 완전히 끝났을 때의 대응)
                function onPlayerStateChange(event) {{
                    if (event.data == YT.PlayerState.ENDED) {{
                        if ({is_loop_js}) {{
                            player.seekTo({s_val}); // 무한반복이면 시작지점으로 점프
                            player.playVideo();
                        }} else {{
                            triggerReset(); // 아니면 버튼 리셋
                        }}
                    }}
                }}

                function triggerReset() {{
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('trigger', 'reset');
                    window.parent.location.replace(url.href);
                }}

                // 실시간 감시 (배속/빨리감기 대응)
                setInterval(function() {{
                    if (player && player.getCurrentTime) {{
                        var curr = player.getCurrentTime();
                        if (curr >= {e_val} - 0.3) {{ // 종료 0.3초 전 감지
                            if ({is_loop_js}) {{
                                player.seekTo({s_val}); // 시작지점으로 강제 점프
                            }} else {{
                                triggerReset();
                            }}
                        }}
                    }}
                }}, 500);
            </script>
            """
            components.html(js_code, height=460)
        else:
            st.warning("연습 준비 완료")
else:
    st.error("데이터 파일을 찾을 수 없습니다.")
