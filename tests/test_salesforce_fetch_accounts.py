import json
import unittest
from unittest import mock

import salesforce_fetch_accounts


class BuildQueryTests(unittest.TestCase):
    def test_build_query_filters_accounts_by_s_prefix_and_limit(self) -> None:
        self.assertEqual(
            salesforce_fetch_accounts.build_query(),
            "SELECT Id, Name FROM Account WHERE Name LIKE 's%' ORDER BY Name LIMIT 4",
        )

    def test_build_query_escapes_single_quotes_in_prefix(self) -> None:
        self.assertEqual(
            salesforce_fetch_accounts.build_query(name_prefix="s'"),
            "SELECT Id, Name FROM Account WHERE Name LIKE 's\\'%'"
            " ORDER BY Name LIMIT 4",
        )


class FetchAccountsTests(unittest.TestCase):
    @mock.patch("urllib.request.urlopen")
    def test_fetch_accounts_queries_salesforce_for_matching_records(
        self,
        mock_urlopen,
    ) -> None:
        response = mock.MagicMock()
        response.read.return_value = json.dumps(
            {
                "totalSize": 4,
                "records": [
                    {"Id": "001000000000001AAA", "Name": "Sales"},
                    {"Id": "001000000000002AAA", "Name": "Sandbox"},
                    {"Id": "001000000000003AAA", "Name": "Sigma"},
                    {"Id": "001000000000004AAA", "Name": "Summit"},
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
            "SELECT+Id%2C+Name+FROM+Account+WHERE+Name+LIKE+%27s%25%27+ORDER+BY+Name+LIMIT+4",
            request.full_url,
        )
        self.assertEqual(request.headers["Authorization"], "Bearer token-123")
        self.assertEqual(payload["totalSize"], 4)


if __name__ == "__main__":
    unittest.main()
