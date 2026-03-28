import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- [1. 기본 설정 및 세션 관리] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 고유 ID를 관리하여 '다시 재생' 시 플레이어를 완전히 새로 로드함
if 'player_instance' not in st.session_state:
    st.session_state.player_instance = 0

is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)

if not is_admin:
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        v_id, r_data = cfg['video_id'], cfg['data']
        
        st.title("📖 Great Gatsby Audio Guide")
        
        # 데이터 선택 (Day, Round, 회차)
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

        # 문장 안내 박스
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
                <p style="color: #666; font-size: 1.1em;">📍 이 단어가 들리면 낭독을 시작하세요</p>
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">"{tgt['phrase']}"</h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            
            # [중요] 토글: 이 값은 JavaScript에서 직접 참조하여 새로고침 없이 동작 결정
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.player_instance += 1
                st.rerun()

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            
            # Python f-string 내 JS 중괄호는 {{ }} 로 이스케이프 처리 필수
            yt_html = f"""
            <div id="player"></div>
            <script>
                var tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = document.getElementsByTagName('script')[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

                var player;
                function onYouTubeIframeAPIReady() {{
                    player = new YT.Player('player', {{
                        height: '450',
                        width: '100%',
                        videoId: '{v_id}',
                        playerVars: {{
                            'start': {s_val},
                            'autoplay': 1,
                            'rel': 0,
                            'enablejsapi': 1
                        }},
                        events: {{
                            'onStateChange': onPlayerStateChange
                        }}
                    }});
                }}

                function onPlayerStateChange(event) {{
                    if (event.data == YT.PlayerState.PLAYING) {{
                        var checkEnd = setInterval(function() {{
                            if (player && player.getCurrentTime) {{
                                var curr = player.getCurrentTime();
                                // 끝 지점보다 2초 여유를 두어 소리 끊김 방지
                                if (curr >= ({e_val} + 2)) {{
                                    if ({str(do_loop).lower()}) {{
                                        player.seekTo({s_val});
                                        player.playVideo();
                                    }} else {{
                                        player.pauseVideo();
                                    }}
                                    clearInterval(checkEnd);
                                }}
                            }}
                        }}, 500);
                    }}
                }}
            </script>
            """
            
            # [해결책] 고유 Key를 명시하되, '다시 재생' 버튼을 누를 때만 변경되도록 함
            # 이렇게 하면 토글을 눌러도 Key가 변하지 않아 영상이 유지됩니다.
            p_key = f"v_{day}_{rnd}_{turn}_{st.session_state.player_instance}"
            components.html(yt_html, height=460, key=p_key)
            
    else:
        st.warning("데이터 파일을 찾을 수 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")