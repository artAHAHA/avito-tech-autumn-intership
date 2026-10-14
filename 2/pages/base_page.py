import sys

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        self.clickable(locator).click()

    def fill(self, locator, value):
        element = self.driver.find_element(*locator)

        cmd_ctrl = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL

        element.send_keys(cmd_ctrl + "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(value)
    def text(self, locator):
        return self.visible(locator).text.strip()

    def attr(self, locator, name):
        return self.visible(locator).get_attribute(name)

    def all_visible(self, locator):
        return self.wait.until(
            lambda d: [e for e in d.find_elements(*locator) if e.is_displayed()]
        )

    def wait_url_contains(self, value):
        self.wait.until(lambda d: value in d.current_url)

    def wait_url_not_contains(self, value):
        self.wait.until(lambda d: value not in d.current_url)

    def current_url(self):
        return self.driver.current_url

    def go_back(self):
        self.driver.back()
