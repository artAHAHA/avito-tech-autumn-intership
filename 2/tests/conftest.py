import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


BASE_URL = os.getenv("BASE_URL", "http://195.19.209.79")


def make_driver(mobile=False):
    options = Options()

    if mobile:
        options.add_experimental_option(
            "mobileEmulation",
            {"deviceName": "iPhone 12 Pro"},
        )
    else:
        options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=options)


@pytest.fixture
def driver():
    driver = make_driver()
    driver.implicitly_wait(1)
    yield driver
    driver.quit()


@pytest.fixture
def mobile_driver():
    driver = make_driver(mobile=True)
    driver.implicitly_wait(1)
    yield driver
    driver.quit()
