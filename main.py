from category import select_brand ,select_type ,select_report
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from zoneinfo import ZoneInfo
from datetime import datetime
from logger import get_logger
from login import get_login
import requests  ,os


# Common Function
def extract_token(driver) -> tuple[dict,str]:
    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    token_resp = requests.get(
        'https://admin.vantagemarkets.com/davinci/token',
        cookies=cookies,
        headers={
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0'
        }
    )
    token = token_resp.text.strip()
    return cookies ,token

def build_api_session(token:str, cookies: dict) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        'authorization': f'Bearer {token}',
        'content-type': 'application/json;charset=UTF-8',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0'
    })
    session.cookies.update(cookies)

    return session

def build_davinci_report(brand,y,m,d):
    return {
        'regulator': brand.lower(),
        'sort': {},
        'filter': {},
        'from': f'{y}-{m}-{d}',
        'to': f'{y}-{m}-{d}',
        'levelId': '',
        'showAll': True,
        'payments': [
            {
                'dataType': 2,
                'paymentStatus': [],
            },
            {
                'dataType': 1,
                'paymentStatus': [],
            },
        ],
    }

def build_output_path(base_dir, system, branch, brand, dt):
    y, m, d = dt.strftime('%Y'), dt.strftime('%m'), dt.strftime('%d')
    output_dir = os.path.join(base_dir, y, m, d, system, branch)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{branch}_{brand}_{dt.strftime('%Y%m%d%H%M%S')}.csv"
    return os.path.join(output_dir, filename)



logger = get_logger(                        # 1. Logger 
    service="vantagemarkets_report",
    stage="download")                       
driver = get_login()                        # 2. Login

brands = ['ASIC','VFSC','VFSC2','FCA']      # 3. Click Revalent ReportName
missions = ['Users','Client','Account','Reports','Task','System Setting']
brand, mission = brands[0] , missions[3]
select_brand(driver,brand)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "Menu1"))
)
types = select_type(driver,mission)
select_report(driver,types[-1])

cookies ,token = extract_token(driver)      # 4. Get token
session = build_api_session(token, cookies) # 5. Session Connection


### 6. Main 
for brand in brands:
    today = datetime.now(ZoneInfo('Asia/Taipei'))
    y ,m ,d = today.strftime('%Y-%m-%d').split('-')
    logger.info(
        "Start processing brand report",
        extra={
            "brand": brand,
            "stage": "init",
            "status": "running",
        },
    )

    json_data = build_davinci_report(brand ,y ,m ,d)
    

    #  Main-1：Post Requester & Get Filename
    logger.info(
            "Requesting report file",
            extra={
                "brand": brand,
                "stage": "main1",
                "status": "running",
            },
        )
    headers = {'authorization': f'Bearer {token}',
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json;charset=UTF-8',
                'user-agent': 'Mozilla/5.0',
    }
    response = session.post('https://report.vantagemarkets.com/api/deposit/download',headers=headers,cookies=cookies,json=json_data)
    filename = response.json()['data']['file']

    #  Main-2：Get Relative Filefolder & Download CSV
    logger.info(
            "Downloading report file",
            extra={
                "brand": brand,
                "stage": "main2",
                "status": "running",
                "filename": filename,
            },
        )
    # DATA_DIR = r'C:\Users\peter.chang\Desktop\test1' # Localhost Anaylsis
    DATA_DIR = os.getenv("DATA_DIR", "/data") # Docker deployment method
    output_path = build_output_path(
        base_dir=DATA_DIR,
        system='CRM',
        branch='DavinciReport',
        brand=brand ,
        dt=datetime.now(ZoneInfo('Asia/Taipei')),
    )
    download_url = f'https://report.vantagemarkets.com/api/download/{filename}'
    response = session.get(download_url,headers=headers,cookies=cookies,stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk) 

        logger.info(
            "Report file downloaded",
            extra={
                "brand": brand,
                "stage": "main2",
                "status": "success",
                "output_path": output_path,
            },
        )
    else:
        pass

driver.quit()