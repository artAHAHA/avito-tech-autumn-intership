from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class AdsPage(BasePage):
    URL = "/ads"

    SEARCH = (By.CSS_SELECTOR, 'input[placeholder="Найти объявление..."]')
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".ant-input-search-btn")

    CARDS = (By.CSS_SELECTOR, ".ads-page__grid > .ant-card")
    CARD_TITLE = (
        By.CSS_SELECTOR,
        ".ant-card-body span.ant-typography:not(.ant-typography-secondary)",
    )
    CARD_CATEGORY = (
        By.CSS_SELECTOR,
        ".ant-card-body .ant-tag:not(._ad-card__revision_1um3u_26)",
    )
    REVISION_TEXT = (
        By.XPATH,
        ".//*[contains(normalize-space(), 'Требует доработок')]",
    )

    SORT = (By.CSS_SELECTOR, ".ads-page__sort-select .ant-select-content")

    CATEGORY_LABELS = (
        By.CSS_SELECTOR,
        ".ads-page__sidebar .ant-checkbox-label",
    )
    CATEGORY_INPUTS = (
        By.CSS_SELECTOR,
        ".ads-page__sidebar .ant-checkbox-input",
    )

    REVISION_SWITCH = (
        By.CSS_SELECTOR,
        ".ads-page__sidebar button[role='switch']",
    )
    RESET_BUTTON = (
        By.XPATH,
        "//button[.//span[normalize-space()='Сбросить фильтры']]",
    )

    PAGINATION_ITEMS = (
        By.CSS_SELECTOR,
        ".ads-page__pagination li.ant-pagination-item",
    )

    def open(self, base_url):
        self.driver.get(base_url.rstrip("/") + "/ads")
        self.visible((By.CSS_SELECTOR, ".ads-page"))

    def cards(self):
        return self.all_visible(self.CARDS)

    def card_titles(self):
        result = []
        for card in self.cards():
            result.append(
                card.find_element(*self.CARD_TITLE).text.strip()
            )
        return result

    def card_categories(self):
        result = []
        for card in self.cards():
            result.append(
                card.find_element(
                    By.CSS_SELECTOR,
                    ".ant-card-body .ant-tag"
                ).text.strip()
            )
        return result

    def has_revision_mark(self, card):
        return bool(card.find_elements(
            By.XPATH,
            ".//*[contains(normalize-space(), 'Требует доработок')]"
        ))

    def revision_marks_count(self):
        return len(
            self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class, 'ant-card')]"
                "//span[normalize-space()='Требует доработок']"
            )
        )

    def click_search(self):
        self.click(self.SEARCH_BUTTON)

    def search(self, title):
        old_cards = self.driver.find_elements(*self.CARDS)
        old_count = len(old_cards)

        # В компонентах Ant Design часто надежнее нажимать Enter прямо в поле
        element = self.driver.find_element(*self.SEARCH)
        element.clear()
        element.send_keys(title)
        element.send_keys(Keys.ENTER)

        # Клик по кнопке оставляем как резервный вариант
        self.click_search()

        if old_count > 1:
            try:
                # Ждем исчезновения ПОСЛЕДНЕЙ карточки (она точно удалится из DOM)
                self.wait.until(EC.staleness_of(old_cards[-1]))
            except Exception:
                pass

    def clear_search(self):
        old_cards = self.driver.find_elements(*self.CARDS)
        old_count = len(old_cards)

        element = self.driver.find_element(*self.SEARCH)

        # Выделяем всё и удаляем, чтобы наверняка очистить поле
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(Keys.ENTER)

        self.click_search()

        try:
            # При очистке ждем, пока количество элементов не изменится (увеличится)
            self.wait.until(lambda d: len(d.find_elements(*self.CARDS)) != old_count)
        except Exception:
            pass
    def select_category(self, category):
        label = self.driver.find_element(
            By.XPATH,
            f"//label[contains(@class,'ant-checkbox-wrapper') and "
            f".//span[contains(@class,'ant-checkbox-label') and "
            f"normalize-space()='{category}']]"
        )
        label.click()

        self.wait.until(
            lambda d: all(
                c == category for c in self.card_categories()
            )
        )

    def category_names_from_cards(self):
        return list(dict.fromkeys(self.card_categories()))

    def select_all_categories(self):
        labels = self.all_visible(self.CATEGORY_LABELS)
        for label in labels:
            label.click()

    def revision_enabled(self):
        return self.attr(self.REVISION_SWITCH, "aria-checked") == "true"

    def toggle_revision(self):
        self.click(self.REVISION_SWITCH)

    def reset_filters(self):
        button = self.visible(self.RESET_BUTTON)
        if button.is_enabled():
            button.click()
            self.wait.until(
                lambda d: self.attr(self.REVISION_SWITCH, "aria-checked") == "false"
            )

    def selected_sort_text(self):
        return self.text(self.SORT)

    def select_sort(self, kind):
        self.click(self.SORT)

        options = self.wait.until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR,
                 ".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
                 ".ant-select-item-option")
            )
        )

        candidates = {
            "new": [
                "По новизне (сначала новые)",
            ],
            "old": [
                "По новизне (сначала старые)",
            ],
            "title_asc": [
                "По названию (А→Я)",
                "По названию (А → Я)",
                "По названию (А-Я)",
                "По названию (А–Я)",
            ],
            "title_desc": [
                "По названию (Я→А)",
                "По названию (Я → А)",
                "По названию (Я-А)",
                "По названию (Я–А)",
            ],
        }

        expected = candidates[kind]

        for option in options:
            text = option.text.strip()
            if text in expected:
                option.click()
                return

        # Запасной вариант для небольших отличий в тире/стрелке.
        for option in options:
            text = option.text.strip().lower()
            if kind == "new" and "новизне" in text and "новые" in text:
                option.click()
                return
            if kind == "old" and "новизне" in text and "старые" in text:
                option.click()
                return
            if kind == "title_asc" and "назван" in text and (
                "а→я" in text or "а → я" in text or "а-я" in text or "а–я" in text
            ):
                option.click()
                return
            if kind == "title_desc" and "назван" in text and (
                "я→а" in text or "я → а" in text or "я-а" in text or "я–а" in text
            ):
                option.click()
                return

        raise AssertionError(
            f"Не найден пункт сортировки {kind}. "
            f"Доступные варианты: {[o.text.strip() for o in options]}"
        )

    def open_card(self, index=0):
        card = self.cards()[index]
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", card
        )
        card.click()
        self.wait_url_contains("/ads/")
        self.wait_url_not_contains("/ads/edit")

    def open_page(self, number):
        locator = (
            By.CSS_SELECTOR,
            f".ads-page__pagination li.ant-pagination-item-{number}"
        )
        old_cards = self.driver.find_elements(*self.CARDS)
        self.click(locator)
        if old_cards:
            self.wait.until(EC.staleness_of(old_cards[0]))

        self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".ads-page__grid")
            )
        )
