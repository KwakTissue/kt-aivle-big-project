'''
서술형 평가 텍스트를 긍부정 분류후 키워드 추출 모델 코드
'''
import json
import requests
from datetime import datetime
import hmac, hashlib
from pytz import timezone
from keybert import KeyBERT
from kiwipiepy import Kiwi
from transformers import BertModel

import warnings
warnings.filterwarnings('ignore')
# key import
import modelpkg.config as config

# api로 모델 불러오는 함수
def api_model(text, n):
    # timestamp 생성
    timestamp = datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d%H%M%S%f")[:-3] 

    client_id = config.pn_client_id;
    client_secret = config.pn_client_secret;

    # HMAC 기반 signature 생성
    signature = hmac.new(
          key=client_secret.encode("UTF-8"), msg= f"{client_id}:{timestamp}".encode("UTF-8"), digestmod=hashlib.sha256
      ).hexdigest()

    url = "https://aiapi.genielabs.ai/kt/nlp/sentiment-analysis"

    # client_key
    client_key = config.pn_client_key

    
    
    headers = {
         "x-client-key":f"{client_key}",
         "x-client-signature":f"{signature}",
         "x-auth-timestamp": f"{timestamp}",
         "Content-Type": "application/json",
         "charset": "utf-8",
     }

    
    body = json.dumps({"text": f"{text}", "top_n": n}) 
    response = requests.post(url, data=body, headers=headers, verify=False)
    
    return response

def emotion_model(text, n=0): # text : 서술형 표현, n : 추출 키워드 개수
    
    # text = sentiment_predict(text)
    
    response = api_model(text, n)
    
    
    if response.status_code == 200:
        try:
            emotion = response.json()['result']['emotion']
            confidences = response.json()['result']['confidences']
            # words = response.json()['result']['expressions']
            
            # words = [text[word['start_offset']:word['start_offset']+word['length']] for word in response.json()['result']['expressions']]

            return confidences, emotion
                
        except json.decoder.JSONDecodeError:
            print(f'json.decoder.JSONDecodeError occured.\nresponse.text: "{response.text}"')
    else:
        print(f"response.status_code: {response.status_code}\nresponse.text: {response.text}")

# 긍부정 분류 함수
def emotion_classification(new_text):
    new_texts = new_text.split('$')

    positive_text = []
    negative_text = []

    for text in new_texts:
        if text[0] == ' ':
            confidence, emotion = emotion_model(text[1:], 5)
        else:
            confidence, emotion = emotion_model(text, 5)
        
        # 긍정, 부정 텍스트 분류
        if confidence['positive'] >= 0.7:
            positive_text.append(text)
        elif confidence['negative'] >= 0.7:
            negative_text.append(text)

    return positive_text, negative_text

# 명사 추출 함수
def noun_extractor(text):
    stop_words = ['어린이', '영유아', '어린이집', '아이', '의', '가', '이', '은', '들', '는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
    results = []
    kiwi = Kiwi()
    result = kiwi.analyze(text)
    for token, pos, _, _ in result[0][0]:
        if len(token) != 1 and pos.startswith('N') or pos.startswith('SL'):
            results.append(token)
            
    # 불용어 처리
    filtered_results = [word for word in results if word not in stop_words]
    
    return ' '.join(filtered_results)

# 키워드 추출 함수
def key_word(texts):
    model = BertModel.from_pretrained('skt/kobert-base-v1')
    kw_model = KeyBERT(model)
    results = []
    for text in texts:
        nouns = noun_extractor(text)
        keywords = kw_model.extract_keywords(nouns, keyphrase_ngram_range=(1, 1), stop_words=None, top_n=5)
        results.extend(keywords)
    results = [x[0] for x in results]
    return results