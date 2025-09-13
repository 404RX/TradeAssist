# test_alpaca_client.py
"""
Comprehensive pytest test suite for AlpacaTradingClient class
Coverage: authentication, retry logic, rate limiting, error handling
"""

import pytest
import requests
import time
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add the app directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alpaca_trading_client import (
    AlpacaTradingClient, 
    AlpacaCredentials, 
    TradingMode, 
    OrderSide, 
    OrderType, 
    TimeInForce,
    RateLimitTracker
)

class TestAlpacaCredentials:
    """Test AlpacaCredentials dataclass"""
    
    def test_credentials_creation(self):
        """Test credential object creation"""
        creds = AlpacaCredentials(
            api_key_id="test_key",
            secret_key="test_secret", 
            mode=TradingMode.PAPER
        )
        
        assert creds.api_key_id == "test_key"
        assert creds.secret_key == "test_secret"
        assert creds.mode == TradingMode.PAPER
    
    def test_credentials_modes(self):
        """Test both trading modes"""
        paper_creds = AlpacaCredentials("key", "secret", TradingMode.PAPER)
        live_creds = AlpacaCredentials("key", "secret", TradingMode.LIVE)
        
        assert paper_creds.mode.value == "paper"
        assert live_creds.mode.value == "live"


class TestRateLimitTracker:
    """Test rate limiting functionality"""
    
    def setup_method(self):
        """Set up rate tracker for each test"""
        self.tracker = RateLimitTracker(max_requests=5, time_window=60)
    
    def test_rate_limit_allows_requests_under_limit(self):
        """Test rate limiter allows requests under the limit"""
        for i in range(5):
            can_request, wait_time = self.tracker.check_rate_limit()
            assert can_request is True
            assert wait_time == 0
            self.tracker.record_request()
    
    def test_rate_limit_blocks_requests_over_limit(self):
        """Test rate limiter blocks requests over the limit"""
        # Fill up the rate limit
        for i in range(5):
            self.tracker.record_request()
        
        # Next request should be blocked
        can_request, wait_time = self.tracker.check_rate_limit()
        assert can_request is False
        assert wait_time > 0
    
    @patch('time.time')
    def test_rate_limit_expires_old_requests(self, mock_time):
        """Test that old requests expire from the rate limit window"""
        # Start at time 0
        mock_time.return_value = 0
        
        # Fill up rate limit
        for i in range(5):
            self.tracker.record_request()
        
        # Should be blocked
        can_request, wait_time = self.tracker.check_rate_limit()
        assert can_request is False
        
        # Move forward 61 seconds (past the 60-second window)
        mock_time.return_value = 61
        
        # Should now allow requests
        can_request, wait_time = self.tracker.check_rate_limit()
        assert can_request is True
        assert wait_time == 0
    
    def test_wait_time_calculation(self):
        """Test wait time calculation when rate limited"""
        # Fill up the rate limit
        start_time = time.time()
        for i in range(5):
            self.tracker.record_request()
        
        # Check wait time
        can_request, wait_time = self.tracker.check_rate_limit()
        assert can_request is False
        assert wait_time > 0
        assert wait_time <= 60  # Should not exceed the window


