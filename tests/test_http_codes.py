from unittest import TestCase, mock

from httpbase.constants import HTTPResponseCodes


TEST_CODES = [
    100,
    101,
    102,
    103,
    122,
    200,
    201,
    202,
    203,
    204,
    205,
    206,
    207,
    208,
    226,
    300,
    301,
    302,
    303,
    304,
    305,
    306,
    307,
    308,
    400,
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    420,
    421,
    422,
    423,
    424,
    425,
    426,
    428,
    429,
    431,
    444,
    449,
    450,
    451,
    499,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    509,
    510,
    511,
]


class TestHTTPCodes(TestCase):
    def test_is_1xx_code(self):
        expected_true = {
            100,
            101,
            102,
            103,
            122,
        }
        for key in TEST_CODES:
            self.assertEqual(HTTPResponseCodes.is_1xx_code(key), key in expected_true)

    def test_is_2xx_code(self):
        expected_true = {
            200,
            201,
            202,
            203,
            204,
            205,
            206,
            207,
            208,
            226,
        }
        for code in TEST_CODES:
            self.assertEqual(HTTPResponseCodes.is_2xx_code(code), code in expected_true)

    def test_is_3xx_code(self):
        expected_true = {
            300,
            301,
            302,
            303,
            304,
            305,
            306,
            307,
            308,
        }
        for code in TEST_CODES:
            self.assertEqual(HTTPResponseCodes.is_3xx_code(code), code in expected_true)

    def test_is_4xx_code(self):
        expected_true = {
            400,
            401,
            402,
            403,
            404,
            405,
            406,
            407,
            408,
            409,
            410,
            411,
            412,
            413,
            414,
            415,
            416,
            417,
            418,
            420,
            421,
            422,
            423,
            424,
            425,
            426,
            428,
            429,
            431,
            444,
            449,
            450,
            451,
            499,
        }
        for code in TEST_CODES:
            self.assertEqual(HTTPResponseCodes.is_4xx_code(code), code in expected_true)

    def test_is_5xx_code(self):
        expected_true = {
            500,
            501,
            502,
            503,
            504,
            505,
            506,
            507,
            509,
            510,
            511,
        }
        for code in TEST_CODES:
            self.assertEqual(HTTPResponseCodes.is_5xx_code(code), code in expected_true)
