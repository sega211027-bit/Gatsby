import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- [1. 설정 및 세션 관리] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 다시 재생 버튼 클릭 시 숫자를 올려서 URL을 강제로 변경함 (key 대용)
if 'reloader' not in st.session_state:
    st.session_state.reloader = 0

is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)

if not is_admin:
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

        # 상단 안내 문구
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
                <p style="color: #666; font-size: 1.1em;">📍 이 단어가 들리면 낭독을 시작하세요</p>
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">"{tgt['phrase']}"</h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            
            # 토글 (체크박스) - 이 값은 JS 내부의 loopActive 변수로 전달됨
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            # [수정] reloader를 올려서 URL을 미세하게 변경 -> 브라우저가 새 영상으로 인식
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.reloader += 1
                st.rerun()

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            
            # [해결책] TypeError를 방지하기 위해 key를 삭제하고, 
            # 대신 API 호출 주소 끝에 ?v={reloader}를 붙여 리로드를 유도합니다.
            yt_html = f"""
            <div id="player"></div>
            <script src="https://www.youtube.com/iframe_api?v={st.session_state.reloader}"></script>
            <script>
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
                                // 설정된 끝 지점보다 2초 더 여유를 줌
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
            
            # st.empty() 컨테이너를 써서 안정적으로 화면을 갱신합니다.
            placeholder = st.empty()
            with placeholder:
                components.html(yt_html, height=460)
            
    else:
        st.warning("데이터 파일을 찾을 수 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")