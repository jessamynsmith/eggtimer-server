from django.contrib.auth import get_user_model
from django.test import TestCase
from mock import patch

from periods import email_sender


class TestEmailSender(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            password='bogus', email='jessamyn@example.com', first_name=u'Jessamyn')

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_send_text_only(self, mock_send):
        result = email_sender.send(self.user, 'Hi!', 'good day', None)

        self.assertEqual(True, result)
        mock_send.assert_called_once_with()

    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_send_with_html(self, mock_send):
        result = email_sender.send(self.user, 'Hi!', 'good day', '<p>good day</p>')

        self.assertEqual(True, result)
        mock_send.assert_called_once_with()
