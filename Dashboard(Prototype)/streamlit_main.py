'''
한국보육진흥원에게 제공하는 평가전&평가후 정보를
streamlit으로 구현한 프로타입 페이지
'''
import os
from PIL import Image
import streamlit as st  
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import altair as alt
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import datetime
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

# data
# import modelpkg.config as config
# from modelpkg.data import data_open, data_load

# 상위 디렉토리의 경로를 만듦
parent_directory = os.path.dirname(os.path.dirname(__file__))

# 페이지 레이아웃 조정
st.set_page_config(page_title="어린이집 평가 시각화", page_icon=":books:", layout="wide")

with st.sidebar:
    choose = option_menu("한국보육진흥원", ["평가 대상 정보", "종합 평가 결과"],
                         icons=['bi bi-check2-square', 'bi bi-check2-square'],
                         menu_icon="bi bi-house-heart", default_index=0,
                         styles={
                            "sidebar": {"background-color": "#F58D3D", "padding": "5!important"},
                            "container": {"padding": "5!important", "background-color": "#fafafa"},
                            "icon": {"color": "orange", "font-size": "25px"}, 
                            "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                            "nav-link-selected": {"background-color": "#02ab21"},
                        }
                        )
    
if choose == '평가 대상 정보':

    childcare_total = pd.read_csv(os.path.join(parent_directory, 'data', '어린이집_total - 어린이집_total.csv'), encoding='UTF-8')
    childcare_2021 = pd.read_csv(os.path.join(parent_directory, 'data', '어린이집_total - 어린이집_2021.csv'), encoding='UTF-8')
    df = childcare_total.copy()
    data = childcare_2021.copy()
    target_df = df[df['평가 인증 년월'].str[:4] == '2021']
    
    
    result = round((len(childcare_2021) / len(childcare_total)) * 100, 1)
    result = str(result)
    target_df = df[df['평가 인증 년월'].str[:4] == '2021']
    target_df2 = data[data['평가예정날짜'].str[:7] == '2024. 3']

    result = round((len(target_df) / len(df)) * 100, 1)
    result = str(result)

    st.info('올해 평가대상 어린이집의 개수는 '+str(len(target_df))+'개로 전체 어린이집 개수의 '+result+'% 입니다')
    
    
    col_count1, col_count2 = st.columns([0.5, 0.5])
    with col_count1:
        #지역별 평가대상
        st.markdown('<h1 style="font-size:40px;">3월 평가대상 어린이집 확인</h1>', unsafe_allow_html=True)
    with col_count2:
        bg_color = '#92C7CF'
        text_color = 'white'
        font_size = '24px'
        metric_htmal_childnum = f"""
            <div style="
                background-color: {bg_color};
                color: {text_color};
                border-radius: 5px;
                padding: 5px;
                text-align: center;
                font-size: {font_size};
                margin: 5px;
            ">
                <div style="font-weight: bold;">어린이집 개수</div>
                <div>{str(len(target_df2))}개</div>
            </div>
        """
        components.html(metric_htmal_childnum, height=100)
        
    #-------------------------------3월달 평가대상 컬럼----------------------------------------------------------------------------
    col_3months1, col_3months2 = st.columns([0.5, 0.5])
    with col_3months1:
        #------------------------------------------구별 평가대상-------------------------------------------------------------------
        st.success("대상 어린이집 명단")
        
        # 선택한 '구'에 해당하는 데이터만 필터링
        choice_data = ['어린이집명', '우편번호', '상세주소', '전화번호', '어린이집유형']
        filtered_df = data[data['평가예정날짜'].str[:7] == '2024. 3'][choice_data].reset_index(drop=True)
        filtered_df['우편번호'] = filtered_df['우편번호'].astype(str)
        filtered_df['우편번호'] = '0'+filtered_df['우편번호'].str.replace(',', '')
        # 선택한 '구'에 해당하는 데이터 출력
        st.write(filtered_df)

        
    with col_3months2:
        #---------------------------------------------3월달 평가대상 지도-------------------------------------------------------------------

        target_df2 = data[data['평가예정날짜'].str[:7] == '2024. 3']
        st.success("대상 어린이집 위치")

        # Folium 지도 불러오기
        seoul_map = folium.Map(location=[37.5389, 127.0049], zoom_start=11)

        # 마커와 클릭 이벤트 설정
        for index, row in target_df2.iterrows():
            location = [row['시설 위도(좌표값)'], row['시설 경도(좌표값)']]
            marker = folium.Marker(location=location, popup=f"마커 {index}")
            marker.add_to(seoul_map)

        # Folium 지도를 Streamlit에 표시
        st.components.v1.html(seoul_map._repr_html_(), width=700, height=400)


    st.markdown("<hr>", unsafe_allow_html=True)



    #------------------------------------어린이집 검색--------------------------------------------------------------------------
    col_checkchlid1, col_checkchlid2 = st.columns([0.5, 0.5])
    
    with col_checkchlid1:
        st.success('어린이집 검색')
        # 어린이집명을 직접 입력해서 검색
        selected_nursery_name = st.text_input('어린이집명 입력')
        st.markdown('')
        selected_nursery_name2 = st.text_input('우편번호 입력')
        st.markdown('')
        search_button = st.button('검색')
        col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
        
    with col_checkchlid2:
        #현재 날짜
        current_date = datetime.datetime(2024, 3, 1)

        if search_button:
            
            if selected_nursery_name:
                # 입력받은 어린이집명으로 필터링
                selected_row = data.loc[(data['어린이집명'] == selected_nursery_name) & (data['우편번호'] == int(selected_nursery_name2))]
                
                # 입력받은 어린이집명이 존재하는지 확인
                if not selected_row.empty:
                    selected_row = selected_row.iloc[0]  # 여러 개의 결과 중 첫 번째 행 선택

                    # '평가예정날짜'와 '평가마감날짜'를 datetime 형식으로 변환
                    selected_row['평가예정날짜'] = pd.to_datetime(selected_row['평가예정날짜'])
                    selected_row['평가마감날짜'] = pd.to_datetime(selected_row['평가마감날짜'])

                    # 현재 날짜와의 차이 계산
                    days_until_evaluation = (selected_row['평가예정날짜'] - current_date).days
                    days_until_evaluation2 = (selected_row['평가마감날짜'] - current_date).days

                    with col_checkchlid1:
                        # 결과를 텍스트 박스로 표시
                        if days_until_evaluation >= 0:
                            col_metrics1.metric(label='평가예정날짜', value=f'3월 1일', delta=f'D-Day {days_until_evaluation}')
                        else:              
                            col_metrics1.metric(label='평가예정날짜', value=f'3월 1일', delta=f'D-Day {days_until_evaluation}')
                            
                        if days_until_evaluation2 >= 0:
                            col_metrics2.metric(label='평가마감날짜', value=f'3월 15일', delta=f'D-Day {days_until_evaluation2}')
                        else:
                            col_metrics2.metric(label='평가마감날짜', value=f'3월 15일', delta=f'D-Day {days_until_evaluation2}')
                            
                    # 평가자 선정
                        col_metrics3.metric(label='평가자', value='이정담')
                    
                    # 추가: 평가예정날짜와 평가마감날짜가 몇 일인지도 표시
                    # st.markdown('<br>', unsafe_allow_html=True)
                    st.text(f"평가예정날짜: {selected_row['평가예정날짜'].strftime('%Y-%m-%d')} | 평가마감날짜: {selected_row['평가마감날짜'].strftime('%Y-%m-%d')}")

                    # Folium 지도 불러오기
                    seoul_map = folium.Map(location=[selected_row['시설 위도(좌표값)'], selected_row['시설 경도(좌표값)']], zoom_start=16)

                    # 마커와 클릭 이벤트 설정
                    location = selected_row['시설 위도(좌표값)'], selected_row['시설 경도(좌표값)']
                    marker = folium.Marker(location=location, popup=f"{selected_row['어린이집명']}")
                    marker.add_to(seoul_map)

                    # Folium 지도를 Streamlit에 표시
                    st.components.v1.html(seoul_map._repr_html_(), width=700, height=400)

                else:
                    st.warning(f"{selected_nursery_name}의 데이터는 존재하지 않습니다.")
            else:
                st.warning("어린이집명을 입력하세요.")
                
    st.markdown("<hr>", unsafe_allow_html=True)


