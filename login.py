from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
import undetected_chromedriver as uc
from logger import get_logger
import pyotp



def get_login()-> uc.Chrome | None:
    logger = get_logger(service="vantagemarkets_login", stage="init")

    driver = None

    try:
        logger.info(
            "Initializing undetected chrome",
            extra={"stage": "init", "status": "running"},
        )

        # Setup TOTP
        setup_key = "BEVP3Q7AFQY6JE4VLN5QQECZNUY5SK6Q"
        totp = pyotp.TOTP(setup_key)


        # Initialize WebDriver
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")       # headless 模式
        options.add_argument("--no-sandbox")         # Docker 必備
        options.add_argument("--disable-dev-shm-usage") # 避免 /dev/shm 空間不足
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222") # 強制啟動 remote debug
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        login_url = "https://admin.vantagemarkets.com/login"
        driver.get(login_url)
        logger.info(
            "Login page opened",
            extra={"stage": "page_load", "status": "success"},
        )


        # Locate username and password => click
        username = "Account OP"  # CRM login username
        password = "Asdf@1021Dec"  # CRM password (Ensure it's correct)

        username_input = wait.until(
                EC.presence_of_element_located((By.ID, "exampleInputEmail1"))
            )
        password_input = wait.until(
            EC.presence_of_element_located((By.ID, "password_login"))
        )

        username_input.send_keys(username)
        password_input.send_keys(password)

        login_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "btnLogin"))
            )
        login_btn.click()
        logger.info(
            "Credential submitted",
            extra={"stage": "login", "status": "success"},
        )


        # InsertInto 2FA code to zone => login
        wait.until(EC.presence_of_element_located((By.NAME, "googleAuthTotp"))).send_keys(totp.now())
        wait.until(EC.element_to_be_clickable((By.ID, "loginBtn-googleAuth"))).click()
        logger.info(
            "TOTP verification success",
            extra={"stage": "totp", "status": "success"},
        )

        return driver
       
    except TimeoutException:
        logger.exception(
            "Timeout while waiting for page element",
            extra={"stage": "timeout", "status": "fail"},
        )

    except NoSuchElementException:
        logger.exception(
            "DOM element not found",
            extra={"stage": "dom", "status": "fail"},
        )

    except WebDriverException:
        logger.exception(
            "WebDriver error occurred",
            extra={"stage": "webdriver", "status": "fail"},
        )

    except Exception:
        logger.exception(
            "Unexpected error during login",
            extra={"stage": "unknown", "status": "fail"},
        )

    finally:
        logger.info(
            "Login process finished",
            extra={"stage": "end", "status": "fail"},
        )

    return None
