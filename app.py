import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- [1. 기본 설정] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)
is_admin = False

if not is_admin:
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        v_id, r_data = cfg['video_id'], cfg['data']
        
        st.title("📖 Great Gatsby Audio Guide")
        
        # 사이드바 선택
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

        # 문장 박스
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
                <p style="color: #666; font-size: 1.1em;">📍 이 단어가 들리면 낭독을 시작하세요</p>
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">"{tgt['phrase']}"</h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            # 버튼 클릭 시 iframe을 다시 로드하도록 유도
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.rerun()

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            
            # [핵심] 유튜브 iframe API를 활용한 HTML/JS 코드
            # 영상이 끝나면(state == 0) 다시 시작 지점으로 보냅니다.
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
                            'end': {e_val},
                            'autoplay': 1,
                            'rel': 0,
                            'cc_load_policy': 1
                        }},
                        events: {{
                            'onStateChange': onPlayerStateChange
                        }}
                    }});
                }}

                function onPlayerStateChange(event) {{
                    // event.data == 0 은 영상이 종료되었음을 의미
                    if (event.data == YT.PlayerState.ENDED && {str(do_loop).lower()}) {{
                        player.seekTo({s_val});
                        player.playVideo();
                    }}
                }}
            </script>
            """
            components.html(yt_html, height=460)
            
    else:
        st.warning("데이터 파일이 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")