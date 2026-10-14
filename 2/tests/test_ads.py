import re
from datetime import datetime

from pages.ads_page import AdsPage
from pages.ad_page import AdPage


MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def parse_publication_date(text):
    match = re.search(
        r"Опубликовано:\s*(\d{1,2})\s+([А-Яа-яЁё]+)\s+"
        r"(\d{4})\s*г\.\s*в\s*(\d{1,2}):(\d{2})",
        text,
    )
    assert match, f"Не удалось распознать дату публикации: {text}"

    day, month, year, hour, minute = match.groups()
    return datetime(
        int(year),
        MONTHS[month.lower()],
        int(day),
        int(hour),
        int(minute),
    )


def collect_visible_dates(driver, ads_page):
    count = len(ads_page.cards())
    result = []

    for index in range(count):
        ads_page.open_card(index)
        result.append(
            parse_publication_date(
                AdPage(driver).publication_date_text()
            )
        )
        driver.back()
        ads_page.wait_url_contains("/ads")
        ads_page.visible(ads_page.CARDS)

    return result


def test_ads_01_search_by_title(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    titles = ads.card_titles()
    assert titles, "На странице нет объявлений"

    query = titles[0]
    ads.search(query)

    result_titles = ads.card_titles()
    assert result_titles, "Поиск не вернул объявлений"
    assert all(
        query.casefold() in title.casefold()
        for title in result_titles
    ), f"В результатах поиска есть объявление без '{query}': {result_titles}"


def test_ads_02_sort_new_first(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    before_count = len(ads.cards())
    assert before_count >= 2, "Для проверки сортировки нужно минимум 2 объявления"

    ads.select_sort("new")
    actual_dates = collect_visible_dates(driver, ads)

    assert actual_dates == sorted(actual_dates, reverse=True), (
        f"Объявления не отсортированы по новизне: {actual_dates}"
    )


def test_ads_03_sort_old_first(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    assert len(ads.cards()) >= 2, "Для проверки сортировки нужно минимум 2 объявления"

    ads.select_sort("old")
    actual_dates = collect_visible_dates(driver, ads)

    assert actual_dates == sorted(actual_dates), (
        f"Объявления не отсортированы от старых к новым: {actual_dates}"
    )


def test_ads_04_sort_title_asc(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    assert len(ads.cards()) >= 2
    ads.select_sort("title_asc")

    titles = ads.card_titles()
    assert titles == sorted(titles, key=str.casefold), (
        f"Названия не отсортированы А→Я: {titles}"
    )


def test_ads_05_sort_title_desc(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    assert len(ads.cards()) >= 2
    ads.select_sort("title_desc")

    titles = ads.card_titles()
    assert titles == sorted(titles, key=str.casefold, reverse=True), (
        f"Названия не отсортированы Я→А: {titles}"
    )


def test_ads_06_category_filter(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    categories = ads.category_names_from_cards()
    assert categories, "Не удалось определить категории объявлений"

    category = categories[0]
    ads.select_category(category)

    result = ads.card_categories()
    assert result, "Фильтр категории не вернул объявления"
    assert all(item == category for item in result), (
        f"После фильтра '{category}' найдены другие категории: {result}"
    )


def test_ads_07_all_categories(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    initial_count = len(ads.cards())
    assert initial_count > 0

    ads.select_all_categories()

    assert len(ads.cards()) == initial_count, (
        "После выбора всех категорий изменилось количество объявлений"
    )


def test_ads_08_revision_filter(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    ads.toggle_revision()

    assert ads.revision_enabled(), (
        "Переключатель 'Только требующие доработки' не включился"
    )

    cards_count = len(ads.cards())

    assert cards_count > 0, (
        "После включения фильтра 'Только требующие доработки' "
        "не найдено объявлений"
    )

    assert ads.revision_marks_count() == cards_count, (
        "После включения фильтра 'Только требующие доработки' "
        "не все объявления имеют отметку 'Требует доработок'"
    )

def test_ads_09_reset_filters(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    initial_count = len(ads.cards())

    category = ads.category_names_from_cards()[0]
    ads.select_category(category)
    ads.toggle_revision()

    ads.reset_filters()

    assert not ads.revision_enabled(), "Переключатель не сбросился"

    checkbox_states = [
        element.is_selected()
        for element in driver.find_elements(*ads.CATEGORY_INPUTS)
    ]
    assert not any(checkbox_states), "Категории не сбросились"

    assert len(ads.cards()) == initial_count, (
        "После сброса фильтров количество объявлений не восстановилось"
    )


def test_ads_10_pagination(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    pages = driver.find_elements(*ads.PAGINATION_ITEMS)
    assert len(pages) >= 2, "На стенде нет второй страницы"

    first_page_titles = ads.card_titles()
    old_first_card = ads.cards()[0]

    ads.open_page(2)

    assert driver.find_element(
        *(
            "css selector",
            ".ads-page__pagination li.ant-pagination-item-active"
        )
    ).get_attribute("title") == "2"

    second_page_titles = ads.card_titles()
    assert second_page_titles != first_page_titles or len(second_page_titles) == 0, (
        "После перехода на вторую страницу содержимое не изменилось"
    )


def test_ads_11_click_card_opens_ad(driver):
    ads = AdsPage(driver)
    ads.open("http://195.19.209.79")

    assert ads.cards(), "Нет объявлений для проверки перехода"

    ads.open_card(0)

    ad = AdPage(driver)
    assert "/ads/" in driver.current_url
    assert ad.title(), "На странице объявления отсутствует заголовок"
    assert ad.price(), "На странице объявления отсутствует цена"
