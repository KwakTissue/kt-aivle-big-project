'''
어린이집 자체평가시 제공하는 streamlit으로 구현한 프로토타입 페이지
'''
import os
from PIL import Image
import streamlit as st  
import pandas as pd
from datetime import datetime, timedelta

# 페이지 레이아웃 조정
st.set_page_config(layout='wide')


# 상위 디렉토리의 경로를 만듦
parent_directory = os.path.dirname(os.path.dirname(__file__))

# CSV 파일 불러오기
df = pd.read_csv(os.path.join(parent_directory, 'data', '어린이집_total - 긍부정키워드.csv'), encoding='UTF-8')

# session_state 초기화
if 'completed_keywords' not in st.session_state:
    st.session_state.completed_keywords = 0
    
with st.sidebar:
    st.title('어린이집 개인정보 입력창 🖥️') # 

    st.markdown('----------------------------------------')
    st.markdown("")
    
    
    question_text = '어린이집명을 입력해주세요 🏡' # 
    st.subheader(question_text)
    
    title = st.text_input('', '노원연두어린이집')
    
    st.markdown('----------------------------------------')

    
    
    question_text2 = '어린이집 주소를 입력해주세요 🛣️' # 
    st.subheader(question_text2)
    
    title1 = st.text_input('', '서울특별시 노원구 덕릉로70가길 21 중계센트럴파크아파트 내 보육시설')
    
    st.markdown('----------------------------------------')
    
    question_text2 = '어린이집 우편번호를 입력해주세요 📮' # 
    
    st.subheader(question_text2)
    title2 = st.text_input('', '01772')


# D-day 계산
if 'completed_keywords' in st.session_state:
    # 입력받은 어린이집명에 해당하는 행을 가져옴
    selected_row = df[df['어린이집'] == title].iloc[0]

    # 평가인증날짜와 현재날짜를 datetime 형식으로 변환
    evaluation_date = pd.to_datetime(selected_row['평가인증날짜'])
    current_date = pd.to_datetime(selected_row['현재날짜'])

    # D-day 계산
    days_left = (evaluation_date + timedelta(days=14) - current_date).days

    # D-day 출력 (한 줄로)
    if days_left > 0:
        
        st.title(f'{title}의 보완 사항 (제출 마감 : D - {days_left} 📅)')
    elif days_left == 0:

        st.title(f"{title}의 보완 사항 (제출 마감 : D - DAY 📅)")
    else:

        st.title(f"{title}의 보완 사항 (제출 시기가 이미 지났습니다 📅)")

    
st.markdown('----------------------------------------')


# 어린이집명 입력 시 카테고리 개수와 부정키워드 개수 출력
if title:
    test = df.loc[df['어린이집'] == title]

    # 중복된 카테고리를 제외하고 유니크한 카테고리만 가져오기
    unique_categories = test['카테고리'].unique()

    # 부정키워드가 있는 카테고리만 필터링
    non_empty_categories = [category for category in unique_categories if any(pd.notna(keyword) and keyword.strip() for keyword in test[test['카테고리'] == category]['부정키워드'].values)]

    # 유니크한, 부정키워드가 있는 카테고리의 개수 계산
    category_count = len(non_empty_categories)

    # 부정키워드가 있는 카테고리만 카운트
    negative_keywords_count = sum(test['부정키워드'].apply(lambda x: len(x.split(', ')) if pd.notna(x) and x else 0))

    st.error(f"#### {title}은 {category_count}개 카테고리에 {negative_keywords_count}개 부정키워드가 있습니다")
    
st.markdown('')

# 해당 어린이집의 부정키워드 개수 추적
total_keywords = negative_keywords_count

result_dict = {}

for index, row in test.iterrows():
    category = row["카테고리"]
    negative_keywords = row["부정키워드"].split(", ")
    result_dict[category] = {"부정키워드": negative_keywords}


col3, col4 = st.columns(2)    
with col3:
    selected_category = st.selectbox("**카테고리 선택**", list(result_dict.keys()))
    selected_category_negative_keywords = result_dict.get(selected_category, {}).get("부정키워드", [])
    

with col4:
    selected_negative_keyword = st.selectbox("**부정키워드 선택**", selected_category_negative_keywords)


st.markdown('----------------------------------------')

question_text1 = f'{selected_negative_keyword}에 대한 보완 방법을 작성해주세요'
st.success(f'##### {question_text1}')

negative_keyword_description = st.text_area("", "")

st.markdown('----------------------------------------')

st.info("##### 이미지 업로드 (📷)")
uploaded_image = st.file_uploader('', type=["jpg", "jpeg", "png"], key="file_uploader")


uploads_dir = 'uploads'
os.makedirs(uploads_dir, exist_ok=True)

col1, col2 = st.columns([20, 1])

# 제출 버튼
if col1.button("제출"):

    # 보완 완료된 키워드 수 증가
    st.session_state.completed_keywords += 1

    # 보완 완료된 경우
    if st.session_state.completed_keywords == total_keywords:
        # 수고 메시지 출력
        success_message = "모든 키워드가 성공적으로 제출되었습니다"
        st.markdown(f"### <div style='text-align:center;'>{success_message}</div>", unsafe_allow_html=True)
    else:
        # 제출 메시지 출력
        st.write(f"### {selected_category} 카테고리의 {selected_negative_keyword} 보완완료! 😊")

# 보완 상태 시각화 (Progress Bar)
st.markdown('')
st.progress(st.session_state.completed_keywords / total_keywords)

# 카테고리 선택 위에 보완 상태 텍스트 표시
status_text = f"### <div style='text-align:center;'> {st.session_state.completed_keywords}/{total_keywords}  완료</div>"
st.markdown(status_text, unsafe_allow_html=True)

# 문의 버튼
if col2.button("문의"):
    st.markdown('')
    st.markdown("### <div style='text-align:center;'>문의 홈페이지: [https://dbnew.educare.or.kr/index.php)</div>", unsafe_allow_html=True)