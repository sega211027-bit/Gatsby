import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- [1. 기본 설정 및 세션 관리] ---
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 다시 재생 버튼을 위한 트리거 (숫자를 바꿔서 변화를 감지)
if 'play_trigger' not in st.session_state:
    st.session_state.play_trigger = 0

#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드", value=False)
is_admin = False


if not is_admin:
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        v_id, r_data = cfg['video_id'], cfg['data']
        
        st.title("📖 Great Gatsby Audio Guide")
        
        # 데이터 선택 (이 값이 바뀔 때만 플레이어가 완전히 새로고침됨)
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #007bff; margin-bottom: 20px; text-align: center;">
                <p style="color: #666; font-size: 1.1em;">📍 이 단어가 들리면 낭독을 시작하세요</p>
                <h1 style="color: #007bff; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.8em;">"{tgt['phrase']}"</h1>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **시작 시점:** {tgt['start_time']}")
            
            # 무한 반복 토글 (이 변경은 iframe 재생에 영향을 주지 않음)
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            # [재생 버튼] 클릭 시 세션 값을 변경하여 iframe에 신호를 보냄
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.session_state.play_trigger += 1

        with col2:
            s_val = int(tgt['start_sec'])
            e_val = int(tgt['end_sec'])
            
            # [핵심] 유튜브 API 연동 HTML
            # 1. '다시 재생' 버튼 클릭 시 현재 분량의 start_sec로 이동
            # 2. 영상 종료 후 2초 뒤에 start_sec로 자동 복귀
            # 3. 토글은 오직 '자동 복귀' 여부만 결정
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
                
                function onYouTubeIframeAPIReady() {{
                    player = new YT.Player('player', {{
                        height: '450',
                        width: '100%',
                        videoId: '{v_id}',
                        playerVars: {{
                            'start': startSec,
                            'autoplay': 1,
                            'rel': 0,
                            'modestbranding': 1,
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
                            var curr = player.getCurrentTime();
                            // 설정된 끝 지점보다 2초 더 들려준 뒤 판단
                            if (curr >= (endSec + 2)) {{
                                if ({str(do_loop).lower()}) {{
                                    player.seekTo(startSec);
                                    player.playVideo();
                                }} else {{
                                    player.pauseVideo();
                                }}
                                clearInterval(checkEnd);
                            }}
                        }}, 500);
                    }}
                }}
            </script>
            """
            
            # [수정] 다시 재생 버튼 클릭 시 src에 미세한 변화를 주어 강제 점프 유도
            # (iframe API와의 가장 확실한 연동 방식)
            player_key = f"yt_{day}_{rnd}_{turn}_{st.session_state.play_trigger}"
            components.html(yt_html, height=460, key=player_key)
            
    else:
        st.warning("데이터 파일을 찾을 수 없습니다.")
else:
    st.title("Admin Mode")
    st.write("데이터 생성을 진행하세요.")