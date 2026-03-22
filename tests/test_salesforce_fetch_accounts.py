import json
import unittest
from unittest import mock

import salesforce_fetch_accounts


class FetchAccountsTests(unittest.TestCase):
    def test_build_query_limits_accounts_to_two(self) -> None:
        self.assertEqual(
            salesforce_fetch_accounts.build_query(),
            "SELECT Id, Name FROM Account LIMIT 2",
        )

    @mock.patch("urllib.request.urlopen")
    def test_fetch_accounts_queries_salesforce_for_two_records(self, mock_urlopen) -> None:
        response = mock.MagicMock()
        response.read.return_value = json.dumps(
            {
                "totalSize": 2,
                "records": [
                    {"Id": "001000000000001AAA", "Name": "Acme"},
                    {"Id": "001000000000002AAA", "Name": "Globex"},
                ],
            }
        ).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = response

        payload = salesforce_fetch_accounts.fetch_accounts(
            "https://example.my.salesforce.com",
            "token-123",
        )

        request = mock_urlopen.call_args.args[0]
        self.assertIn(
            "SELECT+Id%2C+Name+FROM+Account+LIMIT+2",
            request.full_url,
        )
        self.assertEqual(request.headers["Authorization"], "Bearer token-123")
        self.assertEqual(payload["totalSize"], 2)


if __name__ == "__main__":
    unittest.main()
