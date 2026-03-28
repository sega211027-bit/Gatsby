import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- [1. 설정 및 세션 관리] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 재생 버튼 클릭 횟수를 추적하여 플레이어를 강제 리로드하는 용도
if 'reloader' not in st.session_state:
    st.session_state.reloader = 0

#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)
is_admin = False

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
            
            # 토글 상태 저장 (이 값이 바뀌어도 플레이어 ID가 바뀌지 않으면 영상은 유지됨)
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            # [핵심] 버튼 클릭 시 reloader 값을 올려서 플레이어를 새로 생성하게 함
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.reloader += 1
                st.rerun()

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            
            # 자바스크립트 중괄호 {{ }} 이스케이프 적용
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
                                // 끝 지점보다 2초 더 여유를 두어 소리 끊김 방지
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
            
            # [해결책] reloader 번호를 포함한 고유한 Key를 생성하여 
            # 버튼 클릭 시에만 플레이어가 처음(start_sec)부터 다시 로드되도록 강제함
            p_key = f"player_{day}_{rnd}_{turn}_{st.session_state.reloader}"
            components.html(yt_html, height=460, key=p_key)
            
    else:
        st.warning("데이터 파일을 찾을 수 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")