'''
원래 프로토타입 구축시 구글클라우드에 연결해서 구글스프레드 시트 데이터 추출과 로드를 했지만
구글클라우드 무료 크레딧 모두 사용해서 현재는 CSV파일로 대체 했습니다.
밑 코드는 그전 구글클라우드를 통해 데이터를 연동한 코드입니다.
'''

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import os

# 현재 스크립트의 디렉토리를 가져옴
current_directory = os.path.dirname(__file__)

# 상위 디렉토리의 경로를 만듦
parent_directory = os.path.dirname(os.path.dirname(current_directory))

# 데이터 파일의 경로를 만듦
json_file_path = os.path.join(parent_directory, 'aivle-big-project-409307-c5e8f637da87.json')


def data_open(url, sheet_name):
    # 스코프 및 자격 증명 설정
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    json_file = json_file_path
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)

    # 구글 스프레드시트에 연결
    gc = gspread.authorize(credentials)

    # 스프레드시트 URL로부터 문서 열기
    sheet_url = url
    doc = gc.open_by_url(sheet_url)

    # 워크시트 이름으로부터 워크시트 가져오기
    worksheet = doc.worksheet(sheet_name)

    # 워크시트를 데이터프레임으로 읽기
    df = get_as_dataframe(worksheet, evaluate_formulas=True)
    df = df.dropna(axis=0, how='all').dropna(axis=1, how='all')

    return df, worksheet

def data_load(data, worksheet):
    set_with_dataframe(worksheet, data, include_index=False)
