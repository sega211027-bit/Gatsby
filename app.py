#is_admin = False 배포용
#c:\Users\1\python\python.exe -m streamlit run c:/Users/1/Documents/python-program/python-youtube-timeline/youtube_20260828/youtube_roster_system.py

import streamlit as st
import pandas as pd
import re
import json
import os

# --- [1. 핵심 엔진: 시간 변환 및 텍스트 정제 함수] ---

def format_seconds(seconds):
    """초 단위를 시:분:초 또는 분:초로 변환 (60분 이상 대응)"""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def ultra_simplify(txt):
    """검색용: 소문자화, 철자통일(Grey->Gray), 알파벳만 추출"""
    t = str(txt).lower().replace('grey', 'gray')
    return "".join(re.findall(r'[a-z]', t))

def parse_transcript(content):
    """자막 파싱: 모든 노이즈(숫자, 한글, 기호) 제거 후 글자 단위 시간 매핑"""
    full_stream = ""
    char_origin_map = []
    time_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)'
    
    lines = content.split('\n')
    current_sec = 0
    raw_data = []

    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 유튜브 시간 태그 업데이트
        time_match = re.search(time_pattern, line)
        if time_match:
            t_str = time_match.group(1)
            parts = list(map(int, t_str.split(':')))
            if len(parts) == 3: # 시:분:초
                current_sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
            else: # 분:초
                current_sec = parts[0] * 60 + parts[1]

        # 노이즈(숫자, 한글, 특수기호) 제거하고 영문만 남김
        clean_text = re.sub(r'[^a-zA-Z]', ' ', line)
        
        if clean_text.strip():
            idx = len(raw_data)
            raw_data.append({"seconds": current_sec})
            
            for char in clean_text.lower():
                if 'a' <= char <= 'z':
                    full_stream += char
                    char_origin_map.append(idx)
                    
    return full_stream, char_origin_map, raw_data

# --- [2. 메인 UI 설정] ---

st.set_page_config(page_title="Gatsby Audio Guide", layout="wide", page_icon="📖")
JSON_FILE = "final_mapping.json"

# 사이드바: 관리자 모드와 멤버  배포용
# #c:\Users\1\python\python.exe -m streamlit run c:/Users/1/Documents/python-program/python-youtube-timeline/youtube_20260828/youtube_roster_system.py모드 전환
#is_admin = 배포용
# #c:\Users\1\python\python.exe -m streamlit run c:/Users/1/Documents/python-program/python-youtube-timeline/youtube_20260828/youtube_roster_system.py st.sidebar.checkbox("🛠️ 관리자 모드 (데이터 생성)")
is_admin = False

