import glob
import logging
import os
import re
import time
import uuid
import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

import selenium_settings

logging.getLogger('selenium').setLevel(logging.ERROR)


class SeleniumBaseTest(unittest.TestCase):

    def setUp(self):
        super(SeleniumBaseTest, self).setUp()
        self.guid = uuid.uuid1().hex[:8]
        logging.info("Running selenium tests for guid %s" % self.guid)
        self.base_url = self.get_base_url()
        self.admin_url = self.base_url + 'admin/'
        if selenium_settings.ENVIRONMENT_TYPE == 'dev' and not selenium_settings.EMAIL_FILE_PATH:
            raise Exception("Must add setting EMAIL_FILE_PATH if running in a 'dev' environment")
        self.browser = self.open_browser()

    def tearDown(self):
        if len(self._outcome.errors) == 0:
            self.browser.close()

    def get_url(self, url_settings):
        if (not hasattr(selenium_settings, 'ENVIRONMENT_TYPE') or
                not selenium_settings.ENVIRONMENT_TYPE):
            raise Exception("Must add setting ENVIRONMENT_TYPE")
        return url_settings[selenium_settings.ENVIRONMENT_TYPE]

    def get_base_url(self):
        return self.get_url(selenium_settings.BASE_URL)

    def open_browser(self):
        browser_constructor = getattr(webdriver, selenium_settings.BROWSER)
        return browser_constructor()

    def admin_login(self):
        self.browser.get(self.admin_url + 'login/')
        self.wait_for_load('Log in')
        fields = {
            'id_username': selenium_settings.ADMIN_USERNAME,
            'id_password': selenium_settings.ADMIN_PASSWORD,
        }
        self.fill_fields(fields)
        self.submit_form()
        self.wait_for_load('Site administration')

    def admin_logout(self):
        self.browser.get(self.admin_url + 'logout/')

    def retrieve_email(self, email_address, subject):
        email_text = ''
        if selenium_settings.ENVIRONMENT_TYPE == 'dev':
            time.sleep(selenium_settings.SLEEP_INTERVAL)
            email_files = [file for file in
                           glob.glob(os.path.join(selenium_settings.EMAIL_FILE_PATH, '*.log'))]
            email_files.sort(
                key=lambda f: os.path.getmtime(os.path.join(selenium_settings.EMAIL_FILE_PATH, f)),
                reverse=True)
            for email_file in email_files:
                file_handle = open(os.path.join(selenium_settings.EMAIL_FILE_PATH, email_file))
                email_text = file_handle.read()
                file_handle.close()
                if email_text.find(subject) >= 0:
                    assert email_text.find(email_address)
                    break
        return email_text

    def extract_link_from_email(self, email_text):
        email_text = email_text.replace('=\n', '')
        email_text = email_text.replace('=\r\n', '')
        links = re.search('[\S]*\/accounts\/[\S]*', email_text)
        link = links.group(0)
        print(link)
        domain = self.base_url.split('/')[-2]
        self.assertTrue(link.find(domain) >= 0,
                        "Activation URL (%s) should be for domain under test (%s)."
                        "Check Site setup in the Django admin!"
                        % (link[:link.find('/', 8)], domain))
        if selenium_settings.ENVIRONMENT_TYPE == 'dev':
            # Registration links need to be https for production
            link = link.replace('https', 'http')
        return link

    def activate_user(self, email_address):
        print(email_address)
        email_text = self.retrieve_email(email_address, 'Please Confirm Your E-mail Address')
        print(email_text)
        confirmation_link = self.extract_link_from_email(email_text)
        self.browser.get(confirmation_link)
        self.wait_for_load('Please confirm that')
        self.submit_form()
        self.wait_for_load('Sign In')

    def search_for_entities(self, search_text):
        self.fill_fields({'searchbar': search_text})
        self.submit_form('changelist-search')
        self.wait_for_load(' result')

        # Get number of results
        form = self.browser.find_element_by_id('changelist-search')
        search_results = form.find_element_by_class_name('quiet')
        result_list = search_results.text.split(' ')
        return int(result_list[0])

    def delete_entities(self, url, url_loaded_text, search_text, action):
        self.browser.get(url)
        self.wait_for_load(url_loaded_text)

        num_results = self.search_for_entities(search_text)

        if num_results > 0:
            # Delete test users
            self.click_element_by_id('action-toggle')
            self.select_option('action', action)
            self.submit_form(id='changelist-form')
            self.wait_for_load('Are you sure?')
            self.submit_form()
            self.wait_for_load('Successfully deleted')

    def fill_element(self, element, value):
        try:
            element.clear()
        except WebDriverException:
            pass
        element.send_keys(value)

    def fill_select2_field(self, clickable_field_id, input_field_id, value):
        top_level_element = self.browser.find_element_by_id(clickable_field_id)

        clickable_element = webdriver.ActionChains(
            self.browser).click_and_hold(top_level_element).release(top_level_element)
        clickable_element.perform()

        input_element = self.browser.find_element_by_id(input_field_id)
        input_element.send_keys(value + Keys.ENTER)

    def fill_fields(self, fields):
        for field in fields:
            element = self.browser.find_element_by_id(field)
            self.fill_element(element, fields[field])

    def fill_fields_by_name(self, fields):
        for field in fields:
            element = self.browser.find_element_by_name(field)
            self.fill_element(element, fields[field])

    def click_element_by_id(self, id):
        element = self.browser.find_element_by_id(id)
        element.click()

    def click_element_by_name(self, name):
        element = self.browser.find_element_by_name(name)
        element.click()

    def click_element_by_css_selector(self, selector):
        element = self.browser.find_element_by_css_selector(selector)
        element.click()

    def click_element_by_link_text(self, text):
        element = self.browser.find_element_by_partial_link_text(text)
        element.click()

    def select_option(self, name, value):
        element = self.browser.find_element_by_name(name)
        found = False
        for option in element.find_elements_by_tag_name('option'):
            if option.text == value:
                found = True
                option.click()
                break
        if not found:
            raise Exception("Could not find option '%s' in select '%s'" % (value, name))

    def submit_form(self, id=None):
        if id:
            form = self.browser.find_element_by_id(id)
        else:
            form = self.browser.find_element_by_tag_name('form')
        form.submit()

    def page_contains(self, text):
        results = re.findall(text, self.browser.page_source)
        return len(results)

    def assert_page_contains(self, text, expected=1):
        found = self.page_contains(text)
        self.assertEqual(expected, found,
                         "Expected %s occurrences of '%s', found %s" % (expected, text, found))

    def assert_page_contains_by_css_selector(self, selector, value, expected=1):
        elements = self.browser.find_elements_by_css_selector(selector)
        found = 0
        for element in elements:
            if element.get_attribute('value') == value:
                found += 1
        self.assertEqual(expected, found,
                         "Expected %s occurrences of '%s', found %s" % (expected, value, found))

    def wait_for_load(self, text):
        found = 0
        time_slept = 0
        while not found:
            if time_slept > selenium_settings.MAX_SLEEP_TIME:
                raise Exception("Unable to find element '%s' on page" % text)
            time.sleep(selenium_settings.SLEEP_INTERVAL)
            time_slept += selenium_settings.SLEEP_INTERVAL
            found = self.page_contains(text)

    def assert_fields(self, fields):
        for field in fields:
            field_value = self.browser.find_element_by_id(field).get_attribute('value')
            self.assertEqual(fields[field], field_value)

    def assert_select2_choice(self, css_selector, value):
        elements = self.browser.find_elements_by_css_selector(css_selector)
        found = False
        for element in elements:
            if element.text == value:
                found = True
                break
        self.assertTrue(found, "Could not find element with value '%s'" % value)

    def assert_select2_single_choice(self, value):
        self.assert_select2_choice('span.select2-chosen', value)

    def assert_select2_multiple_choice(self, value):
        self.assert_select2_choice('li.select2-search-choice div', value)
