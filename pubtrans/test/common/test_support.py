import mock
import unittest

from pubtrans.common import support


class TestSupportNotify(unittest.TestCase):

    def setUp(self):
        super(TestSupportNotify, self).setUp()

        self.logger = mock.MagicMock()

        self.session_info = {
            'environment': 'unit_tests',
            'service': 'testService',
            'handler': 'Test',
            'requestId': 'testRequestId'
        }

        self.message = "A message"
        self.details = ['a', 'b', 'c']

        self.expected_extra = {'env': 'unit_tests',
                               'service': self.session_info['service'],
                               'handler': self.session_info['handler'],
                               'requestId': self.session_info['requestId'],
                               'details': ''}

        self.support = support.Support(self.logger, self.session_info)

    def test_notify_critical(self):

        self.support.notify_critical(self.message)

        self.expected_extra['details'] = self.message
        self.logger.critical.assert_called_with(self.message, extra=self.expected_extra)

        message = "A message"

        self.support.notify_critical(message, self.details)
        self.expected_extra['details'] = self.details
        self.logger.critical.assert_called_with(message, extra=self.expected_extra)

    def test_notify_error(self):

        self.support.notify_error(self.message)

        self.expected_extra['details'] = self.message
        self.logger.error.assert_called_with(self.message, extra=self.expected_extra)

        message = "A message"

        self.support.notify_error(message, self.details)
        self.expected_extra['details'] = self.details
        self.logger.error.assert_called_with(message, extra=self.expected_extra)

    def test_notify_warning(self):

        self.support.notify_warning(self.message)

        self.expected_extra['details'] = self.message
        self.logger.warning.assert_called_with(self.message, extra=self.expected_extra)

        message = "A message"

        self.support.notify_warning(message, self.details)
        self.expected_extra['details'] = self.details
        self.logger.warning.assert_called_with(message, extra=self.expected_extra)

    def test_notify_info(self):

        self.support.notify_info(self.message)

        self.expected_extra['details'] = self.message
        self.logger.info.assert_called_with(self.message, extra=self.expected_extra)

        message = "A message"

        self.support.notify_info(message, self.details)
        self.expected_extra['details'] = self.details
        self.logger.info.assert_called_with(message, extra=self.expected_extra)

    def test_notify_debug(self):

        self.support.notify_debug(self.message)

        self.expected_extra['details'] = self.message
        self.logger.debug.assert_called_with(self.message, extra=self.expected_extra)

        message = "A message"

        self.support.notify_debug(message, self.details)
        self.expected_extra['details'] = self.details
        self.logger.debug.assert_called_with(message, extra=self.expected_extra)
