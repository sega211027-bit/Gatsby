import streamlit as st
import json
import os
import streamlit.components.v1 as components

# 1. 앱 설정 및 상태 초기화
st.set_page_config(page_title="Gatsby Audio Guide", layout="wide")
JSON_FILE = "final_mapping.json"

if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# 종료 신호 수신 시 상태 리셋
if st.query_params.get("trigger") == "reset":
    st.session_state.is_playing = False
    st.query_params.clear()
    st.rerun()

# 2. 데이터 로드 및 전처리
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    v_id, r_data = cfg['video_id'], cfg['data']
    
    # 사이드바 컨트롤러 (모든 옵션을 문자열로 처리하여 안정성 확보)
    st.sidebar.header("⚙️ 컨트롤러")
    loop_active = st.sidebar.toggle("🔄 무한 반복 모드", value=True)
    
    day_list = sorted(list(set(str(d['Day']) for d in r_data)))
    day = st.sidebar.select_slider("📅 Day", options=day_list)
    
    rnd_list = sorted(list(set(str(d['ROUND']) for d in r_data if str(d['Day']) == day)))
    rnd = st.sidebar.select_slider("🔁 Round", options=rnd_list)
    
    turn_list = sorted(list(set(str(d['회차']) for d in r_data if str(d['Day']) == day and str(d['ROUND']) == rnd)))
    turn = st.sidebar.select_slider("🔢 회차", options=turn_list)

    # 선택된 구간 데이터 추출
    tgt = next(d for d in r_data if str(d['Day']) == day and str(d['ROUND']) == rnd and str(d['회차']) == turn)
    s_val, e_val = int(float(tgt.get('start_sec', 0))), int(float(tgt.get('end_sec', 0)))

    # --- [3. UI 디자인: 웅장한 스타일 복구] ---
    st.markdown(f"""
        <div style="background-color: #f8faff; padding: 25px; border-radius: 20px; border: 2px solid #e1e8f0; margin-bottom: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around;">
                <div><span style="font-size: 1.5em; color: #666;">Day</span><br><span style="font-size: 6.5em; font-weight: 900; color: #007bff; line-height: 1;">{day}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">ROUND</span><br><span style="font-size: 6.5em; font-weight: 900; color: #007bff; line-height: 1;">{rnd}</span></div>
                <div><span style="font-size: 1.5em; color: #666;">회차</span><br><span style="font-size: 6.5em; font-weight: 900; color: #28a745; line-height: 1;">{turn}</span></div>
            </div>
        </div>
        <div style="background-color: #ffffff; padding: 35px; border-radius: 15px; border: 4px solid #f1f1f1; text-align: center; margin-bottom: 25px;">
            <h1 style="font-family: 'Times New Roman', serif; font-style: italic; color: #222; font-size: 3.8em; margin: 0; line-height: 1.2;">"{tgt.get('phrase', '')}"</h1>
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
        
        # 재생 시간 정보 표시
        st.write(f"⏱️ **구간:** {s_val//60}:{s_val%60:02d} ~ {e_val//60}:{e_val%60:02d}")

    with col2:
        if st.session_state.is_playing:
            loop_js = "true" if loop_active else "false"
            
            # [수정 핵심] 중괄호 충돌을 피하기 위해 텍스트 치환 방식 채택
            js_temp = """
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
                setInterval(function() {
                    if (player && player.getCurrentTime) {
                        var curr = player.getCurrentTime();
                        if (curr >= E_VAL - 0.4) {
                            if (IS_LOOP) { player.seekTo(S_VAL); }
                            else { window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + "?trigger=reset"; }
                        }
                    }
                }, 500);
            </script>
            """
            js_final = js_temp.replace("V_ID", v_id).replace("S_VAL", str(s_val)).replace("E_VAL", str(e_val)).replace("IS_LOOP", loop_js)
            
            # Key 값을 고유하게 생성하여 슬라이더 변경 시 즉시 로드
            components.html(js_final, height=460, key=f"yt{day}{rnd}{turn}")
        else:
            st.warning("연습 준비 완료. ▶ START를 눌러주세요.")
else:
    st.error("데이터 파일(final_mapping.json)을 찾을 수 없습니다.")
