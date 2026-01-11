import requests
import time
from datetime import datetime, timedelta # 날짜를 계산해주는 도구입니다

# 1. 신분증 설정
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 2. 시작 날짜와 종료 날짜 설정
start_date = datetime(2025, 3, 1) # 시작: 2025년 3월 1일
end_date = datetime(2025, 5, 31)  # 종료: 2025년 5월 31일

current_date = start_date

# 3. 날짜 반복 (시작일부터 종료일까지 하루씩 더해가며 반복)
while current_date <= end_date:
    # 네이버가 원하는 형식(YYYY-MM-DD)으로 날짜를 변환합니다
    target_date = current_date.strftime("%Y-%m-%d")
    print(f"\n📅 [작업 중] {target_date} 데이터 수집 시작")
    
    page = 1
    
    # 4. 페이지 반복 (해당 날짜의 모든 페이지 훑기)
    while True:
        url = f"https://land.naver.com/news/airsList.naver?baseDate={target_date}&page={page}&size=20"
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            news_list = data.get('list', [])

            # 만약 해당 페이지에 뉴스가 없다면 그 날짜는 끝!
            if not news_list:
                break 

            # 뉴스 제목 출력
            for news in news_list:
                title = news.get('title')
                print(f"   ({target_date} / {page}p) {title}")

            page += 1
            time.sleep(0.3) # 서버 매너 타임 (차단 방지)
            
        except Exception as e:
            print(f"   ❌ 에러 발생: {e}")
            break

    # 하루를 더해서 다음 날짜로 넘어갑니다
    current_date += timedelta(days=1)

print("\n✨ 모든 기간의 수집이 완료되었습니다!")