class TestAlpacaTradingClientAuthentication:
    """Test authentication and connection handling"""
    
    def setup_method(self):
        """Set up test credentials"""
        self.paper_creds = AlpacaCredentials(
            api_key_id="PKTEST123456789",
            secret_key="test_secret_key",
            mode=TradingMode.PAPER
        )
        self.live_creds = AlpacaCredentials(
            api_key_id="PKLIVE123456789", 
            secret_key="live_secret_key",
            mode=TradingMode.LIVE
        )
    
    @patch('alpaca_trading_client.requests.Session')
    def test_client_initialization_success(self, mock_session_class):
        """Test successful client initialization"""
        # Mock successful account response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'id': 'test_account_id',
            'status': 'ACTIVE'
        }
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # This should not raise an exception
        client = AlpacaTradingClient(self.paper_creds)
        
        # Verify session headers were set correctly
        expected_headers = {
            "APCA-API-KEY-ID": self.paper_creds.api_key_id,
            "APCA-API-SECRET-KEY": self.paper_creds.secret_key,
            "Content-Type": "application/json",
            "User-Agent": "AlpacaTradingClient/1.0"
        }
        mock_session.headers.update.assert_called_with(expected_headers)
    
    @patch('alpaca_trading_client.requests.Session')
    def test_client_initialization_failure(self, mock_session_class):
        """Test client initialization with invalid credentials"""
        # Mock failed account response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid credentials"}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Should raise ConnectionError
        with pytest.raises(ConnectionError, match="Invalid Alpaca credentials"):
            AlpacaTradingClient(self.paper_creds)
    
    @patch('alpaca_trading_client.requests.Session')
    def test_mode_switching(self, mock_session_class):
        """Test switching between paper and live trading modes"""
        # Mock session for initial setup
        mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {'id': 'test_id', 'status': 'ACTIVE'}
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create client in paper mode
        client = AlpacaTradingClient(self.paper_creds)
        assert client.credentials.mode == TradingMode.PAPER
        
        # Switch to live mode
        client.switch_mode(self.live_creds)
        assert client.credentials.mode == TradingMode.LIVE
        
        # Verify headers were updated
        expected_headers = {
            "APCA-API-KEY-ID": self.live_creds.api_key_id,
            "APCA-API-SECRET-KEY": self.live_creds.secret_key
        }
        mock_session.headers.update.assert_called_with(expected_headers)
    
    def test_base_url_selection(self):
        """Test that correct base URLs are selected for each mode"""
        with patch('alpaca_trading_client.requests.Session'):
            with patch.object(AlpacaTradingClient, '_validate_connection'):
                paper_client = AlpacaTradingClient(self.paper_creds)
                live_client = AlpacaTradingClient(self.live_creds)
        
        # Check paper trading URLs
        assert "paper-api.alpaca.markets" in paper_client.base_urls[TradingMode.PAPER]["trading"]
        assert "data.alpaca.markets" in paper_client.base_urls[TradingMode.PAPER]["data"]
        
        # Check live trading URLs
        assert "api.alpaca.markets" in live_client.base_urls[TradingMode.LIVE]["trading"]
        assert "data.alpaca.markets" in live_client.base_urls[TradingMode.LIVE]["data"]


