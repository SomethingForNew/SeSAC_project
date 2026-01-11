import requests # 웹 서버에 데이터를 요청(Request)하기 위해 사용하는 라이브러리입니다.
import csv # 데이터를 엑셀에서 읽을 수 있는 CSV 형식으로 저장하기 위한 라이브러리입니다.
from konlpy.tag import Okt # 한국어 문장에서 명사만 쏙쏙 뽑아내기 위한 형태소 분석기 도구입니다.

# 1. 도구 및 주소 설정
okt = Okt() # Okt라는 이름의 분석기(요리사)를 생성하여 변수에 담습니다.
url = "https://land.naver.com/news/airsList.naver?baseDate=2026-01-11&page=1&size=20" # 데이터를 가져올 목적지 주소입니다.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
} # 서버가 나를 '사람(브라우저)'으로 인식하게 만드는 신분증 정보입니다.

# 2. 서버에 데이터 요청
response = requests.get(url, headers=headers) # get(주소, 신분증): 해당 주소로 신분증을 지참해 데이터를 받으러 갑니다.
data = response.json() # .json(): 서버가 보내준 복잡한 응답 데이터를 파이썬이 이해하기 쉬운 사전(Dictionary) 형태로 변환합니다.
news_list = data.get('list', []) # .get('키이름', 기본값): 데이터 뭉치 안에서 'list'라는 상자를 찾고, 없으면 빈 리스트([])를 반환합니다.

# 3. 파일 열기 및 저장 (인자 상세 설명)
# open()의 인자들:
# - 'naver_news_final.csv': 생성할 파일의 이름입니다.
# - 'w': 'Write'의 약자로, 파일을 '쓰기 모드'로 열겠다는 뜻입니다. (기존 내용이 있다면 삭제하고 새로 씁니다.)
# - encoding='utf-8-sig': 한글이 깨지지 않게 저장하는 설정입니다. (특히 엑셀에서 열 때 필수입니다.)
# - newline='': 줄 바꿈이 이중으로 생기는 현상을 방지하여 표를 깔끔하게 만듭니다.
with open('naver_news_final.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f) # csv.writer(파일객체): 열어둔 파일(f)에 글을 써줄 '작가'를 배정합니다.
    
    # writerow(['항목1', '항목2']): 리스트 안의 내용들을 엑셀의 한 행(Row)에 칸별로 기록합니다.
    writer.writerow(['날짜', '언론사', '뉴스제목', '핵심키워드']) 
    
    for news in news_list: # 리스트 안의 뉴스들을 하나씩 순서대로 꺼냅니다.
        date = "2026-01-11"
        press = news.get('pressCorporationName') # 'pressCorporationName' 키값으로 언론사 이름을 가져옵니다.
        title = news.get('title') # 'title' 키값으로 뉴스 제목을 가져옵니다.
        
        # okt.nouns(문장): 문장 속에서 '명사'만 골라내어 리스트 형태로 만듭니다.
        nouns = okt.nouns(title) 
        
        # len(단어) >= 2: 단어의 길이가 2자 이상인 것만 필터링하여 키워드 리스트를 만듭니다.
        keywords = [n for n in nouns if len(n) >= 2]
        
        # ", ".join(리스트): 여러 단어들 사이에 쉼표를 넣어 하나의 긴 문장으로 합칩니다.
        keywords_str = ", ".join(keywords) 
        
        # 최종적으로 정제된 데이터들을 파일의 한 줄에 기록합니다.
        writer.writerow([date, press, title, keywords_str])

print("✨ 모든 인자 설정이 적용된 분석 저장이 완료되었습니다!")