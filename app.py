import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- [1. 세션 상태 초기화: 최상단 배치] ---
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'play_id' not in st.session_state:
    st.session_state.play_id = 0

# 2. 시간 변환 함수
def format_time(seconds):
    try:
        s = int(float(seconds))
        return f"{s // 60}:{s % 60:02d}"
    except: return "0:00"

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")

# --- [3. 쿼리 파라미터 처리] ---
if st.query_params.get("trigger") == "reset":
    st.session_state.is_playing = False
    # 최신 Streamlit 방식의 안전한 파라미터 삭제
    st.query_params.clear()
    st.rerun()

# 4. 데이터 로드
JSON_FILE = "final_mapping.json"
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # 사이드바 설정
    st.sidebar.header("⚙️ Settings")
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=False)
    
    day_opts = sorted(list(set(str(d['Day']) for d in r_data)))
    day = st.sidebar.select_slider("📅 Day", options=day_opts)
    
    rnd_opts = sorted(list(set(str(d['ROUND']) for d in r_data if str(d['Day']) == day)))
    rnd = st.sidebar.select_slider("🔁 Round", options=rnd_opts)
    
    turn_opts = sorted(list(set(str(d['회차']) for d in r_data if str(d['Day']) == day and str(d['ROUND']) == rnd)))
    turn = st.sidebar.select_slider("🔢 회차", options=turn_opts)

    tgt = next(d for d in r_data if str(d['Day']) == day and str(d['ROUND']) == rnd and str(d['회차']) == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # 5. UI 대시보드
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 20px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 15px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.2em; color: #666;">Day</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff; line-height: 1;">{day}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">ROUND</span><br><span style="font-size: 5.5em; font-weight: 900; color: #007bff; line-height: 1;">{rnd}</span></div>
                <div><span style="font-size: 1.2em; color: #666;">회차</span><br><span style="font-size: 5.5em; font-weight: 900; color: #28a745; line-height: 1;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 25px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 20px;">
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #222; font-size: 3.2em; margin: 0;">"{tgt.get('phrase', '')}"</h1>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<style>div.stButton > button { height: 110px !important; font-size: 38px !important; border-radius: 15px !important; }</style>", unsafe_allow_html=True)
        
        if not st.session_state.is_playing:
            if st.button("▶ START", use_container_width=True, type="primary"):
                # play_id를 문자열 조합으로 변경하여 식별 안정성 강화
                st.session_state.play_id += 1
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
        # 재생 중일 때만 컴포넌트를 호출하여 충돌 방지
        if st.session_state.is_playing:
            is_loop = "true" if loop_active else "false"
            
            # .replace() 방식으로 문법 충돌 원천 차단
            js_template = """
            <div id="player"></div>
            <script>
                var tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = document.getElementsByTagName('script')[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
                var player;
                function onYouTubeIframeAPIReady() {
                    player = new YT.Player('player', {
                        height: '450', width: '100%', videoId: 'V_ID',
                        playerVars: { 'start': S_VAL, 'end': E_VAL, 'autoplay': 1, 'controls': 1, 'rel': 0, 'enablejsapi': 1 }
                    });
                }
                var monitor = setInterval(function() {
                    if (player && player.getCurrentTime) {
                        var curr = player.getCurrentTime();
                        if (curr >= E_VAL - 0.4) {
                            if (IS_LOOP) { player.seekTo(S_VAL); }
                            else { 
                                clearInterval(monitor);
                                const url = new URL(window.parent.location.href);
                                url.searchParams.set('trigger', 'reset');
                                window.parent.location.replace(url.href);
                            }
                        }
                    }
                }, 500);
            </script>
            """
            js_code = js_template.replace("V_ID", v_id).replace("S_VAL", str(s_val)).replace("E_VAL", str(e_val)).replace("IS_LOOP", is_loop)
            
            # [해결책] 고정된 이름 + 순차적 번호로 Key 충돌 완벽 차단
            final_key = f"yt_vfinal_id_{st.session_state.play_id}"
            components.html(js_code, height=460, key=final_key)
        else:
            # STOP 상태일 때는 컴포넌트를 아예 제거하여 메모리 충돌 방지
            st.info("연습 준비 완료. ▶ START를 눌러주세요.")
else:
    st.error("JSON 파일을 찾을 수 없습니다.")