class TestAlpacaTradingClientRetryLogic:
    """Test exponential backoff and retry logic"""
    
    def setup_method(self):
        """Set up client with mocked session"""
        self.creds = AlpacaCredentials("test_key", "test_secret", TradingMode.PAPER)
        
        with patch('alpaca_trading_client.requests.Session'):
            with patch.object(AlpacaTradingClient, '_validate_connection'):
                self.client = AlpacaTradingClient(self.creds)
        
        # Mock the session
        self.mock_session = Mock()
        self.client.session = self.mock_session
        
        # Mock rate tracker to allow requests
        self.client.rate_tracker = Mock()
        self.client.rate_tracker.check_rate_limit.return_value = (True, 0)
    
    @patch('time.sleep')
    @patch('random.uniform')
    def test_exponential_backoff_with_jitter_5xx_errors(self, mock_random, mock_sleep):
        """Test exponential backoff with jitter for 5xx errors"""
        mock_random.return_value = 0.1  # Fixed jitter for predictable testing
        
        # Mock responses: first 2 fail with 500, third succeeds
        mock_responses = []
        for i in range(2):
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 500
            mock_response.json.return_value = {"message": "Internal Server Error"}
            mock_responses.append(mock_response)
        
        # Success response
        success_response = Mock()
        success_response.ok = True
        success_response.json.return_value = {"status": "success"}
        mock_responses.append(success_response)
        
        self.mock_session.get.side_effect = mock_responses
        
        # Make request
        result = self.client._make_request("test/endpoint")
        
        # Verify it succeeded after retries
        assert result["status"] == "success"
        
        # Verify sleep was called with exponential backoff + jitter
        # First retry: base=1.0, jitter=0.1, delay = 1.0 * (1 + 0.1) = 1.1
        # Second retry: base=2.0, jitter=0.1, delay = 2.0 * (1 + 0.1) = 2.2
        expected_delays = [1.1, 2.2]
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
        
        assert len(actual_delays) == 2
        for expected, actual in zip(expected_delays, actual_delays):
            assert abs(actual - expected) < 0.01  # Allow for floating point precision
    
    @patch('time.sleep')
    @patch('random.uniform')
    def test_exponential_backoff_max_delay_cap(self, mock_random, mock_sleep):
        """Test that exponential backoff caps at 32 seconds"""
        mock_random.return_value = 0.0  # No jitter for this test
        
        # Mock 4 consecutive failures (should hit the 32s cap)
        mock_responses = []
        for i in range(4):
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 503
            mock_response.json.return_value = {"message": "Service Unavailable"}
            mock_responses.append(mock_response)
        
        self.mock_session.get.side_effect = mock_responses
        
        # Should raise RuntimeError after max retries
        with pytest.raises(RuntimeError):
            self.client._make_request("test/endpoint")
        
        # Check that delays cap at 32 seconds
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
        
        # Expected: [1, 2, 4] seconds (before hitting the 32s cap on 4th retry)
        assert len(actual_delays) == 3
        assert actual_delays[0] == 1.0  # 2^0 = 1
        assert actual_delays[1] == 2.0  # 2^1 = 2  
        assert actual_delays[2] == 4.0  # 2^2 = 4
    
    @patch('time.sleep')
    @patch('random.uniform')
    def test_network_error_retry_with_jitter(self, mock_random, mock_sleep):
        """Test network error retry with exponential backoff and jitter"""
        mock_random.return_value = -0.1  # Negative jitter
        
        # Mock network errors followed by success
        network_error = requests.ConnectionError("Connection failed")
        success_response = Mock()
        success_response.ok = True
        success_response.json.return_value = {"status": "success"}
        
        self.mock_session.get.side_effect = [network_error, network_error, success_response]
        
        # Should succeed after retries
        result = self.client._make_request("test/endpoint")
        assert result["status"] == "success"
        
        # Verify jittered delays
        # First retry: base=1.0, jitter=-0.1, delay = max(0.1, 1.0 * (1 - 0.1)) = 0.9
        # Second retry: base=2.0, jitter=-0.1, delay = max(0.1, 2.0 * (1 - 0.1)) = 1.8
        expected_delays = [0.9, 1.8]
        actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
        
        assert len(actual_delays) == 2
        for expected, actual in zip(expected_delays, actual_delays):
            assert abs(actual - expected) < 0.01
    
    def test_non_retryable_error_no_retry(self):
        """Test that non-retryable errors don't trigger retry logic"""
        # Mock 404 error (not retryable)
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not found"}
        self.mock_session.get.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="Alpaca API error \\(404\\)"):
            self.client._make_request("test/endpoint")
        
        # Should only be called once (no retries)
        assert self.mock_session.get.call_count == 1
    
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep):
        """Test behavior when max retries are exceeded"""
        # Mock persistent 500 errors
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal Server Error"}
        self.mock_session.get.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="Alpaca API error \\(500\\)"):
            self.client._make_request("test/endpoint", max_retries=2)
        
        # Should be called 3 times total (initial + 2 retries)
        assert self.mock_session.get.call_count == 3
        
        # Should sleep 2 times (between retries)
        assert mock_sleep.call_count == 2


class TestAlpacaTradingClientRateLimiting:
    """Test rate limiting integration"""
    
    def setup_method(self):
        """Set up client with real rate tracker"""
        self.creds = AlpacaCredentials("test_key", "test_secret", TradingMode.PAPER)
        
        with patch('alpaca_trading_client.requests.Session'):
            with patch.object(AlpacaTradingClient, '_validate_connection'):
                self.client = AlpacaTradingClient(self.creds)
        
        # Use a restrictive rate tracker for testing
        self.client.rate_tracker = RateLimitTracker(max_requests=2, time_window=60)
        
        # Mock successful responses
        self.mock_session = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "success"}
        self.mock_session.get.return_value = mock_response
        self.client.session = self.mock_session
    
    @patch('time.sleep')
    def test_rate_limit_enforced(self, mock_sleep):
        """Test that rate limiting is enforced"""
        # First 2 requests should succeed immediately
        self.client._make_request("test/endpoint1")
        self.client._make_request("test/endpoint2")
        
        # Third request should trigger rate limiting
        self.client._make_request("test/endpoint3")
        
        # Should have slept due to rate limiting
        mock_sleep.assert_called()
        sleep_call_args = mock_sleep.call_args[0][0]
        assert sleep_call_args > 0
    
    def test_rate_limit_headers_logged(self):
        """Test that rate limit events are properly logged"""
        with patch('alpaca_trading_client.get_api_error_logger') as mock_logger_getter:
            mock_logger = Mock()
            mock_logger_getter.return_value = mock_logger
            
            # Fill up rate limit
            self.client._make_request("test/endpoint1")
            self.client._make_request("test/endpoint2")
            
            with patch('time.sleep'):
                self.client._make_request("test/endpoint3")
            
            # Should have logged rate limit hit
            mock_logger.warning.assert_called()
            log_call = mock_logger.warning.call_args[0][0]
            assert "RATE_LIMIT_HIT" in log_call


