# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\tests\test_data_validation.py
import unittest
import pandas as pd
import logging
import sys
import os
from datetime import datetime

# Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.trade_manager import TradeManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\test.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TestDataValidation(unittest.TestCase):
    def setUp(self):
        self.trade_manager = TradeManager()
        
    def test_valid_ohlcv_data(self):
        data = {
            "timestamp": [datetime(2025, 7, 1, 10, 0), datetime(2025, 7, 1, 10, 1)],
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "volume": [1000, 1200]
        }
        df = pd.DataFrame(data)
        try:
            result = self.trade_manager.verify_ohlcv_data(df)
            self.assertEqual(len(result), 2)
            logging.info("Valid OHLCV data test passed")
        except Exception as e:
            logging.error(f"Valid OHLCV data test failed: {str(e)}")
            self.fail(f"Valid OHLCV data test failed: {str(e)}")
    
    def test_duplicate_timestamps(self):
        data = {
            "timestamp": [datetime(2025, 7, 1, 10, 0), datetime(2025, 7, 1, 10, 0)],
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "volume": [1000, 1200]
        }
        df = pd.DataFrame(data)
        try:
            result = self.trade_manager.verify_ohlcv_data(df)
            self.assertEqual(len(result), 1)  # Should remove duplicate
            logging.info("Duplicate timestamps test passed")
        except Exception as e:
            logging.error(f"Duplicate timestamps test failed: {str(e)}")
            self.fail(f"Duplicate timestamps test failed: {str(e)}")
    
    def test_missing_columns(self):
        data = {
            "timestamp": [datetime(2025, 7, 1, 10, 0)],
            "open": [100.0],
            "high": [102.0],
            "low": [99.0]
            # Missing close and volume
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            self.trade_manager.verify_ohlcv_data(df)
            logging.info("Missing columns test passed")
    
    def test_negative_values(self):
        data = {
            "timestamp": [datetime(2025, 7, 1, 10, 0)],
            "open": [100.0],
            "high": [102.0],
            "low": [-99.0],
            "close": [101.0],
            "volume": [1000]
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            self.trade_manager.verify_ohlcv_data(df)
            logging.info("Negative values test passed")
    
    def test_non_monotonic_timestamps(self):
        data = {
            "timestamp": [datetime(2025, 7, 1, 10, 1), datetime(2025, 7, 1, 10, 0)],
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "volume": [1000, 1200]
        }
        df = pd.DataFrame(data)
        with self.assertRaises(ValueError):
            self.trade_manager.verify_ohlcv_data(df)
            logging.info("Non-monotonic timestamps test passed")

if __name__ == "__main__":
    unittest.main()