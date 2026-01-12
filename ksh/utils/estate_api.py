import os
import requests
import time
import pandas as pd
from dotenv import load_dotenv

def fetch_estate():

    load_dotenv('../.env')
    API_KEY = os.getenv('PUBLIC_API_KEY')

    BASE_URL = f'http://openapi.seoul.go.kr:8088/{API_KEY}/json/tbLnOpendataRtmsV'

    years = [2023, 2024, 2025]
    districts = {
        '서초구': '11650',
        '강남구': '11680',
        '송파구': '11710'
    }

    rows_all = []
    step = 1000

    for year in years:
        for gu_nm, gu_cd in districts.items():
            start = 1

            while True:
                end = start + step - 1
                url = f'{BASE_URL}/{start}/{end}/{year}/{gu_cd}'

                res = requests.get(url)
                if res.status_code != 200:
                    print('요청 실패:', year, gu_nm)
                    break

                data = res.json().get('tbLnOpendataRtmsV', {})
                rows = data.get('row', [])

                if not rows:
                    break

                rows_all.extend(rows)
                print(f'{year} {gu_nm} {start}~{end} 수집')

                start += step
                time.sleep(2)

    df = pd.DataFrame(rows_all)

    if df.empty:
        print("데이터가 없습니다.")
    
    # 중복값 제거 (거래일 + 건물명 + 면적 + 층 + 가격)
    df_clean = df.drop_duplicates(subset=[
            'CTRT_DAY',
            'BLDG_NM', 
            'ARCH_AREA',
            'FLR',
            'THING_AMT'
        ], keep='first')
    
    # 캐시 저장
    save_cache(df, cache_file)

    # CSV 저장
    df.to_csv(
        '../data/raw/seoul_apt_raw.csv.csv',
        index=False,
        encoding='utf-8-sig'
    )

    return df