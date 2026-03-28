#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드") 관리자용
#is_admin = False 배포용, 지금 상태는 배포용


import streamlit as st
import pandas as pd
import re
import json
import os

# --- [1. 시간 변환 및 텍스트 정제 함수] ---

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
    """검색용: 소문자화, 철자통일, 알파벳만 추출"""
    t = str(txt).lower().replace('grey', 'gray')
    return "".join(re.findall(r'[a-z]', t))

def parse_transcript(content):
    """자막 파싱: 모든 노이즈 제거 후 글자 단위 시간 매핑"""
    full_stream = ""
    char_origin_map = []
    time_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)'
    
    lines = content.split('\n')
    current_sec = 0
    raw_data = []

    for line in lines:
        line = line.strip()
        if not line: continue
        
        # 시간 업데이트
        time_match = re.search(time_pattern, line)
        if time_match:
            t_str = time_match.group(1)
            parts = list(map(int, t_str.split(':')))
            if len(parts) == 3: # 시:분:초
                current_sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
            else: # 분:초
                current_sec = parts[0] * 60 + parts[1]

        # 노이즈(숫자, 한글, 특수기호) 제거
        clean_text = re.sub(r'[^a-zA-Z]', ' ', line)
        
        if clean_text.strip():
            idx = len(raw_data)
            raw_data.append({"seconds": current_sec})
            
            for char in clean_text.lower():
                if 'a' <= char <= 'z':
                    full_stream += char
                    char_origin_map.append(idx)
                    
    return full_stream, char_origin_map, raw_data

# --- [2. UI 및 매칭 로직] ---

st.set_page_config(page_title="Gatsby Roster System", layout="wide")
JSON_FILE = "final_mapping.json"
#is_admin = st.sidebar.checkbox("🛠️ 관리자 모드")
is_admin = False

if is_admin:
    st.title("🛠️ 초정밀 매칭 (시:분:초 포맷 완결판)")
    yt_url = st.text_input("유튜브 주소")
    roster_file = st.file_uploader("로스터(xlsx)", type=['xlsx'])
    sub_file = st.file_uploader("자막(txt)", type=['txt'])
    
    if st.button("🚀 매칭 및 데이터 생성"):
        try:
            v_id = re.search(r"(?:v=|\/|be\/)([0-9A-Za-z_-]{11})", yt_url).group(1)
            df = pd.read_excel(roster_file)
            content = sub_file.read().decode("utf-8")
            
            # 자막 데이터 분석
            full_stream, char_map, raw_data = parse_transcript(content)

            final_list = []
            last_pos = 0 

            for _, row in df.iterrows():
                search_s = ultra_simplify(row['시작 단어(5)'])
                search_e = ultra_simplify(row['마지막 단어(5)'])

                # 검색 (순차적 범위 검색)
                pos = full_stream.find(search_s, last_pos, last_pos + 30000)
                if pos == -1: pos = full_stream.find(search_s, last_pos)
                if pos == -1 and len(search_s) > 8: pos = full_stream.find(search_s[:8], last_pos)

                if pos != -1:
                    m_idx = char_map[pos]
                    s_s = raw_data[m_idx]['seconds']
                    s_t = format_seconds(s_s) # [핵심] 시:분:초 변환 적용
                    
                    e_pos = full_stream.find(search_e, pos + len(search_s))
                    if e_pos != -1:
                        e_idx = char_map[e_pos]
                        e_s = raw_data[e_idx]['seconds'] + 2
                        last_pos = e_pos 
                    else:
                        e_s = s_s + 120
                        last_pos = pos + len(search_s)
                else:
                    # 매칭 실패 시 보정
                    s_s = final_list[-1]['end_sec'] if final_list else 0
                    s_t = format_seconds(s_s)
                    e_s = s_s + 120
                    last_pos += 100

                final_list.append({
                    "Day": str(row['Day']), "ROUND": int(row['ROUND']), "회차": int(row['회차']),
                    "담당자": str(row['담당자']), "start_time": s_t,
                    "start_sec": int(s_s), "end_sec": int(e_s), "phrase": str(row['시작 단어(5)'])
                })
            
            st.success("✅ 시:분:초 포맷팅이 전 구간에 적용되었습니다.")
            st.download_button("📥 최종 JSON 다운로드", json.dumps({"video_id": v_id, "data": final_list}, ensure_ascii=False, indent=4), file_name=JSON_FILE)
        except Exception as e:
            st.error(f"오류: {e}")
else:
    # 멤버용 화면
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        v_id, r_data = cfg['video_id'], cfg['data']
        st.title("📖 Great Gatsby Audio Guide")
        day = st.sidebar.selectbox("Day", sorted(list(set(d['Day'] for d in r_data))))
        rnd = st.sidebar.selectbox("Round", sorted(list(set(d['ROUND'] for d in r_data if d['Day'] == day))))
        turn = st.sidebar.selectbox("회차", [d['회차'] for d in r_data if d['Day'] == day and d['ROUND'] == rnd])
        tgt = next(d for d in r_data if d['Day'] == day and d['ROUND'] == rnd and d['회차'] == turn)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("시작 시간", tgt['start_time'])
            st.info(f"**{tgt['담당자']}** 님 파트\n\n{tgt['phrase']}")
            if st.button("▶️ 재생"): st.rerun()
        with col2:
            url = f"https://www.youtube.com/embed/{v_id}?start={tgt['start_sec']}&end={tgt['end_sec']}&autoplay=1"
            st.components.v1.iframe(url, height=450)