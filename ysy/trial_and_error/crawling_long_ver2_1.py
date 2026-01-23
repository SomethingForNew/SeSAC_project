import os
import requests
import csv
import time
import random
from datetime import datetime, timedelta
from konlpy.tag import Okt

# 1. 자바 환경 설정
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jdk-21'

# 2. 분석기 준비
try:
    okt = Okt()
    print("✅ 형태소 분석기 준비 완료!")
except Exception as e:
    print(f"❌ 분석기 오류: {e}")

# 3. 설정 (시작 날짜를 4월 3일로 변경)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
start_date = datetime(2025, 4, 3) # 4월 3일부터 시작!
end_date = datetime(2025, 5, 31)
current_date = start_date

# 4. 파일 이어 쓰기 (모드를 'a'로 설정하여 기존 데이터 뒤에 붙입니다)
# encoding='utf-8-sig'를 유지하여 한글 깨짐을 방지합니다.
with open('naver_news_3months_ultra_safe.csv', 'a', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    
    # 주의: 'a' 모드에서는 제목줄(writer.writerow(['키워드 목록']))을 다시 쓰지 않습니다.
    # 이미 파일 맨 윗줄에 제목이 있기 때문입니다.

    total_page_count = 0 

    while current_date <= end_date:
        target_date = current_date.strftime("%Y-%m-%d")
        print(f"\n📅 [업데이트 중] {target_date} 수집 시작...")
        
        page = 1
        while True:
            url = f"https://land.naver.com/news/airsList.naver?baseDate={target_date}&page={page}&size=20"
            
            try:
                # [서버 매너] 1.0초에서 2.5초 사이의 넉넉한 휴식 (차단 방지 강화)
                time.sleep(random.uniform(1.0, 2.5))
                
                response = requests.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"   ⚠️ 서버 응답 지연(코드 {response.status_code}). 15초간 대피합니다.")
                    time.sleep(15)
                    continue

                data = response.json()
                news_list = data.get('list', [])

                if not news_list:
                    break 

                for news in news_list:
                    title = news.get('title')
                    nouns = okt.nouns(title)
                    keywords = [n for n in nouns if len(n) >= 2]
                    keywords_str = ", ".join(keywords)
                    if keywords_str:
                        writer.writerow([keywords_str]) # 기존 파일 끝에 추가
                
                print(f"   > {page}페이지 완료")
                
                page += 1
                total_page_count += 1

                # [세션 브레이크] 25페이지마다 10초간 긴 휴식
                if total_page_count % 25 == 0:
                    print("   🛌 서버의 의심을 피하기 위해 10초간 정지합니다.")
                    time.sleep(10)
                
            except Exception as e:
                print(f"   🛑 에러 발생: {e}. 10초 후 재시도.")
                time.sleep(10)
                break

        current_date += timedelta(days=1)

print("\n✨ [업데이트 완료] 4월 3일부터 5월 31일까지 모든 데이터가 추가되었습니다!")