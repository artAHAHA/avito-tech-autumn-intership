from pages.ads_page import AdsPage
from pages.ad_page import AdPage
from pages.edit_ad_page import EditAdPage


BASE_URL = "http://195.19.209.79"


def open_first_edit(driver):
    ads = AdsPage(driver)
    ads.open(BASE_URL)
    ads.open_card(0)

    ad = AdPage(driver)
    detail_url = driver.current_url
    original_title = ad.title()
    original_price = ad.price()
    original_description = ad.description()

    ad.click_edit()

    return EditAdPage(driver), detail_url, original_title, original_price, original_description


def restore_ad(driver, detail_url, title, price, description):
    try:
        driver.get(detail_url + "/edit")
        edit = EditAdPage(driver)

        edit.set_title(title)
        edit.set_price(price.replace("₽", "").strip())
        edit.set_description(description)
        edit.save()
    except Exception:
        # Восстановление не должно маскировать исходную ошибку теста.
        pass


def test_edit_01_required_field_validation(driver):
    edit, detail_url, original_title, original_price, original_description = open_first_edit(driver)

    try:
        edit.set_price("")
        edit.click(edit.SAVE)

        assert edit.validation_message_visible(), (
            "При сохранении объявления с пустым обязательным полем "
            "не появилось сообщение о проверке полей"
        )
    finally:
        restore_ad(
            driver,
            detail_url,
            original_title,
            original_price,
            original_description,
        )


def test_edit_02_save_changes(driver):
    edit, detail_url, original_title, original_price, original_description = open_first_edit(driver)

    new_title = (original_title + " autotest")[:100]

    try:
        edit.set_title(new_title)
        edit.save()

        ad = AdPage(driver)
        assert ad.title() == new_title, (
            "После сохранения новое название не отображается на странице объявления"
        )
    finally:
        restore_ad(
            driver,
            detail_url,
            original_title,
            original_price,
            original_description,
        )


def test_edit_03_cancel_editing(driver):
    edit, detail_url, original_title, original_price, original_description = open_first_edit(driver)

    edit.set_title((original_title + " cancel-test")[:100])
    edit.cancel()

    confirmation_text = edit.confirm_cancel()

    assert "Отменить редактирование" in confirmation_text
    assert "несохраненные изменения" in confirmation_text

    ad = AdPage(driver)
    assert ad.title() == original_title, (
        "После отмены редактирования изменения сохранились"
    )


def test_edit_04_ai_description(driver):
    edit, detail_url, original_title, original_price, original_description = open_first_edit(driver)

    try:
        edit.open_ai_description()

        ai_text = edit.ai_response_text()

        assert ai_text, (
            "В окне AI отсутствует ответ на запрос "
            "'Придумать описание'"
        )

        edit.apply_ai()

        actual_description = edit.description()

        assert actual_description == ai_text, (
            "После нажатия 'Применить' описание объявления "
            "не совпадает с ответом AI.\n"
            f"Ответ AI: {ai_text!r}\n"
            f"Описание объявления: {actual_description!r}"
        )

    finally:
        restore_ad(
            driver,
            detail_url,
            original_title,
            original_price,
            original_description,
        )

def test_edit_05_ai_price(driver):
    edit, detail_url, original_title, original_price, original_description = open_first_edit(driver)

    try:
        edit.open_ai_price()

        ai_text = edit.ai_response_text()

        assert ai_text.strip(), (
            "После нажатия 'Узнать цену' "
            "ответ AI отсутствует или пустой"
        )

        edit.apply_ai()

        assert edit.price().strip(), (
            "После применения AI цена объявления осталась пустой"
        )

    finally:
        restore_ad(
            driver,
            detail_url,
            original_title,
            original_price,
            original_description,
        )
