from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from logger import get_logger
import re ,logging




def select_brand(driver, target_text: str, timeout: int = 30) -> bool:
    logger = get_logger(
        service="vantagemarkets_ui",
        stage="select",
    )

    logger = logging.LoggerAdapter(
        logger.logger,
        {
            **logger.extra,
            "component": "regulator_dropdown",
        },
    )
    wait = WebDriverWait(driver, timeout)

    try:
        logger.info(
            "Selecting regulator brand",
            extra={"status": "running"},
        )
        dropdown = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "header-regulator"))
        )
        dropdown.click()

        li_div_list = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//ul[contains(@class,'dropdown-menu')]"
                    "/li[@role='presentation']/div[1]",
                )
            )
        )

        for div in li_div_list:
            span = div.find_element(By.TAG_NAME, "span")
            if span.text.strip() == target_text:
                wait.until(EC.element_to_be_clickable(span)).click()

                logger.info(
                    "Regulator selected",
                    extra={
                        "status": "success",
                        "target": target_text,
                    },
                )
                return True

        logger.warning(
            "Target regulator not found",
            extra={
                "status": "fail",
                "target": target_text,
            },
        )
        return False

    except TimeoutException:
        logger.exception(
            "Timeout during regulator selection",
            extra={"status": "fail"},
        )
        raise


def select_type(driver, keytype: str, timeout: int = 30) -> list[str]:
    logger = get_logger(
        service="vantagemarkets_ui",
        stage="extract",
    )

    logger = logging.LoggerAdapter(
        logger.logger,
        {
            **logger.extra,
            "component": "type_dropdown",
        },
    )
    wait = WebDriverWait(driver, timeout)

    try:
        logger.info(
            "Extracting task types",
            extra={"status": "running"},
        )
        # waiting for old element missing
        old_menu = driver.find_element(By.ID, "Menu1")
        wait.until(EC.staleness_of(old_menu))

        report_list = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#Menu1 li"))
        )

        for li in report_list:
            if keytype in li.text.strip():
                wait.until(EC.element_to_be_clickable(li)).click()

                logger.info(
                    "Task type clicked",
                    extra={
                        "status": "success",
                        "keytype": keytype,
                    },
                )
                break
        else:
            raise NoSuchElementException(f"Task type '{keytype}' not found")

        dropdown_items = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//ul[contains(@class,'dropdown-menu')]"
                    "/li[@role='presentation']",
                )
            )
        )

        results = []
        for div in dropdown_items:
            word = div.text.strip()
            if word:
                word = re.sub(r'[^A-Za-z /]', '', word)
                if word:  # 避免變成空字串
                    results.append(word)

        logger.info(
            "Task types extracted",
            extra={
                "status": "success",
                "keytype": keytype,
                "count": len(results),
            },
        )

        return results

    except TimeoutException:
        logger.exception(
            "Timeout extracting task types",
            extra={"status": "fail"},
        )
        raise


def select_report(driver, keyreport: str, timeout: int = 30) -> bool:
    logger = get_logger(
        service="vantagemarkets_ui",
        stage="select",
    )

    logger = logging.LoggerAdapter(
        logger.logger,
        {
            **logger.extra,
            "component": "report_dropdown",
        },
    )
    wait = WebDriverWait(driver, timeout)

    try:
        logger.info(
            "Selecting report",
            extra={"status": "running"},
        )

        items = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//ul[contains(@class,'dropdown-menu')]"
                    "/li[@role='presentation']",
                )
            )
        )

        for div in items:
            try:
                link = div.find_element(By.TAG_NAME, "a")
                if keyreport in link.text.strip():
                    wait.until(EC.element_to_be_clickable(link)).click()

                    logger.info(
                            "Report selected",
                            extra={
                                "status": "success",
                                "report": keyreport,
                            },
                        )
                    return True
            except NoSuchElementException:
                continue

        logger.warning(
            "Report not found",
            extra={
                "status": "fail",
                "report": keyreport,
            },
        )
        return False

    except TimeoutException:
        logger.exception(
            "Timeout selecting report",
            extra={"status": "fail"},
        )
        raise