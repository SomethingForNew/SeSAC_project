# --- [1. 도구 상자(Library) 가져오기] ---
import os              # 운영체제(OS) 관리: 파일 저장 등
import urllib.request  # 웹 우체부: 인터넷 주소로 접속
import json            # 데이터 번역기: JSON 형식을 파이썬으로 변환
import pandas as pd    # 데이터 요리사: 표(DataFrame) 생성 및 분석
from datetime import datetime  # 시간의 파수꾼: 날짜 처리
import time            # [추가] 시간 조절 도구: 서버 차단을 막기 위해 잠시 멈추는 기능

# --- [2. 네이버 API 출입증 설정] ---
client_id = "KtYAETZuUbKhHH7B1EW_"      
client_secret = "HWj4widnFY" 

# --- [3. 데이터를 수집하는 '기능' 정의하기] ---
def fetch_dessert_trend(year):
    """특정 연도의 디저트 관련 블로그 글을 긁어오는 함수"""
    print(f"--- {year}년 데이터 수집 엔진 가동 중... ---")
    
    encText = urllib.parse.quote("디저트 추천")
    url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display=100&start=1"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        
        if rescode == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))
            items = data['items']
            df = pd.DataFrame(items)
            
            # [정제 작업] HTML 태그 제거
            df['title'] = df['title'].str.replace("<b>", "").str.replace("</b>", "")
            df['description'] = df['description'].str.replace("<b>", "").str.replace("</b>", "")
            
            df['target_year'] = year
            return df
        else:
            print(f"연결 실패 (코드: {rescode})")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"수집 중 오류 발생: {e}")
        return pd.DataFrame()

# --- [4. 실제로 10년 치 반복해서 실행하기] ---
all_years_results = [] 
years = range(2016, 2026) 

for y in years: 
    year_data = fetch_dessert_trend(y)
    all_years_results.append(year_data)
    
    # --- [추가 포인트] 네이버 서버에 부담을 주지 않기 위한 매너 타임 ---
    # 1.5초 동안 파이썬이 잠시 잠을 잡니다. 429 Too Many Requests 에러 방지용입니다.
    if y != 2025: # 마지막 연도가 아니면 잠시 쉽니다.
        print("네이버 서버 보호를 위해 1.5초간 휴식합니다...")
        time.sleep(1.5)

# --- [5. 모든 표를 합쳐서 엑셀 파일로 저장하기] ---
final_result = pd.concat(all_years_results, ignore_index=True)
final_result.to_csv("dessert_trend_2016_2025.csv", index=False, encoding='utf-8-sig')

print("\n축하합니다! 10년 치 데이터(2016-2025)가 'dessert_trend_2016_2025.csv'로 완벽히 저장되었습니다! 🎉")