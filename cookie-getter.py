#! /bin/env python3

from selenium import webdriver
import selenium.common
import argparse
import sys
import pickle
import time

class wait_for_page_load(object):
    """
    As seen here:
    http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html
    """
    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def wait_for(self, condition_function):
        start_time = time.time()
        while time.time() < start_time + 10:
            if condition_function():
                return True
            else:
                time.sleep(0.1)
        raise Exception(
            'Timeout waiting for {}'.format(condition_function.__name__)
        )

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        self.wait_for(self.page_has_loaded)

parser = argparse.ArgumentParser()
parser.add_argument("dropbox_url")
parser.add_argument("cookies_file")
parser.add_argument("-p" , "--password")
args = parser.parse_args()

driver = webdriver.Firefox()
driver.get(args.dropbox_url)

try:
    password_input = driver.find_element_by_name("password")
except selenium.common.exceptions.NoSuchElementException:
    password_input = None

if password_input:
    if not args.password:
        print("Password required, but none provided", file=sys.stderr)
        driver.quit()
        sys.exit(1)

    password_input.send_keys(args.password)
    try:
        with wait_for_page_load(driver):
            password_input.submit()
    except:
        print("Wrong password or network error", file=sys.stderr)
        driver.quit()
        sys.exit(2)

pickle.dump(driver.get_cookies(), open(args.cookies_file, "wb"))

driver.quit()
