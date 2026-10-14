from selenium.webdriver.common.by import By

from pages.ads_page import AdsPage


BASE_URL = "http://195.19.209.79"


def test_mobile_01_theme_switching(mobile_driver):
    ads = AdsPage(mobile_driver)
    ads.open(BASE_URL)

    theme_button = (By.CSS_SELECTOR, "button.app-header__theme")
    icon = (By.CSS_SELECTOR, "button.app-header__theme [role='img']")

    before = mobile_driver.find_element(*icon).get_attribute("aria-label")

    assert before in ("moon", "sun"), (
        f"Неизвестное состояние темы: {before}"
    )

    mobile_driver.find_element(*theme_button).click()

    after = mobile_driver.find_element(*icon).get_attribute("aria-label")

    assert after in ("moon", "sun")
    assert after != before, (
        "После переключения тема не изменилась"
    )

    mobile_driver.find_element(*theme_button).click()

    restored = mobile_driver.find_element(*icon).get_attribute("aria-label")
    assert restored == before, (
        "После повторного переключения тема не вернулась в исходное состояние"
    )