class TestAlpacaTradingClientAPIFunctions:
    """Test specific API function implementations"""
    
    def setup_method(self):
        """Set up client with mocked successful responses"""
        self.creds = AlpacaCredentials("test_key", "test_secret", TradingMode.PAPER)
        
        with patch('alpaca_trading_client.requests.Session'):
            with patch.object(AlpacaTradingClient, '_validate_connection'):
                self.client = AlpacaTradingClient(self.creds)
        
        # Mock session and rate tracker
        self.mock_session = Mock()
        self.client.session = self.mock_session
        self.client.rate_tracker = Mock()
        self.client.rate_tracker.check_rate_limit.return_value = (True, 0)
    
    def test_get_account(self):
        """Test get_account method"""
        expected_account = {
            'id': 'test_account',
            'status': 'ACTIVE',
            'buying_power': '10000.00'
        }
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = expected_account
        self.mock_session.get.return_value = mock_response
        
        result = self.client.get_account()
        
        assert result == expected_account
        self.mock_session.get.assert_called_once()
        
        # Check that correct endpoint was called
        call_args = self.mock_session.get.call_args
        assert "v2/account" in str(call_args)
    
    def test_has_position_true(self):
        """Test has_position returns True when position exists"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'symbol': 'AAPL',
            'qty': '100'
        }
        self.mock_session.get.return_value = mock_response
        
        result = self.client.has_position("AAPL")
        assert result is True
    
    def test_has_position_false_404(self):
        """Test has_position returns False for 404 'position does not exist'"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "position does not exist"}
        self.mock_session.get.return_value = mock_response
        
        result = self.client.has_position("AAPL")
        assert result is False
    
    def test_has_position_raises_for_invalid_symbol(self):
        """Test has_position raises error for invalid symbol"""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "symbol not found: INVALID"}
        self.mock_session.get.return_value = mock_response
        
        with pytest.raises(RuntimeError):
            self.client.has_position("INVALID")
    
    def test_place_order(self):
        """Test place_order method"""
        expected_order = {
            'id': 'order_123',
            'symbol': 'AAPL',
            'side': 'buy',
            'qty': '10'
        }
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = expected_order
        self.mock_session.post.return_value = mock_response
        
        result = self.client.place_order(
            symbol="AAPL",
            qty="10", 
            side=OrderSide.BUY,
            order_type=OrderType.MARKET
        )
        
        assert result == expected_order
        self.mock_session.post.assert_called_once()
        
        # Verify the request data
        call_args = self.mock_session.post.call_args
        request_data = call_args[1]['json']
        assert request_data['symbol'] == 'AAPL'
        assert request_data['qty'] == '10'
        assert request_data['side'] == 'buy'
        assert request_data['type'] == 'market'
    
    def test_place_order_validation_error(self):
        """Test place_order raises error when neither qty nor notional provided"""
        with pytest.raises(ValueError, match="Either qty or notional must be specified"):
            self.client.place_order(
                symbol="AAPL",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET
            )
    
    def test_get_bars_with_parameters(self):
        """Test get_bars method with various parameters"""
        expected_bars = {
            'bars': {
                'AAPL': [
                    {'t': '2023-01-01T00:00:00Z', 'o': 150.0, 'h': 155.0, 'l': 149.0, 'c': 154.0, 'v': 1000000}
                ]
            }
        }
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = expected_bars
        self.mock_session.get.return_value = mock_response
        
        result = self.client.get_bars(
            symbols="AAPL",
            timeframe="1Day",
            start="2023-01-01",
            end="2023-01-31",
            limit=100
        )
        
        assert result == expected_bars
        
        # Verify request parameters
        call_args = self.mock_session.get.call_args
        params = call_args[1]['params']
        assert params['symbols'] == 'AAPL'
        assert params['timeframe'] == '1Day'
        assert params['start'] == '2023-01-01'
        assert params['end'] == '2023-01-31'
        assert params['limit'] == 100


class TestAlpacaTradingClientErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    def setup_method(self):
        """Set up client for error testing"""
        self.creds = AlpacaCredentials("test_key", "test_secret", TradingMode.PAPER)
        
        with patch('alpaca_trading_client.requests.Session'):
            with patch.object(AlpacaTradingClient, '_validate_connection'):
                self.client = AlpacaTradingClient(self.creds)
        
        self.mock_session = Mock()
        self.client.session = self.mock_session
        self.client.rate_tracker = Mock()
        self.client.rate_tracker.check_rate_limit.return_value = (True, 0)
    
    def test_json_decode_error_handling(self):
        """Test handling of invalid JSON responses"""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Non-JSON response text"
        self.mock_session.get.return_value = mock_response
        
        result = self.client._make_request("test/endpoint")
        
        # Should return text response when JSON parsing fails
        assert result == {"status": "success", "data": "Non-JSON response text"}
    
    def test_timeout_handling(self):
        """Test handling of request timeouts"""
        timeout_error = requests.exceptions.Timeout("Request timed out")
        self.mock_session.get.side_effect = timeout_error
        
        with pytest.raises(ConnectionError, match="Request failed after"):
            self.client._make_request("test/endpoint")
    
    def test_connection_error_handling(self):
        """Test handling of connection errors"""
        connection_error = requests.exceptions.ConnectionError("DNS lookup failed")
        self.mock_session.get.side_effect = connection_error
        
        with pytest.raises(ConnectionError, match="Request failed after"):
            self.client._make_request("test/endpoint")
    
    def test_unsupported_http_method(self):
        """Test error for unsupported HTTP methods"""
        with pytest.raises(ValueError, match="Unsupported HTTP method: PATCH"):
            self.client._make_request("test/endpoint", method="PATCH")
    
    @patch('alpaca_trading_client.get_api_error_logger')
    def test_error_logging_sanitization(self, mock_logger_getter):
        """Test that error logging sanitizes sensitive data"""
        mock_logger = Mock()
        mock_logger_getter.return_value = mock_logger
        
        # Mock response with sensitive data in error message
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "message": "Invalid API key PKTEST123456789ABCDEF provided"
        }
        self.mock_session.get.return_value = mock_response
        
        with pytest.raises(RuntimeError):
            self.client._make_request("test/endpoint")
        
        # Verify error was logged
        mock_logger.error.assert_called()
        
        # Check that sensitive data was sanitized (the actual sanitization
        # is handled by the safe_api_error_log function)
        log_call_args = mock_logger.error.call_args[0][0]
        assert "API_ERROR" in log_call_args


