from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class AdPage(BasePage):
    TITLE = (By.CSS_SELECTOR, ".ad-item-page__title")
    PRICE = (By.CSS_SELECTOR, ".ad-item-page__price")
    DATE = (By.CSS_SELECTOR, ".ad-item-page__date")
    DESCRIPTION = (By.CSS_SELECTOR, ".ad-item-page__description")
    EDIT_BUTTON = (
        By.XPATH,
        "//button[.//span[normalize-space()='Редактировать']]",
    )

    def title(self):
        return self.text(self.TITLE)

    def price(self):
        return self.text(self.PRICE)

    def publication_date_text(self):
        return self.text(self.DATE)

    def description(self):
        return self.text(self.DESCRIPTION)

    def click_edit(self):
        self.click(self.EDIT_BUTTON)
        self.wait_url_contains("/edit")
