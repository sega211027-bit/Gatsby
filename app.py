import streamlit as st
import json
import os
import time
import streamlit.components.v1 as components

def format_seconds(seconds):
    try:
        seconds = int(seconds)
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    except:
        return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

if 'v_key' not in st.session_state:
    st.session_state.v_key = str(time.time())
if 'loop_enabled' not in st.session_state:
    st.session_state.loop_enabled = False

if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']

    st.title("📖 Great Gatsby Audio Guide")

    day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
    rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
    turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
    tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

    s_time_disp = format_seconds(tgt['start_sec'])
    e_time_disp = format_seconds(tgt['end_sec'])

    st.info(f"👤 **낭독자:** {tgt['담당자']}\n\n🕒 **구간:** {s_time_disp} ~ {e_time_disp}")

    # 🔹 사이드바에 무한 반복 토글 버튼 추가
    if st.sidebar.button("♻️ 무한 반복 토글"):
        st.session_state.loop_enabled = not st.session_state.loop_enabled
        st.rerun()
    st.sidebar.caption(f"현재 상태: {'무한 반복 ON' if st.session_state.loop_enabled else '무한 반복 OFF'}")

    s_val = str(tgt['start_sec'])
    e_val = str(tgt['end_sec'])

    final_src = f"https://www.youtube.com/embed/{v_id}?start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&rel=0&iv_load_policy=3"

    components.html(f"""
        <div id="player"></div>
        <script src="https://www.youtube.com/iframe_api"></script>
        <script>
          var player;
          var start = {s_val};
          var end = {e_val};
          var loopEnabled = {str(st.session_state.loop_enabled).lower()}; // Python 상태 반영

          function onYouTubeIframeAPIReady() {{
            player = new YT.Player('player', {{
              height: '450',
              width: '100%',
              videoId: '{v_id}',
              playerVars: {{
                start: start,
                end: end,
                autoplay: 1,
                rel: 0,
                iv_load_policy: 3
              }},
              events: {{
                'onStateChange': onPlayerStateChange
              }}
            }});
          }}

          function onPlayerStateChange(event) {{
            if (event.data == YT.PlayerState.ENDED) {{
              if (loopEnabled) {{
                player.seekTo(start);
                player.playVideo();
              }}
            }}
          }}
        </script>
    """, height=460)
else:
    st.error("데이터 파일이 없습니다.")
