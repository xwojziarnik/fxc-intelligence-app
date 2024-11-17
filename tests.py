from unittest.mock import MagicMock, patch

from utils import callback_after_receiving_a_message


class TestCallback:
    @patch("utils.connect_to_postgres")
    @patch("utils.save_transaction_to_postgres")
    @patch("utils.update_provider_balance")
    def test_callback_with_mocked_postgres(
        self,
        mock_update_provider_balance,
        mock_save_transaction_to_postgres,
        mock_connect_to_postgres,
    ):
        # with
        mock_connection = MagicMock()
        mock_connect_to_postgres.return_value = mock_connection
        mock_save_transaction_to_postgres.return_value = None
        mock_update_provider_balance.return_value = None
        mock_body = b'{"id": 1, "value": 456}'

        # when
        callback_after_receiving_a_message(None, None, None, mock_body)

        # then
        mock_save_transaction_to_postgres.assert_called_once_with(
            account_id=1, transaction_amount=456
        )
        mock_update_provider_balance.assert_called_once_with(providers_id=1, amount=456)
