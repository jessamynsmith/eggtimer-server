from django.test import TestCase

from periods import helpers


class TestEmailSender(TestCase):

    def test_http(self):
        result = helpers.get_full_domain()
        self.assertEqual('http://example.com', result)

    def test_https(self):
        with self.settings(SECURE_SSL_REDIRECT=True):
            result = helpers.get_full_domain()
            self.assertEqual('https://example.com', result)