############################################### 보육 진흥원 화면 (현장평가 진행 중-후) ###################################################
if choose == '종합 평가 결과':

    # 데이터 불러오기
    childcare_2021 = pd.read_csv(os.path.join(parent_directory, 'data', '어린이집_total - 어린이집_2021.csv'), encoding='UTF-8')
    data = childcare_2021.copy()


    # 서울 구 리스트
    seoul_districts = [
        '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
        '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
        '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
    ]



    # Folium을 사용하여 서울특별시 지도 불러오기
    seoul_map = folium.Map(location=[37.5505, 126.9680], zoom_start=13)

    # 서울 구별 위도, 경도 데이터
    seoul_district_coordinates = {
        '강남구': [37.514575, 127.0495556],
        '강동구': [37.52736667, 127.1258639],
        '강북구': [37.63695556, 127.0277194],
        '강서구': [37.54815556, 126.851675],
        '관악구': [37.47538611, 126.9538444],
        '광진구': [37.53573889, 127.0845333],
        '구로구': [37.49265, 126.8895972],
        '금천구': [37.44910833, 126.9041972],
        '노원구': [37.65146111, 127.0583889],
        '도봉구': [37.66583333, 127.0495222],
        '동대문구': [37.571625, 127.0421417],
        '동작구': [37.50965556, 126.941575],
        '마포구': [37.56070556, 126.9105306],
        '서대문구': [37.57636667, 126.9388972],
        '서초구': [37.48078611, 127.0348111],
        '성동구': [37.56061111, 127.039],
        '성북구': [37.58638333, 127.0203333],
        '송파구': [37.51175556, 127.1079306],
        '양천구': [37.51423056, 126.8687083],
        '영등포구': [37.52361111, 126.8983417],
        '용산구': [37.53609444, 126.9675222],
        '은평구': [37.59996944, 126.9312417],
        '종로구': [37.57037778, 126.9816417],
        '중구': [37.56100278, 126.9996417],
        '중랑구': [37.60380556, 127.0947778],
    }

    # 전체 구의 어린이집 평가완료 비율 계산
    all_districts_completion_percentage = data.groupby('평가완료여부').size().reset_index(name='count')
    all_districts_completion_percentage['percentage'] = all_districts_completion_percentage['count'] / len(data) * 100

    # 텍스트로 평가완료 비율 추가
    all_percentage_texts = []
    for index, row in all_districts_completion_percentage.iterrows():
        completion_percentage_value_all = row['percentage']
        completion_status_all = row['평가완료여부']
    
        percentage_text_all = f"{completion_status_all}: {round(completion_percentage_value_all)}%"

        all_percentage_texts.append(percentage_text_all)

        
        
        
    #------------------------------------------------------------------------ 가로 막대 차트 -----------------------------------------------------------------------------------




    


    #------------------------------------------------------------------------ 지도 시각화 -----------------------------------------------------------------------------------

    # 차트를 Streamlit에 표시
    col1, col2 = st.columns(2)
    
    # col1에 바 차트 추가
    with col1:
        
        col1.header('2024년 서울시 평가 완료 비율')
        # st.markdown('----------------------------------------')
        st.markdown('')
        st.markdown('')
        
        
        # 가로막대형 바차트 생성
        st.markdown('')
        st.error('현재까지 서울시 평가 완료 비율')
        
        all_districts_completion_percentage['평가완료여부_1'] = all_districts_completion_percentage['평가완료여부'].map({'Y': '완료', 'N': '미완료'})
        fig = px.bar(all_districts_completion_percentage,
                    x='percentage',
                    y='평가완료여부_1',
                    text='percentage',
                    color='평가완료여부',
                    orientation='h',  # 여기서 orientation을 'h'로 설정하여 가로막대형으로 변경
                    height=500,
                    width=700)
        

        # 바의 두께 조절
        fig.update_layout(bargap=0.5)  # 0.1은 바 사이의 간격을 나타내며, 이 값을 조절하여 바의 두께를 변경

        # 값이 높은 범주가 윗쪽에 오도록 정렬
        fig.update_layout(yaxis=dict(categoryorder='total ascending'))


        # 바 차트에 퍼센트 값을 표시하기 위한 추가적인 설정
        fig.update_traces(texttemplate='%{text:.0f}%', textposition='inside', textfont=dict(size=20))
        
        # x, y 축에 대한 레이아웃 조정
        fig.update_layout( xaxis=dict(title='') ,  # x축 레이블 수정
                           yaxis=dict(title='') # y축 레이블 수정
                         )  
        
        # 사용자 정의 범례 생성
        legend_labels = {'N': '미완료', 'Y': '완료'}
        legend_colors = {'완료': '#FDDB7E', '미완료': '#C2D178'}
        
        for i, label in enumerate(legend_labels):
            fig.data[i].marker.color = legend_colors[legend_labels[label]]
            fig.data[i].name = legend_labels[label]

        fig.update_layout(legend=dict(x=0.8, y=0.2, title='', font=dict(size=18)))  # 범례 위치 및 제목 설정
        
        fig.update_layout(
            xaxis=dict(
                title=dict(text=""),  # x 축 제목 제거
                tickfont=dict(size=16, color="black"),  # x 축 눈금 레이블 크기 및 색상 설정
            ),
            yaxis=dict(
                title=dict(text=""),  # y 축 제목 제거
                tickfont=dict(size=16, color="black"),  # y 축 눈금 레이블 크기 및 색상 설정
            )
        )
        
        fig.update_layout(
            paper_bgcolor='#FFFFFF',  # 차트의 배경색 설정
            plot_bgcolor='#FFFFFF'    # 차트 플롯 영역의 배경색 설정
        )
        
        
        st.plotly_chart(fig)


    # col2에 지도 시각화 추가
    with col2:
        col2.header('2024년 구별 평가 완료 비율')
        # st.markdown('----------------------------------------')
        st.markdown('')
        st.markdown('')
        
        col3, col4 = st.columns(2)
        
        with col3:
            
            # 드롭다운을 통해 선택한 지역구
            selected_district = st.selectbox('구 선택', ['전체'] + seoul_districts)
            
        
        # 선택한 지역구에 따라 데이터 필터링
        filtered_data = data if selected_district == '전체' else data[data['시군구명'] == selected_district]

        # '평가 인증 년월' 열의 값을 '0000년 00월' 형식으로 변환
        filtered_data['평가 인증 년월'] = filtered_data['평가 인증 년월'].astype(str)
        filtered_data['평가 인증 년월'] = filtered_data['평가 인증 년월'].apply(lambda x: f"{x[:4]}년 {x[5:7]}월" if x != '<NA>' else '')

        
        # 초기값 설정
        completion_status_y = '완료: 0%'
        completion_status_n = '미완료: 0%'
    
        if selected_district != '전체':
            
            
            if selected_district in seoul_district_coordinates:
                coord = seoul_district_coordinates[selected_district]
                
                # Folium 지도에 구의 어린이집 위치 표시
                folium.Marker(location=coord, popup=f"{selected_district} 구", icon=folium.Icon(color='blue', icon='info-sign')).add_to(seoul_map)

                # CircleMarker를 사용하여 원형 마커 추가
                folium.CircleMarker(
                    location=coord,
                    radius=30,
                    popup=f"{selected_district} 구",
                    color='black',
                    fill=True,
                    fill_color='skyblue',
                    fill_opacity=0.7
                ).add_to(seoul_map)

                # Folium 지도의 중심 좌표를 선택한 구의 위치로 설정
                seoul_map.location = [coord[0], coord[1]]

                # 선택한 구의 평가완료 비율 계산
                selected_district_data = filtered_data[filtered_data['시군구명'] == selected_district]

                if not selected_district_data.empty:
                    selected_district_completion_percentage = selected_district_data.groupby('평가완료여부').size().reset_index(name='count')

                    # 선택한 구에 해당하는 데이터가 있을 경우에만 평가완료 비율을 지도에 텍스트로 추가
                    if not selected_district_completion_percentage.empty:
                        selected_district_completion_percentage['percentage'] = selected_district_completion_percentage['count'] / len(selected_district_data) * 100

                        # 'Y'의 경우 계산
                        percentage_value_y = selected_district_completion_percentage.loc[selected_district_completion_percentage['평가완료여부'] == 'Y', 'percentage'].values
                        completion_status_y = f"완료: {round(percentage_value_y[0])}%" if len(percentage_value_y) > 0 else '완료: 0%'

                        # 'N'의 경우 계산
                        percentage_value_n = selected_district_completion_percentage.loc[selected_district_completion_percentage['평가완료여부'] == 'N', 'percentage'].values
                        completion_status_n = f"미완료: {round(percentage_value_n[0])}%" if len(percentage_value_n) > 0 else '미완료: 0%'

                        # Folium 지도에 값 표시
                        folium.Marker(
                            location=coord,
                            icon=folium.DivIcon(
                                html=f"<div style='position: relative; left: 35px; background-color: white; padding: 10px; border-radius: 20px; text-align: center; width: 80px; height: 60px;'>"
                                    f"<div><strong>{selected_district}</strong></div>"
                                    f"<div style='margin-top: 5px;'><strong>{completion_status_y}</strong></div>" 
                                    f"<div><strong>{completion_status_n}</strong></div>"
                                    f"</div>"
                            ),
                        ).add_to(seoul_map)
            
                        
                    else:
                        st.warning(f"선택한 {selected_district} 구에 대한 '평가완료' 데이터가 없습니다.")
                else:
                    st.warning(f"선택한 {selected_district} 구에 대한 데이터가 없습니다.")
            else:
                st.warning(f"선택한 {selected_district} 구에 대한 좌표 정보가 없습니다.")
                
        with col4:
            # 텍스트로 평가완료 비율 추가
            st.markdown('')
            st.info(f"{selected_district} 평가 완료 비율({completion_status_y}, {completion_status_n})")
            
        # Folium 지도를 Streamlit에 표시
        st.components.v1.html(seoul_map._repr_html_(), height=500)



    #--------------------------------------------------------------------------- 평가 결과 표 ---------------------------------------------------------------------------------


    st.markdown('----------------------------------------')

    # 표를 항상 표시하고 페이징 버튼만 추가
    st.header('2024년 평가 예정 어린이집의 지난 평가 결과')
    st.markdown('')
    st.markdown('')

    # 전체 데이터로 결과 데이터 정렬
    result_data = data[['어린이집명', '시군구명', '보육과정 및 상호작용', '보육환경 및 운영관리', '건강 및 안전', '교직원']] #'평가완료여부', '평가예정날짜', '평가마감날짜']]
    col5, col6 = st.columns([1, 6])
    with col5:
        # 테이블에 대한 정렬 기준을 선택할 수 있는 셀렉트박스 추가
        st.markdown('')
        st.markdown('')
        st.markdown('')
        st.success("정렬 기준 선택")
        
        selected_category_for_sort = st.selectbox('', result_data.columns[2:6])
       
        # 페이지 및 버튼 관련 상태
        current_page = st.session_state.get('current_page', 1)
        page_size = 10  # 페이지당 데이터 개수
        num_pages = (len(result_data) // page_size) + 1
        
        # 정렬 기준이 변경될 때마다 테이블을 업데이트
        col1, col2, col3,  = st.columns([1.1, 4, 0.5])
        col2.markdown('')
        
        # 이전 페이지 버튼
        prev_button_clicked = col2.button("이전 페이지") and current_page > 1
        col2.markdown('')

        # 다음 페이지 버튼
        next_button_clicked = col2.button("다음 페이지") and current_page < num_pages
        col2.markdown('')

        # 이전 페이지 버튼이 클릭되었을 때
        if prev_button_clicked:
            current_page -= 1

        # 다음 페이지 버튼이 클릭되었을 때
        if next_button_clicked:
            current_page += 1
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.button(f"{current_page}/{num_pages}", key=f"page_button_{current_page}")
            
    with col6:
        result_data = result_data.sort_values(by=selected_category_for_sort)
        
        # 현재 페이지의 데이터 가져오기
        start_index = (current_page - 1) * page_size
        end_index = current_page * page_size
        page_data = result_data.iloc[start_index:end_index, :]

        # 표에 대한 정렬 기준을 클릭 시 해당 기준으로 정렬되도록 변경
            # HTML을 사용하여 CSS를 적용하여 열 간격을 일정하게 조절
        table_html = page_data.to_html(index=False, classes=["table"], escape=False)

        # CSS 스타일을 적용한 표를 Markdown으로 출력
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.markdown("""
            <style>
                .table {
                    width: 100%;  /* 가로 길이를 조절할 수 있는 width 속성 추가 */
                    border-spacing: 0;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 10px;  /* 셀의 내용과 테두리 간격을 조절할 수 있는 padding 속성 추가 */
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('')

        # 페이지 정보 업데이트
        st.session_state['current_page'] = current_page        
   
    st.markdown('----------------------------------------')
    



    #----------------------------------------------------------------- 프로그래스 바 & 라디오 버튼-------------------------------------------------------------------------------
    ld_format = "%Y. %m. %d"
    new_format = "%Y년 %m월"
    data['평가예정날짜'] = pd.to_datetime(data['평가예정날짜'], format=ld_format).dt.strftime(new_format)
    data['평가예정월'] = data['평가예정날짜']
    
    #현재 날짜
    current_date = datetime.datetime(2024, 3, 1)
    # 각 월별로 '평가완료여부'의 비율 계산
    monthly_completion_percentage = data.groupby(['평가예정월', '평가완료여부']).size().unstack().fillna(0)
    monthly_completion_percentage['Total'] = monthly_completion_percentage['N'] + monthly_completion_percentage['Y']
    monthly_completion_percentage['평가완료비율(%)'] = (monthly_completion_percentage['Y'] / monthly_completion_percentage['Total']) * 100
    

    st.header(f"2024년 월별 평가 완료 현황")
    col2, col4 = st.columns([3, 7])
    with col2:
        st.markdown('')
        # Radio 박스로 다른 월 선택 (디폴트 값은 현재 날짜 월)
        default_month_str = '2024년 03월'
        selected_month_str = st.selectbox('', monthly_completion_percentage.index, index=monthly_completion_percentage.index.get_loc(default_month_str))
      
   
    #--------------------------------------------------------------------------- 현황 TEXT -------------------------------------------------------------------------------------
        
        # 선택한 월의 텍스트 정보 표시
        selected_month_data = data[data['평가예정월'] == selected_month_str]
        num_total_evaluations = selected_month_data.shape[0]
        num_completed_evaluations = selected_month_data[selected_month_data['평가완료여부'] == 'Y'].shape[0]
        num_not_completed_evaluations = selected_month_data[selected_month_data['평가완료여부'] == 'N'].shape[0]
        
        # 색상 및 스타일 지정
        bg_color = '#FFA07A'
        bg_color1 = '#3CB371'
        bg_color2 = '#9370DB'
        text_color = 'white'
        shadow_color = '#CD5C5C'
        shadow_color1 = '#2E8B57'
        shadow_color2 = '#663399'
        font_size = '24px'

        # HTML로 Metric 디자인
        metric_html_total = f"""
            <div style="
                background-color: {bg_color};
                color: {text_color};
                border-radius: 10px;
                box-shadow: 5px 5px 10px {shadow_color};
                padding: 10px;
                text-align: center;
                font-size: {font_size};
                margin: 5px;
            ">
                <div style="font-weight: bold;">총 평가 건수</div>
                <div>{num_total_evaluations}건</div>
            </div>
        """

        metric_html_completed = f"""
            <div style="
                background-color: {bg_color1};
                color: {text_color};
                border-radius: 10px;
                box-shadow: 5px 5px 10px {shadow_color1};
                padding: 10px;
                text-align: center;
                font-size: {font_size};
                margin: 5px;
            ">
                <div style="font-weight: bold;">평가 완료 건수</div>
                <div>{num_completed_evaluations}건</div>
            </div>
        """

        metric_html_not_completed = f"""
            <div style="
                background-color: {bg_color2};
                color: {text_color};
                border-radius: 10px;
                box-shadow: 5px 5px 10px {shadow_color2};
                padding: 10px;
                text-align: center;
                font-size: {font_size};
                margin: 5px;
            ">
                <div style="font-weight: bold;">평가 미완료 건수</div>
                <div>{num_not_completed_evaluations}건</div>
            </div>
        """

        # st.metric 함수 사용
        components.html(metric_html_total, height=100)
        components.html(metric_html_completed, height=100)
        components.html(metric_html_not_completed, height=100)

    #--------------------------------------------------------------------------- 현황 차트 -------------------------------------------------------------------------------------

    with col4:
        # 선택한 월의 데이터 필터링
        selected_month_data_chart = data[data['평가예정월'] == selected_month_str]

        
        # 월별 전체 개수 및 'Y'값 개수 계산
        total_evaluations_chart = len(selected_month_data_chart)
        completed_evaluations_chart = (selected_month_data_chart['평가완료여부'] == 'Y').sum()
        
        st.markdown('')
        st.markdown('')
        
        
        st.error(f'{selected_month_str} 평가 현황')
        # 바 차트 생성
        fig_chart = px.bar(x=[total_evaluations_chart, completed_evaluations_chart],
                        y=['전체', '평가완료'],
                        text=[total_evaluations_chart, completed_evaluations_chart],
                        height=350,
                        width=900,
                        color=['전체', '평가완료'],  # 여기에 원하는 색상을 지정
                        orientation='h',  # 여기서 orientation을 'h'로 설정하여 가로막대형으로 변경
                        color_discrete_map={'전체': '#FDDB7E', '평가완료': '#C2D178'})

        
        # x 및 y 축 레이블 및 숫자의 크기 및 색상 변경
        fig_chart.update_layout(
            xaxis=dict(
                title=dict(text=""),  # x 축 제목 제거
                tickfont=dict(size=16, color="black"),  # x 축 눈금 레이블 크기 및 색상 설정
            ),
            yaxis=dict(
                title=dict(text=""),  # y 축 제목 제거
                tickfont=dict(size=16, color="black"),  # y 축 눈금 레이블 크기 및 색상 설정
            )
        )
        
        # 범례의 제목 변경
        fig_chart.update_layout(legend_title_text='')
        
        # 범례의 글자 크기 조절
        fig_chart.update_layout(legend=dict(title=dict(font=dict(size=16)), font=dict(size=16)))
        
        # 바의 두께 조절
        fig_chart.update_layout(bargap=0.5)  # 0.1은 바 사이의 간격을 나타내며, 이 값을 조절하여 바의 두께를 변경
        
        # 값이 높은 범주가 윗쪽에 오도록 정렬
        fig_chart.update_layout(yaxis=dict(categoryorder='total ascending'))
        
        # 바 차트에 퍼센트 값을 표시하기 위한 추가적인 설정
        fig_chart.update_traces(texttemplate='%{text}건', textposition='inside', textfont=dict(size=20))
        
        fig.update_layout(
            paper_bgcolor='#FFFFFF',  # 차트의 배경색 설정
            plot_bgcolor='#FFFFFF'    # 차트 플롯 영역의 배경색 설정
        )

        
        # 차트를 Streamlit에 표시
        st.plotly_chart(fig_chart)
        
    #----------------------------------------------------------------- 프로그래스 바 & 라디오 버튼-------------------------------------------------------------------------------


    # 선택한 월의 프로그래스 바 및 정보 표시
    selected_month_progress = st.progress(monthly_completion_percentage.loc[selected_month_str, '평가완료비율(%)'] / 100)
    st.markdown('<br>', unsafe_allow_html=True)

    # Markdown으로 텍스트 화면 가운데 정렬
    st.markdown(f'<div style="text-align: center; font-size: 19px;">[{round(monthly_completion_percentage.loc[selected_month_str, "평가완료비율(%)"])}% 평가완료]</div>', unsafe_allow_html=True)
    st.markdown('')
    
#------------------------------------------------------------------라디오 버튼 & 프로그래스 바-------------------------------------------------------------------------------



    st.markdown('----------------------------------------')
    
    # 카테고리별 어린이집 평가 결과 섹션 시작
    st.header('영역별 어린이집 평가 키워드')

    # 긍정적/부정적 키워드 워드 클라우드 표시
    selected_category = st.radio('', ['보육과정 및 상호작용', '보육환경 및 운영관리', '건강 및 안전', '교직원'], key='unique_key')

    # st.markdown('<br>', unsafe_allow_html=True)

    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

    # '개선완료'로 표시된 어린이집 개수 계산
    total_improvement_completed = sum([
        (data['보육과정 및 상호작용'].isin(['우수', '보통'])).sum(),
        (data['보육환경 및 운영관리'].isin(['우수', '보통'])).sum(),
        (data['건강 및 안전'].isin(['우수', '보통'])).sum(),
        (data['교직원'].isin(['우수', '보통'])).sum()
    ])

    # '개선필요'로 표시된 어린이집 개수 계산
    total_improvement_needed = sum([
        (data['보육과정 및 상호작용'] == '개선필요').sum(),
        (data['보육환경 및 운영관리'] == '개선필요').sum(),
        (data['건강 및 안전'] == '개선필요').sum(),
        (data['교직원'] == '개선필요').sum()
    ])

    # 전체 어린이집 개수 계산
    total_centers = sum([
        len(data['보육과정 및 상호작용']),
        len(data['보육환경 및 운영관리']),
        len(data['건강 및 안전']),
        len(data['교직원'])
    ])

    sucess_dict = {'보육과정 및 상호작용' : [1790, 953, 837], '보육환경 및 운영관리' : [1530, 930, 600], '건강 및 안전' : [931, 500, 431], '교직원' : [541, 451, 90]}

    total_improvements, completed_improvements, remaining_improvements = sucess_dict[selected_category][0], sucess_dict[selected_category][1], sucess_dict[selected_category][2]


    # 텍스트 표시
    st.info(f"**(전체 키워드 {total_improvements}개)**  /   {selected_category}은(는) **개선완료 키워드** **{completed_improvements}개,** \n **개선필요 키워드** **{remaining_improvements}개** 입니다")
    st.markdown('')

    # 개선완료 비율 계산
    completion_ratio = completed_improvements / total_improvements

    # Progress Bar 표시
    st.progress(completion_ratio)
    st.markdown('<br>', unsafe_allow_html=True)

    # Markdown으로 텍스트 화면 가운데 정렬
    st.markdown(f'<div style="text-align: center;font-size: 19px;">[{round(completion_ratio*100)}% 개선완료]</div>', unsafe_allow_html=True)


    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)




    #-------------------------------------------------------------------워드 클라우드------------------------------------------------------------------------------------------


    
    file_path_test = 'test (1).csv'
    data_test = pd.read_csv(os.path.join(parent_directory, 'data', '어린이집_total - 긍부정키워드.csv'), encoding='UTF-8')

    positive_keywords = ' '.join([x for x in data_test[data_test['카테고리'] == selected_category]['긍정키워드'] if x != 'Nothing'])
    wordcloud_positive = WordCloud(width=400, height=300, background_color='white', font_path='C:/Windows/fonts/HMKMRHD.TTF').generate(positive_keywords)

    negative_keywords = ' '.join([x for x in data_test[data_test['카테고리'] == selected_category]['부정키워드'] if x != 'Nothing'])
    wordcloud_negative = WordCloud(width=400, height=300, background_color='black', font_path='C:/Windows/fonts/HMKMRHD.TTF').generate(negative_keywords)

    # 두 개의 컬럼에 워드 클라우드 표시
    col1, col2, col3 = st.columns([0.7, 2.4, 1.7])
    with col2:
    # 긍정적 키워드 텍스트 표시
        st.subheader('긍정적 키워드 😊')
        st.markdown('<br>', unsafe_allow_html=True)
        st.image(wordcloud_positive.to_array(), width=None)

    with col3:
        st.subheader('보완점 키워드 😅')
        st.markdown('<br>', unsafe_allow_html=True)
        st.image(wordcloud_negative.to_array(), width=None)


    # 차트와 서브헤더 사이 간격 추가
    st.markdown('----------------------------------------')
    st.markdown('<br>', unsafe_allow_html=True)
