import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- [1. 기본 설정 및 세션 상태 초기화] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 플레이어를 강제로 새로고침하기 위한 고유 ID 관리
if 'player_id' not in st.session_state:
    st.session_state.player_id = 0

#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)
is_admin = False

if not is_admin:
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        v_id, r_data = cfg['video_id'], cfg['data']
        
        st.title("📖 Great Gatsby Audio Guide")
        
        # 선택박스 (이 값이 바뀌면 player_id를 올려서 영상을 새로 로드)
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

        # 상단 문장 박스
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
                <p style="color: #666; font-size: 1.1em;">📍 이 단어가 들리면 낭독을 시작하세요</p>
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">"{tgt['phrase']}"</h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            
            # [수정] 토글을 눌러도 rerun이 발생하지 않도록 하여 영상 끊김 방지
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            # [수정] 버튼 클릭 시에만 ID를 변경하여 영상을 처음(start_sec)부터 다시 로드
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.player_id += 1
                st.rerun()

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            
            # 자바스크립트 내 중괄호 {{ }} 이스케이프 적용
            yt_html = f"""
            <div id="player"></div>
            <script>
                var tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = document.getElementsByTagName('script')[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

                var player;
                var startSec = {s_val};
                var endSec = {e_val};
                var loopActive = {str(do_loop).lower()};
                
                function onYouTubeIframeAPIReady() {{
                    player = new YT.Player('player', {{
                        height: '450',
                        width: '100%',
                        videoId: '{v_id}',
                        playerVars: {{
                            'start': startSec,
                            'autoplay': 1,
                            'rel': 0,
                            'enablejsapi': 1,
                            'origin': window.location.origin
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
                                // 끝 지점보다 2초 더 여유있게 들려줌
                                if (curr >= (endSec + 2)) {{
                                    if (loopActive) {{
                                        player.seekTo(startSec);
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
            
            # TypeError 방지를 위해 고정된 key를 쓰지 않고 컨테이너만 사용
            # 하지만 다시 재생 버튼 클릭 시에는 강제로 새로 그려야 하므로 id를 조합함
            st.components.v1.html(yt_html, height=460)
            
    else:
        st.warning("데이터 파일을 찾을 수 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")