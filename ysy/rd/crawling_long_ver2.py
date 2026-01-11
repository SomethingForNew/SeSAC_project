import os
import requests
import csv
import time
from datetime import datetime, timedelta
from konlpy.tag import Okt

# 1. 자바 환경 설정 (소영님 컴퓨터 경로에 맞춤)
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'

# 2. 분석기 준비
try:
    okt = Okt()
    print("✅ 형태소 분석기 준비 완료!")
except Exception as e:
    print(f"❌ 분석기 준비 중 오류 발생: {e}")

# 3. 설정 및 날짜 범위 지정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
start_date = datetime(2025, 3, 1)
end_date = datetime(2025, 5, 31)
current_date = start_date

# 4. CSV 파일 열기 (한 번 열어서 모든 데이터를 계속 추가합니다)
# 파일명: naver_news_3months_keywords.csv
with open('naver_news_3months_keywords.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['키워드 목록']) # 엑셀 첫 줄 제목

    # [날짜 반복 시작]
    while current_date <= end_date:
        target_date = current_date.strftime("%Y-%m-%d")
        print(f"\n📅 [작업 중] {target_date} 수집 및 분석 시작")
        
        page = 1
        # [페이지 반복 시작]
        while True:
            url = f"https://land.naver.com/news/airsList.naver?baseDate={target_date}&page={page}&size=20"
            
            try:
                response = requests.get(url, headers=headers)
                data = response.json()
                news_list = data.get('list', [])

                if not news_list: # 더 이상 가져올 뉴스가 없으면 페이지 반복 종료
                    break 

                for news in news_list:
                    title = news.get('title')
                    
                    # 제목에서 명사만 추출
                    nouns = okt.nouns(title)
                    # 2글자 이상 단어만 필터링
                    keywords = [n for n in nouns if len(n) >= 2]
                    keywords_str = ", ".join(keywords)
                    
                    if keywords_str:
                        # 엑셀 파일에 키워드 한 줄 쓰기
                        writer.writerow([keywords_str])
                
                print(f"   > {page}페이지 완료")
                page += 1
                time.sleep(0.3) # 서버 과부하 방지 (매너 타임)
                
            except Exception as e:
                print(f"   ❌ {target_date} 작업 중 에러 발생: {e}")
                break

        # 다음 날짜로 이동
        current_date += timedelta(days=1)

print("\n✨ 모든 기간(3, 4, 5월)의 키워드 수집 및 저장이 완료되었습니다!")