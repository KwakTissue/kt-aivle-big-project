'''
현장평가자가 어린이집에서 평가시 사용할 streamlit으로 구현한 프로토타입 페이지
'''
import streamlit as st
import pandas as pd
import random
from streamlit_folium import folium_static
import folium
from datetime import datetime 
import json
from streamlit_option_menu import option_menu
import os

# 상위 디렉토리의 경로를 만듦
parent_directory = os.path.dirname(os.path.dirname(__file__))

# CSV 파일 불러오기
df = pd.read_csv(os.path.join(parent_directory, 'data', '어린이집_total - 어린이집_2021.csv'), encoding='UTF-8')
df_check = pd.read_csv(os.path.join(parent_directory, 'data', '어린이집_total - 현장평가.csv'), encoding='UTF-8')

# 세션 상태에 입력한 값을 저장할 딕셔너리
session_state = st.session_state

# 초기값 설정
if 'core_indicator' not in session_state or session_state.core_indicator is None:
    session_state.core_indicator = None
if 'sub_indicator' not in session_state or session_state.sub_indicator is None:
    session_state.sub_indicator = None
if 'sub_item' not in session_state or session_state.sub_item is None:
    session_state.sub_item = None
if 'response_dict' not in session_state or session_state.response_dict is None:
    session_state.response_dict = {}

st.title('현장평가자 검사지')
st.markdown('-------------------------------------------------------------------')

with st.sidebar:
    choose = option_menu("현장평가 APP", ["사전 정보", "체크리스트"],
                         icons=['bi bi-info-circle', 'bi bi-list-check'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
                            "container": {"padding": "5!important", "background-color": "#fafafa"},
                            "icon": {"color": "orange", "font-size": "25px"}, 
                            "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                            "nav-link-selected": {"background-color": "#02ab21"},
                        }
                        )
    
if choose == '사전 정보':
    col1, col2 = st.columns(2)

    col1.info('##### 평가 일자를 입력하세요')
    col1.date_input('', datetime(2024, 3, 1))

    st.markdown('')

    # HTML 스타일을 사용하여 큰 글씨로 평가자 이름 안내
    col2.info('##### 평가자 아이디를 입력하세요')
    # 이름 입력을 위한 텍스트 상자 생성
    id_input = col2.text_input('')
    
    # 이름이 입력되었을 경우
    if id_input:
        # 어린이집 코드를 랜덤으로 선택
        st.markdown('-------------------------------------------------------------------')
    
        if 'selected_kindergarten_code' not in session_state or session_state.selected_kindergarten_code is None or id_input != session_state.selected_name:
            unique_kindergarten_codes = 11350001006 # 노원연두어린이집
            random_kindergarten_code = 11350001006
            session_state.selected_kindergarten_code = random_kindergarten_code
            session_state.selected_name = id_input  # 새로운 이름 저장

        # 선택된 어린이집명 출력
        selected_kindergarten_name = df[df['어린이집코드'] == session_state.selected_kindergarten_code]['어린이집명'].values[0]
        st.success(f"#### 평가자: 이정담")
        st.error(f"#### 평가자에게 배정된 어린이집: {selected_kindergarten_name}")
        st.markdown("")

        # 선택된 어린이집의 추가 정보 가져오기
        selected_kindergarten = df[df['어린이집코드'] == session_state.selected_kindergarten_code].reset_index(drop=True)

        # Folium을 사용하여 지도에 위치 표시
        st.success(f"{selected_kindergarten_name}의 위치")
        m = folium.Map(location=[selected_kindergarten.iloc[0]['시설 위도(좌표값)'], selected_kindergarten.iloc[0]['시설 경도(좌표값)']], zoom_start=17)

        # Folium Marker로 위치 표시
        folium.Marker(
            location=[selected_kindergarten.iloc[0]['시설 위도(좌표값)'], selected_kindergarten.iloc[0]['시설 경도(좌표값)']],
            popup='어린이집 위치',
            icon=folium.Icon(color='red')
        ).add_to(m)

        # Folium 지도를 Streamlit에 출력
        folium_static(m)
        st.markdown("")
        # 선택된 어린이집의 정보를 표 형식으로 출력
        st.success(f"{selected_kindergarten_name}의 2021년 평가 결과")
        st.table(selected_kindergarten[['보육과정 및 상호작용', '보육환경 및 운영관리', '건강 및 안전', '교직원']])

if choose == '체크리스트':
    st.info('### 체크리스트')
    st.markdown("")

    # 핵심지표 선택
    core_indicator = st.selectbox('핵심지표 선택', df_check['핵심지표'].unique())
    if core_indicator != session_state.core_indicator:
        session_state.core_indicator = core_indicator
        session_state.sub_indicator = None
        session_state.sub_item = None

    # 선택된 핵심지표에 해당하는 세부지표 선택
    sub_indicator_options = st.selectbox('세부지표 선택', df_check[df_check['핵심지표'] == core_indicator]['세부지표'].unique())
    if sub_indicator_options != session_state.sub_indicator:
        session_state.sub_indicator = sub_indicator_options
        session_state.sub_item = None

    # 선택된 세부지표에 해당하는 세부항목 선택
    sub_item_options = df_check[(df_check['핵심지표'] == core_indicator) & (df_check['세부지표'] == sub_indicator_options)]['세부항목'].unique()
    
    st.markdown('-------------------------------------------------------------------')
    # 객관식 질문 출력
    st.success('#### YES/NO 질문')
    st.markdown("")
    multiple_choice_questions = df_check[(df_check['핵심지표'] == core_indicator) & (df_check['세부지표'] == sub_indicator_options) & (df_check['유형'] == '객관식')]

    if not multiple_choice_questions.empty:
        for idx, row in multiple_choice_questions.iterrows():
            question_text = row['질문']
            checkbox_key = f'{question_text}'  # 질문 텍스트를 키로 사용
            answer = st.checkbox(question_text, key=checkbox_key, value=session_state.response_dict.get(checkbox_key, False))

            # 체크박스의 상태를 딕셔너리에 저장
            session_state.response_dict[checkbox_key] = answer
    else:
        st.warning("선택한 세부지표에 대한 객관식 질문이 없습니다.")
        
    
    # 추가된 부분: 세부지표 내에 서술형 질문이 없으면 알림 메시지 출력
    st.markdown('')
    st.markdown('')
    
    descriptive_questions = df_check[(df_check['핵심지표'] == core_indicator) & (df_check['세부지표'] == sub_indicator_options) & (df_check['유형'] == '서술형')]
    if not descriptive_questions.empty:
        st.warning('#### 서술형 질문')
        st.markdown("")
        for idx, row in descriptive_questions.iterrows():
            question_text = row['질문']
            textarea_key = f'{question_text}'  # 질문 텍스트를 키로 사용
            label_text = f"<span style='font-size:20px;'>{question_text}</span>"
            st.markdown(label_text, unsafe_allow_html=True)

            answer = st.text_area('', key=textarea_key, value=session_state.response_dict.get(textarea_key, ''))

            # 텍스트 에어리어의 상태를 딕셔너리에 저장
            session_state.response_dict[textarea_key] = answer
            st.markdown("")
    else:
        st.warning('#### 서술형 질문')
        
        st.warning("선택한 세부지표에 대한 서술형 질문이 없습니다.")
    
    st.markdown("")

    # 저장 버튼 추가
    if st.button('제출'):
        # JSON 파일로 저장
        #with open('응답결과.json', 'w', encoding='utf-8') as json_file:
        #    json.dump(session_state.response_dict, json_file, ensure_ascii=False, indent=2)

        st.success('응답이 성공적으로 제출되었습니다.')