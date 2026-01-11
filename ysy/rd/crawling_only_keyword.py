import os
import requests
import csv
import time
from konlpy.tag import Okt

# 1. 자바의 위치를 컴퓨터 주소록에 '강제로' 등록 (가장 중요!)
# 소영님의 실제 설치 경로인 'C:\Program Files\Java\jdk-21'을 정확히 적어줍니다.
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'

# 2. 요리사(분석기) 준비
# 이제 KoNLPy가 위에서 설정한 JAVA_HOME을 보고 자바를 완벽하게 인식합니다.
try:
    okt = Okt() 
    print("✅ 분석기(Okt)가 준비되었습니다.")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    print("TIP: 자바 설치 폴더 이름이 jdk-21이 맞는지 다시 확인해주세요!")

# 3. 데이터 가져올 대상 설정 (테스트용 오늘 날짜)
target_date = "2026-01-11"
url = f"https://land.naver.com/news/airsList.naver?baseDate={target_date}&page=1&size=20"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 4. 데이터 요청 및 변환
response = requests.get(url, headers=headers)
data = response.json()
news_list = data.get('list', [])

# 5. 오직 '키워드 목록'만 저장
with open('only_keywords_final.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f) # 파일에 글을 써줄 작가를 고용
    writer.writerow(['키워드 목록']) # 엑셀의 헤더(제목줄)를 딱 하나만 만듭니다.
    
    for news in news_list:
        title = news.get('title') # 뉴스 제목만 가져오기
        
        # 제목에서 명사만 추출
        nouns = okt.nouns(title) 
        
        # 2글자 이상의 의미 있는 단어만 필터링 (조사, 한글자 단어 제거)
        keywords = [n for n in nouns if len(n) >= 2]
        
        # 단어들을 콤마(,)로 연결해 하나의 문장처럼 만듭니다.
        keywords_str = ", ".join(keywords) 
        
        # 만약 추출된 키워드가 있다면 파일에 한 줄 기록
        if keywords_str:
            writer.writerow([keywords_str]) # 엑셀 한 행에 키워드 뭉치만 쏙!

print("✨ [완료] 날짜/신문사 없이 키워드만 저장되었습니다!")