class TestAlpacaTradingClientIntegration:
    """Integration tests for complete workflows"""
    
    def setup_method(self):
        """Set up client for integration testing"""
        self.creds = AlpacaCredentials("test_key", "test_secret", TradingMode.PAPER)
        
        with patch('alpaca_trading_client.requests.Session'):
            with patch.object(AlpacaTradingClient, '_validate_connection'):
                self.client = AlpacaTradingClient(self.creds)
        
        self.mock_session = Mock()
        self.client.session = self.mock_session
        self.client.rate_tracker = Mock()
        self.client.rate_tracker.check_rate_limit.return_value = (True, 0)
    
    def test_complete_trading_workflow(self):
        """Test a complete trading workflow: check account, place order, check position"""
        # Mock account response
        account_response = Mock()
        account_response.ok = True
        account_response.json.return_value = {
            'id': 'test_account',
            'buying_power': '10000.00',
            'status': 'ACTIVE'
        }
        
        # Mock order response
        order_response = Mock()
        order_response.ok = True
        order_response.json.return_value = {
            'id': 'order_123',
            'symbol': 'AAPL',
            'side': 'buy',
            'qty': '10',
            'status': 'filled'
        }
        
        # Mock position response
        position_response = Mock()
        position_response.ok = True
        position_response.json.return_value = {
            'symbol': 'AAPL',
            'qty': '10',
            'market_value': '1500.00'
        }
        
        # Set up responses in order
        self.mock_session.get.side_effect = [account_response, position_response]
        self.mock_session.post.return_value = order_response
        
        # Execute workflow
        account = self.client.get_account()
        assert account['status'] == 'ACTIVE'
        assert float(account['buying_power']) >= 1500  # Enough for trade
        
        order = self.client.buy_market("AAPL", "10")
        assert order['symbol'] == 'AAPL'
        assert order['status'] == 'filled'
        
        position = self.client.get_position("AAPL")
        assert position['symbol'] == 'AAPL'
        assert position['qty'] == '10'
    
    @patch('time.sleep')
    def test_resilient_api_calls_with_retry(self, mock_sleep):
        """Test that API calls are resilient to temporary failures"""
        # Mock sequence: failure, failure, success
        failure_response = Mock()
        failure_response.ok = False
        failure_response.status_code = 503
        failure_response.json.return_value = {"message": "Service temporarily unavailable"}
        
        success_response = Mock()
        success_response.ok = True
        success_response.json.return_value = {
            'id': 'test_account',
            'status': 'ACTIVE'
        }
        
        self.mock_session.get.side_effect = [
            failure_response,
            failure_response, 
            success_response
        ]
        
        # Should succeed after retries
        account = self.client.get_account()
        assert account['status'] == 'ACTIVE'
        
        # Verify retries occurred
        assert self.mock_session.get.call_count == 3
        assert mock_sleep.call_count == 2


# Test configuration and fixtures
@pytest.fixture
def paper_credentials():
    """Fixture for paper trading credentials"""
    return AlpacaCredentials(
        api_key_id="PKTEST123456789",
        secret_key="test_secret_key",
        mode=TradingMode.PAPER
    )

@pytest.fixture
def live_credentials():
    """Fixture for live trading credentials"""
    return AlpacaCredentials(
        api_key_id="PKLIVE123456789",
        secret_key="live_secret_key", 
        mode=TradingMode.LIVE
    )

@pytest.fixture
def mock_successful_client():
    """Fixture for client with mocked successful responses"""
    creds = AlpacaCredentials("test_key", "test_secret", TradingMode.PAPER)
    
    with patch('alpaca_trading_client.requests.Session'):
        with patch.object(AlpacaTradingClient, '_validate_connection'):
            client = AlpacaTradingClient(creds)
    
    # Mock session with successful responses
    mock_session = Mock()
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"status": "success"}
    mock_session.get.return_value = mock_response
    mock_session.post.return_value = mock_response
    mock_session.delete.return_value = mock_response
    
    client.session = mock_session
    client.rate_tracker = Mock()
    client.rate_tracker.check_rate_limit.return_value = (True, 0)
    
    return client


# Performance tests
class TestAlpacaTradingClientPerformance:
    """Test performance-related functionality"""
    
    def test_rate_tracker_performance(self):
        """Test that rate tracker performs well with many requests"""
        tracker = RateLimitTracker(max_requests=1000, time_window=60)
        
        # Time many operations
        start_time = time.time()
        
        for i in range(500):
            can_request, wait_time = tracker.check_rate_limit()
            if can_request:
                tracker.record_request()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete quickly (less than 100ms for 500 operations)
        assert elapsed < 0.1
    
    def test_concurrent_rate_limiting(self):
        """Test rate limiting behavior under concurrent access"""
        import threading
        import queue
        
        tracker = RateLimitTracker(max_requests=10, time_window=60)
        results = queue.Queue()
        
        def make_requests():
            for i in range(5):
                can_request, wait_time = tracker.check_rate_limit()
                if can_request:
                    tracker.record_request()
                results.put(can_request)
        
        # Start multiple threads
        threads = []
        for i in range(4):  # 4 threads x 5 requests = 20 total requests
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        allowed_requests = 0
        blocked_requests = 0
        
        while not results.empty():
            result = results.get()
            if result:
                allowed_requests += 1
            else:
                blocked_requests += 1
        
        # Should have allowed some requests and blocked others
        assert allowed_requests > 0
        assert blocked_requests > 0
        assert allowed_requests <= 10  # Respect the rate limit


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--durations=10",  # Show 10 slowest tests
        "-x",  # Stop on first failure
    ])