if is_admin:
    # --- [A. 관리자 모드: 타임스탬프 추출 엔진] ---
    st.title("🛠️ 데이터 엔진 (Admin Mode)")
    st.write("로스터와 자막 파일을 업로드하여 매칭 데이터를 생성합니다.")
    
    yt_url = st.text_input("유튜브 영상 주소", placeholder="https://www.youtube.com/watch?v=...")
    roster_file = st.file_uploader("로스터 엑셀 업로드 (xlsx)", type=['xlsx'])
    sub_file = st.file_uploader("유튜브 자막 텍스트 업로드 (txt)", type=['txt'])
    
    if st.button("🚀 초정밀 매칭 실행"):
        try:
            v_id = re.search(r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})", yt_url).group(1)
            df = pd.read_excel(roster_file)
            content = sub_file.read().decode("utf-8")
            
            full_stream, char_map, raw_data = parse_transcript(content)
            final_list = []
            last_pos = 0 

            for _, row in df.iterrows():
                search_s = ultra_simplify(row['시작 단어(5)'])
                search_e = ultra_simplify(row['마지막 단어(5)'])

                # 1단계: 주변 3만 자 내에서 검색 / 2단계: 전체 검색 / 3단계: 부분 검색
                pos = full_stream.find(search_s, last_pos, last_pos + 30000)
                if pos == -1: pos = full_stream.find(search_s, last_pos)
                if pos == -1 and len(search_s) > 8: pos = full_stream.find(search_s[:8], last_pos)

                if pos != -1:
                    m_idx = char_map[pos]
                    s_s = raw_data[m_idx]['seconds']
                    s_t = format_seconds(s_s)
                    
                    e_pos = full_stream.find(search_e, pos + len(search_s))
                    if e_pos != -1:
                        e_idx = char_map[e_pos]
                        e_s = raw_data[e_idx]['seconds'] + 2
                        last_pos = e_pos 
                    else:
                        e_s = s_s + 120
                        last_pos = pos + len(search_s)
                else:
                    s_s = final_list[-1]['end_sec'] if final_list else 0
                    s_t = format_seconds(s_s)
                    e_s = s_s + 120
                    last_pos += 100

                final_list.append({
                    "Day": str(row['Day']), "ROUND": int(row['ROUND']), "회차": int(row['회차']),
                    "담당자": str(row['담당자']), "start_time": s_t,
                    "start_sec": int(s_s), "end_sec": int(e_s), "phrase": str(row['시작 단어(5)'])
                })
            
            st.success("✅ 매칭 완료! 아래 버튼으로 JSON을 다운로드하세요.")
            st.download_button("📥 final_mapping.json 다운로드", 
                             json.dumps({"video_id": v_id, "data": final_list}, ensure_ascii=False, indent=4), 
                             file_name=JSON_FILE)
        except Exception as e:
            st.error(f"오류 발생: {e}")

else:
    # --- [B. 배포 모드: 낭독반 멤버용 대형 스크립트 가이드] ---
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        
        v_id, r_data = cfg['video_id'], cfg['data']
        
        st.title("📖 Great Gatsby Audio Guide")
        
        # 사이드바에서 본인 회차 선택
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)

        # 1. 상단: 대형 스크립트 출력
        st.markdown("### 🔍 오늘 낭독할 문장 (Script)")
        st.markdown(f"""
            <div style="
                background-color: #f8f9fb; 
                padding: 35px; 
                border-radius: 15px; 
                border-left: 12px solid #007bff;
                box-shadow: 2px 2px 12px rgba(0,0,0,0.08);
                margin-bottom: 25px;
            ">
                <h1 style="color: #1A1C1E; line-height: 1.6; font-family: 'Times New Roman', serif; font-style: italic; font-size: 2.2em;">
                    "{tgt['phrase']}"
                </h1>
                <hr style="margin: 20px 0; border: 0; border-top: 1px solid #eee;">
                <p style="text-align: right; color: #555; font-size: 1.2em;">
                    <b>낭독자:</b> {tgt['담당자']}  &nbsp;|&nbsp;  <b>시작점:</b> {tgt['start_time']}
                </p>
            </div>
        """, unsafe_allow_html=True)

        # 2. 중앙: 컨트롤 및 영상 영역
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### ⚙️ Player Control")
            do_loop = st.checkbox("🔄 구간 무한 반복 재생", value=True)
            
            if st.button("▶️ 처음부터 다시 재생", use_container_width=True):
                st.rerun()
                
            st.info("💡 '무한 반복'을 켜두면 해당 파트가 끝난 뒤 자동으로 처음으로 돌아가 쉐도잉 연습을 돕습니다.")
            st.caption(f"현재 설정된 구간: {tgt['start_sec']}초 ~ {tgt['end_sec']}초")
        
        with col2:
            # 유튜브 루프 파라미터 적용 (loop=1과 playlist=videoId 조합)
            loop_param = f"&loop=1&playlist={v_id}" if do_loop else ""
            # cc_load_policy=1을 추가하여 유튜브 자체 자막도 함께 활성화
            embed_url = f"https://www.youtube.com/embed/{v_id}?start={tgt['start_sec']}&end={tgt['end_sec']}&autoplay=1{loop_param}&cc_load_policy=1"
            
            st.components.v1.iframe(embed_url, height=450)
    else:
        st.warning("⚠️ 매칭 데이터(final_mapping.json)가 없습니다. 관리자 모드에서 먼저 데이터를 생성해주세요.")