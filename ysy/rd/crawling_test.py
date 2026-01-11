import requests # 웹 서버에 데이터를 달라고 요청하는 도구입니다.
import csv      # 데이터를 엑셀(CSV) 형식으로 저장하기 위한 도구입니다.
import jpype    # 파이썬 안에서 자바(Java) 엔진을 강제로 깨우는 도구입니다.
from konlpy.tag import Okt # 한국어 문장에서 명사(단어)를 골라내는 분석기입니다.

# 1. 자바 엔진(JVM) 경로 설정
# r은 'Raw string'의 약자로, 경로의 역슬래시(\)를 글자 그대로 인식하게 합니다.
# jvm.dll은 자바의 핵심 심장부 파일입니다.
jvm_path = r'C:\Program Files\Java\jdk-21\bin\server\jvm.dll'

# 2. 자바 엔진 실행 체크
# 이미 자바가 실행 중인지(isJVMStarted) 확인하고, 안 켜져 있다면(not) 실행합니다.
if not jpype.isJVMStarted():
    jpype.startJVM(jvm_path) # 지정한 주소에 있는 자바 엔진을 가동합니다.

# 3. 분석기(요리사)와 대상 설정
okt = Okt() # 형태소 분석기 Okt를 소환하여 'okt'라는 변수에 담습니다.
target_date = "2026-01-11" # 수집하고 싶은 날짜를 글자 형태로 정합니다.

# API 주소: f"..."는 문자열 안에 {변수}를 넣을 수 있게 해주는 편리한 방식입니다.
url = f"https://land.naver.com/news/airsList.naver?baseDate={target_date}&page=1&size=20"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
} # 서버에 "나는 사람이 쓰는 브라우저예요"라고 알려주는 신분증입니다.

# 4. 데이터 요청 및 응답 수신
response = requests.get(url, headers=headers) # 설정한 주소로 데이터를 요청합니다.
data = response.json() # 서버가 준 복잡한 데이터를 파이썬 사전(Dictionary) 구조로 변환합니다.
news_list = data.get('list', []) # 데이터 뭉치에서 'list'라는 뉴스 목록만 쏙 뽑아냅니다.

# 5. CSV 파일 저장 (파일 열기)
# 'w': 쓰기 모드, 'utf-8-sig': 한글 깨짐 방지, 'newline=""': 줄 사이 빈칸 방지
with open('naver_news_final_check.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f) # 파일(f)에 글을 써줄 '작가(writer)'를 고용합니다.
    writer.writerow(['날짜', '언론사', '뉴스제목', '핵심키워드']) # 엑셀의 맨 윗줄 제목을 씁니다.
    
    # 뉴스 목록(news_list)에서 뉴스 하나씩(news) 꺼내어 반복합니다.
    for news in news_list:
        press = news.get('pressCorporationName') # 언론사 이름을 가져옵니다.
        title = news.get('title') # 뉴스 제목을 가져옵니다.
        
        # [데이터 정제 시작]
        # okt.nouns: 제목에서 명사만 추출 (예: '강남 아파트' -> ['강남', '아파트'])
        nouns = okt.nouns(title) 
        
        # 2글자 이상인 유의미한 단어만 남기는 필터링 과정입니다.
        keywords = [n for n in nouns if len(n) >= 2]
        
        # ", ".join: 단어 리스트를 하나의 문자열로 합칩니다. (['강남', '아파트'] -> "강남, 아파트")
        keywords_str = ", ".join(keywords) 
        
        # 작가(writer)에게 실제 데이터 한 줄을 쓰라고 명령합니다.
        writer.writerow([target_date, press, title, keywords_str])

print("✨ [완료] 분석된 데이터가 파일에 잘 저장되었습니다!")