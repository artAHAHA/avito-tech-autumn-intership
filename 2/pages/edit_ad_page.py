from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class EditAdPage(BasePage):
    CATEGORY = (By.ID, "category")
    TITLE = (By.ID, "title")
    PRICE = (By.ID, "price")
    TYPE = (By.ID, "type")
    BRAND = (By.ID, "brand")
    MODEL = (By.ID, "model")
    CONDITION = (By.ID, "condition")
    COLOR = (By.ID, "color")
    DESCRIPTION = (By.ID, "description")

    SAVE = (
        By.XPATH,
        "//div[contains(@class,'edit-form__actions')]"
        "//button[.//span[normalize-space()='Сохранить']]",
    )
    CANCEL = (
        By.XPATH,
        "//div[contains(@class,'edit-form__actions')]"
        "//button[.//span[normalize-space()='Отменить']]",
    )

    AI_DESCRIPTION = (
        By.XPATH,
        "//aside[contains(@class,'_ai-panel')]"
        "//button[.//span[contains(translate(normalize-space(), "
        "'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ', "
        "'абвдеёжзийклмнопрстуфхцчшщъыьэюя'), 'описание')]]",
    )
    AI_PRICE = (
        By.XPATH,
        "//aside[contains(@class,'_ai-panel')]"
        "//button[.//span[normalize-space()='Узнать цену']]",
    )

    MODAL = (By.CSS_SELECTOR, ".ant-modal")
    MODAL_APPLY = (
        By.XPATH,
        "//div[contains(@class,'ant-modal')]"
        "//button[.//span[normalize-space()='Применить']]",
    )
    MODAL_CLOSE = (
        By.XPATH,
        "//div[contains(@class,'ant-modal')]"
        "//button[.//span[normalize-space()='Закрыть']]",
    )

    AI_POPUP = (
        By.CSS_SELECTOR,
        "div.ant-popover-container[role='tooltip']"
    )

    AI_POPUP_TEXT = (
        By.XPATH,
        "//div[contains(@class, 'ant-popover-container') and @role='tooltip']"
        "//p[contains(@class, '_ai-popup__text--new')]"
    )

    AI_APPLY = (
        By.XPATH,
        "//div[contains(@class, 'ant-popover-container')]"
        "//button[.//span[normalize-space()='Применить']]"
    )

    AI_CLOSE = (
        By.XPATH,
        "//div[contains(@class, 'ant-popover-container')]"
        "//button[.//span[normalize-space()='Закрыть']]"
    )

    CONFIRM_MODAL = (By.CSS_SELECTOR, ".ant-modal-confirm")

    def title(self):
        return self.attr(self.TITLE, "value")

    def price(self):
        return self.attr(self.PRICE, "value")

    def description(self):
        return self.attr(self.DESCRIPTION, "value")

    def set_title(self, value):
        self.fill(self.TITLE, value)

    def set_price(self, value):
        self.fill(self.PRICE, str(value))

    def set_description(self, value):
        self.fill(self.DESCRIPTION, value)

    def save(self):
        self.click(self.SAVE)
        self.wait_url_not_contains("/edit")

    def cancel(self):
        self.click(self.CANCEL)

    def confirm_cancel(self):
        modal = self.visible(self.CONFIRM_MODAL)
        text = modal.text
        buttons = modal.find_elements(By.CSS_SELECTOR, ".ant-modal-confirm-btns button")
        if not buttons:
            raise AssertionError("В окне подтверждения нет кнопок")
        buttons[-1].click()
        self.wait_url_not_contains("/edit")
        return text

    def validation_message_visible(self):
        selectors = [
            (
                By.CSS_SELECTOR,
                ".ant-form-item-explain-error"
            ),
            (
                By.XPATH,
                "//*[contains(normalize-space(), "
                "'Пожалуйста, проверьте правильность заполнения полей')]"
            ),
        ]

        for locator in selectors:
            elements = self.driver.find_elements(*locator)
            if any(e.is_displayed() for e in elements):
                return True
        return False

    def open_ai_description(self):
        self.click(self.AI_DESCRIPTION)
        self.visible(self.AI_POPUP)

    def open_ai_price(self):
        self.click(self.AI_PRICE)
        self.visible(self.AI_POPUP)

    def ai_response_text(self):
        elements = self.driver.find_elements(
            *self.AI_POPUP_TEXT
        )

        for element in elements:
            if element.is_displayed():
                return element.text.strip()

        raise AssertionError(
            "Открытый AI-попап найден, но текст ответа AI не найден"
        )

    def apply_ai(self):
        self.click(self.AI_APPLY)
        self.wait.until(
            EC.invisibility_of_element_located(self.AI_POPUP)
        )

    def close_ai(self):
        self.click(self.AI_CLOSE)
        self.wait.until(
            EC.invisibility_of_element_located(self.AI_POPUP)
        )

    def modal_text(self):
        return self.text(self.MODAL)

    def apply_modal(self):
        self.click(self.MODAL_APPLY)
        self.wait.until(
            EC.invisibility_of_element_located(self.MODAL)
        )

    def close_modal(self):
        self.click(self.MODAL_CLOSE)
        self.wait.until(
            EC.invisibility_of_element_located(self.MODAL)
        )
