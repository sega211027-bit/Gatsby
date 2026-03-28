# [1. 세션 상태에 '현재 선택된 회차'를 기억함]
if 'last_selected_id' not in st.session_state:
    st.session_state.last_selected_id = None

# [2. 드롭박스에서 선택된 정보를 하나의 ID로 만듦]
current_id = f"{day}-{rnd}-{turn}"

# [3. 트리거 판별: 회차가 바뀌거나 '다시 재생' 버튼을 눌렀을 때만 v_key 갱신]
# 토글(loop_active)이 바뀌는 것은 여기에 포함되지 않으므로 영상이 리셋되지 않음
if st.session_state.last_selected_id != current_id:
    st.session_state.v_key = str(time.time())
    st.session_state.last_selected_id = current_id

# [4. 버튼 트리거 (수동 강제 리셋)]
# with col1: 블록 내부
if st.button("▶️ 처음부터 다시 재생"):
    st.session_state.v_key = str(time.time())
    st.rerun()

# [5. 기존 유튜브 API 그대로 사용]
# loop_active 값만 URL에 반영됨 (v_key가 그대로면 브라우저가 재생 시점을 유지함)
params = f"start={s_val}&end={e_val}&autoplay=1&playlist={v_id}&loop={'1' if loop_active else '0'}"
final_src = f"https://www.youtube.com/embed/{v_id}?{params}&t={st.session_state.v_key}"
