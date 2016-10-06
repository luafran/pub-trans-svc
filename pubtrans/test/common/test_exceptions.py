import unittest

from pubtrans.common import exceptions


class TestExceptions(unittest.TestCase):
    def test_GeneralInfoException(self):
        try:
            raise exceptions.GeneralInfoException("Testing GeneralInfoException")
        except exceptions.GeneralInfoException:
            pass

    def test_BadRequest(self):
        try:
            raise exceptions.BadRequest("Testing BadRequest")
        except exceptions.BadRequest:
            pass

    def test_MissingArgumentValue(self):
        try:
            raise exceptions.MissingArgumentValue("Testing MissingArgumentValue")
        except exceptions.MissingArgumentValue:
            pass

    def test_InvalidArgumentValue(self):
        try:
            raise exceptions.InvalidArgumentValue("Testing InvalidArgumentValue")
        except exceptions.InvalidArgumentValue:
            pass

    def test_Forbidden(self):
        try:
            raise exceptions.Forbidden("Testing Forbidden")
        except exceptions.Forbidden:
            pass

    def test_Unauthorized(self):
        try:
            raise exceptions.Unauthorized("Testing Unauthorized")
        except exceptions.Unauthorized:
            pass

    def test_UnauthorizedRead(self):
        try:
            raise exceptions.UnauthorizedRead("Testing UnauthorizedRead")
        except exceptions.UnauthorizedRead:
            pass

    def test_UnauthorizedWrite(self):
        try:
            raise exceptions.UnauthorizedWrite("Testing UnauthorizedWrite")
        except exceptions.UnauthorizedWrite:
            pass

    def test_UnauthorizedExecute(self):
        try:
            raise exceptions.UnauthorizedExecute("Testing UnauthorizedExecute")
        except exceptions.UnauthorizedExecute:
            pass

    def test_NotFound(self):
        try:
            raise exceptions.NotFound("Testing NotFound")
        except exceptions.NotFound:
            pass

    def test_MethodNotAllowed(self):
        try:
            raise exceptions.MethodNotAllowed("Testing MethodNotAllowed")
        except exceptions.MethodNotAllowed:
            pass

    def test_CouldNotConnectToDatabase(self):
        try:
            raise exceptions.CouldNotConnectToDatabase("Testing CouldNotConnectToDatabase")
        except exceptions.CouldNotConnectToDatabase:
            pass

    def test_DatabaseOperationError(self):
        try:
            raise exceptions.DatabaseOperationError("Testing DatabaseOperationError")
        except exceptions.DatabaseOperationError:
            pass

    def test_ExternalProviderUnavailablePermanently(self):
        try:
            raise exceptions.ExternalProviderUnavailablePermanently(
                "Testing ExternalProviderUnavailablePermanently")
        except exceptions.ExternalProviderUnavailablePermanently:
            pass

    def test_ExternalProviderUnavailableTemporarily(self):
        try:
            raise exceptions.ExternalProviderUnavailableTemporarily(
                "Testing ExternalProviderUnavailableTemporarily")
        except exceptions.ExternalProviderUnavailableTemporarily:
            pass

    def test_ExternalProviderBadResponse(self):
        try:
            raise exceptions.ExternalProviderBadResponse("Testing ExternalProviderBadResponse")
        except exceptions.ExternalProviderBadResponse:
            pass
