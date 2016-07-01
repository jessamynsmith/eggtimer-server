# -*- coding: iso-8859-15 -*-

import datetime
import selenium_settings
from base_test import SeleniumBaseTest


class SignupTest(SeleniumBaseTest):
    PASSWORD = 's3l3n1uM'
    PASSWORD2 = 'sel3n1uM2'
    PASSWORD3 = 'sel3n1uM3'

    def setUp(self):
        super(SignupTest, self).setUp()

        self.admin_login()
        self.delete_entities(self.admin_url + 'periods/user/',
                             'Select user to change',
                             selenium_settings.EMAIL_USERNAME.split('@')[0],
                             'Delete selected users')
        self.admin_logout()

        self.USERNAME = selenium_settings.EMAIL_USERNAME.replace('@', '+%s@' % self.guid)
        self.NEW_USERNAME = self.USERNAME.replace('@', '1@')
        self.signup_url = self.base_url + 'accounts/signup/'
        self.login_url = self.base_url + 'accounts/login/'
        self.user_information = {
            'id_email': self.USERNAME,
        }
        self.signup_fields = self.user_information.copy()
        self.signup_fields.update({
            'id_password1': self.PASSWORD,
            'id_password2': self.PASSWORD,
        })
        self.organization_fields = {
            'id_organization_name': u'Selenium Organization \xe5',
            'id_job_title': u'Administrator \xe5',
        }

    def login(self, username, password):
        fields = {
            'id_login': username,
            'id_password': password,
        }
        self.browser.get(self.login_url)
        self.wait_for_load('Sign In')
        self.fill_fields(fields)
        self.submit_form()

    def logout(self):
        # For some reason clicking the menu fails
        self.browser.get(self.base_url + 'accounts/logout')
        self.wait_for_load('egg timer')

    def click_menu_item(self, menu_item_text):
        # The menu items are capitalized via CSS, so use .upper()
        self.click_element_by_link_text(menu_item_text.upper())

    def test_signup(self):
        self.browser.get(self.login_url)
        self.wait_for_load('Sign In')
        self.click_element_by_link_text('sign up')
        self.wait_for_load('Sign Up')

        # Should fail if not filled in
        self.submit_form()
        self.assert_page_contains("This field is required.", 3)

        # Fill in fields and re-submit
        self.fill_fields(self.signup_fields)

        self.submit_form()
        title = datetime.datetime.now().strftime("%B %Y")
        self.wait_for_load(title)

        self.logout()
        self.wait_for_load('Sign In')

        # Try to sign up again with same info; should fail
        self.browser.get(self.signup_url)
        self.wait_for_load('Sign Up')
        self.fill_fields(self.signup_fields)
        self.submit_form()
        self.wait_for_load('Sign Up')
        self.assert_page_contains("A user is already registered with this e-mail address.")

        # Activate account
        self.activate_user(self.USERNAME)

        # Log in successfully
        self.login(self.USERNAME, self.PASSWORD)
        self.wait_for_load(title)

        # TODO Fix and enable tests
        # # Change password
        # self.click_menu_item(self.user_information['id_first_name'])
        # self.wait_for_load('aria-expanded="true"')
        # self.click_menu_item('Change Password')
        # self.wait_for_load('Change Password')
        # self.submit_form()
        # self.wait_for_load('This field is required.')
        # self.assert_page_contains("This field is required.", 3)
        # self.fill_fields({'id_oldpassword': 'bogusvalue'})
        # self.submit_form()
        # self.wait_for_load('Please type your current password.')
        # fields = {
        #     'id_oldpassword': self.PASSWORD,
        #     'id_password1': self.PASSWORD2,
        #     'id_password2': self.PASSWORD2,
        # }
        # self.fill_fields(fields)
        # self.submit_form()
        # self.wait_for_load('Change Password')
        # self.assert_page_contains("This field is required.", 0)
        #
        # # Test logout
        # self.logout()
        #
        # # Test reset password via email
        # self.click_menu_item('Sign In')
        # self.wait_for_load('Sign In')
        # self.click_element_by_link_text('Forgot Password?')
        # self.wait_for_load('Password Reset')
        # self.fill_fields_by_name({'email': 'bogus@example.com'})
        # self.submit_form()
        # self.wait_for_load("The e-mail address is not assigned to any user account")
        # self.fill_fields_by_name({'email': self.USERNAME})
        # self.submit_form()
        # self.wait_for_load('We have sent you an e-mail.')
        # # Retrieve and use email
        # email_text = self.retrieve_email(self.USERNAME, 'Password Reset E-mail')
        # reset_link = self.extract_link_from_email(email_text)
        # self.browser.get(reset_link)
        # self.wait_for_load('Change Password')
        # fields = {
        #     'id_password1': self.PASSWORD3,
        #     'id_password2': self.PASSWORD3,
        # }
        # self.fill_fields(fields)
        # self.submit_form()
        # self.assert_page_contains('Your password is now changed.')
        #
        # # Try to log in with old info
        # self.login(self.USERNAME, self.PASSWORD)
        # self.wait_for_load('The e-mail address and/or password you specified are not correct.')
        #
        # # Log in with updated info
        # self.login(self.USERNAME, self.PASSWORD3)
        # self.wait_for_load('Postings')
        #
        # # Update user information - no change
        # self.click_menu_item('Profile')
        # self.wait_for_load('aria-expanded="true"')
        # self.click_menu_item('Contact Info')
        # self.wait_for_load('Update Contact Information')
        # self.assert_fields(self.user_information)
        # self.submit_form()
        # self.wait_for_load('Postings')
        #
        # # Update user information
        # self.click_menu_item('Profile')
        # self.wait_for_load('aria-expanded="true"')
        # self.click_menu_item('Contact Info')
        # self.wait_for_load('Update Contact Information')
        # fields = {
        #     'id_email': selenium_settings.EMAIL_USERNAME,
        # }
        # self.fill_fields(fields)
        # self.submit_form()
        # self.wait_for_load(title)
        #
        # # Ensure updated information was saved
        # self.click_menu_item('Profile')
        # self.wait_for_load('aria-expanded="true"')
        # self.click_menu_item('Contact Info')
        # self.wait_for_load('Update Contact Information')
        # self.assert_fields(fields)
