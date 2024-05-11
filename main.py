from time import sleep
import requests
import pandas as pd
from bs4 import BeautifulSoup

# 創建一個Session對象來維持會話
session = requests.Session()

# 設置一個常見的用戶代理
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
session.headers.update(headers)


# 網址
base_url = 'https://web.pcc.gov.tw'
url = f'{base_url}/prkms/tender/common/basic/readTenderBasic?pageSize=50&firstSearch=true&searchType=basic&isBinding=N&isLogIn=N&level_1=on&orgName=&orgId=&tenderName=AI&tenderId=&tenderType=TENDER_DECLARATION&tenderWay=TENDER_WAY_ALL_DECLARATION&dateType=isDate&tenderStartDate=2023%2F12%2F01&tenderEndDate=2024%2F05%2F11&radProctrgCate=&policyAdvocacy='

# 使用requests庫發送GET請求
response = session.get(url)

# 檢查響應狀態碼是否為200（成功）
if response.status_code == 200:
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 打印整個HTML結構
    # print(soup.prettify())

    # 查找id為'printRange'的<div>標籤
    div_content = soup.find('div', id='printArea')
    view_links = soup.find_all('a', title="檢視")
    # for link in view_links:
    #     print(link)

    partial_urls = [link['href'] for link in view_links]

    for i, partial_url in enumerate(partial_urls):
        full_url = base_url + partial_url
        response = requests.get(full_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            div_content = soup.find('div', id='printRange')

            if div_content:
                tables = div_content.find_all('table')
                data_frames = []

                for table in tables:
                    rows = []
                    for tr in table.find_all('tr'):
                        cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                        rows.append(cols)

                    df = pd.DataFrame(rows)
                    data_frames.append(df)

                if data_frames:
                    combined_df = pd.concat(data_frames)
                    csv_filename = f'output_data_{i+1}.csv'
                    combined_df.to_csv(csv_filename, index=False, header=False)
                    print(f"Data has been written to '{csv_filename}'")
                else:
                    print("No data found in the tables.")
            else:
                print("No div with id 'printRange' was found.")
        else:
            print('Failed to retrieve the webpage. Status code:', response.status_code)
        
        sleep(30)
else:
    print('Failed to retrieve the webpage. Status code:', response.status_code)
