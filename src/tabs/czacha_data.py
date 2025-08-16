# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\czacha_data.py
import json
import logging
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from src.core.error_handler import ErrorHandler
from utils.normalization import normalize_symbol

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class CzachaData:
    """Class managing data for the Czacha tab."""

    def __init__(self):
        try:
            logging.debug("Initializing CzachaData")
            self.data_file = Path(__file__).resolve().parents[2] / "data" / "czacha.json"
            self.error_handler = ErrorHandler()
            self.data = self.load_data()
            logging.debug("CzachaData initialized")
        except Exception as e:
            self.error_handler.log_error("Initializing CzachaData", f"Error initializing CzachaData: {str(e)}")
            raise

    def load_data(self):
        """Loads data from czacha.json."""
        try:
            if not self.data_file.exists():
                logging.warning("No czacha.json file found, creating empty one")
                default_data = {
                    "total_capital": 10000.0,
                    "strategies": []
                }
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2, ensure_ascii=False)
                return default_data
            
            with open(self.data_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            
            logging.info(f"Loaded czacha.json data")
            logging.info(f"Loaded total capital: {data.get('total_capital', 0.0)}")
            logging.info(f"Loaded strategies: {', '.join(s['name'] + '_' + s['symbol'] for s in data.get('strategies', []))}")
            return data
        except Exception as e:
            self.error_handler.log_error("Loading czacha.json", f"Error loading czacha.json: {str(e)}")
            return {"total_capital": 10000.0, "strategies": []}

    def save_data(self):
        """Saves data to czacha.json."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logging.info("Saved data to czacha.json")
        except Exception as e:
            self.error_handler.log_error("Saving czacha.json", f"Error saving czacha.json: {str(e)}")
            raise

    def update_total_capital(self, new_capital):
        """Updates the total capital."""
        try:
            new_capital = float(new_capital)
            if new_capital < 0:
                raise ValueError("Total capital must be non-negative")
            if abs(new_capital - self.data["total_capital"]) < 0.01:  # Avoid redundant updates
                logging.debug(f"No change in total capital: {new_capital}")
                return
            self.data["total_capital"] = new_capital
            for strategy in self.data["strategies"]:
                strategy["start_capital"] = self.data["total_capital"] * (strategy["capital_percentage"] / 100)
                if strategy.get("is_first_trade", True):
                    strategy["capital_current"] = strategy["start_capital"]
            self.save_data()
            logging.info(f"Updated total capital to {new_capital}")
        except Exception as e:
            self.error_handler.log_error("Updating total capital", f"Error updating total capital: {str(e)}")
            raise

    def update_strategy(self, strategy_name, symbol, capital_percentage=None, trade_percentage=None, reinvest=None, promotion=None):
        """Updates strategy data."""
        try:
            normalized_symbol = normalize_symbol(symbol)
            for strategy in self.data["strategies"]:
                if strategy["name"] == strategy_name and strategy["symbol"] == normalized_symbol:
                    if capital_percentage is not None:
                        strategy["capital_percentage"] = float(capital_percentage)
                        strategy["start_capital"] = self.data["total_capital"] * (strategy["capital_percentage"] / 100)
                        if strategy.get("is_first_trade", True):
                            strategy["capital_current"] = strategy["start_capital"]
                    if trade_percentage is not None:
                        strategy["trade_percentage"] = float(trade_percentage)
                    if reinvest is not None:
                        strategy["reinvest"] = reinvest
                    if promotion is not None:
                        strategy["promotion"] = promotion
                    break
            else:
                logging.warning(f"Strategy {strategy_name} with symbol {normalized_symbol} not found, adding new")
                new_strategy = {
                    "name": strategy_name,
                    "symbol": normalized_symbol,
                    "capital_percentage": float(capital_percentage or 10.0),
                    "trade_percentage": float(trade_percentage or 2.0),
                    "start_capital": self.data["total_capital"] * (float(capital_percentage or 10.0) / 100),
                    "capital_current": self.data["total_capital"] * (float(capital_percentage or 10.0) / 100),
                    "is_first_trade": True,
                    "reinvest": reinvest or "Disabled",
                    "promotion": promotion or "Enabled",
                    "days": 0,
                    "max_dd": 0.0,
                    "max_profit": 0.0,
                    "profit_live": 0.0,
                    "profit_total": 0.0
                }
                self.data["strategies"].append(new_strategy)
            self.save_data()
            logging.info(f"Updated strategy {strategy_name} with symbol {normalized_symbol}")
        except Exception as e:
            self.error_handler.log_error("Updating strategy", f"Error updating strategy {strategy_name} with symbol {normalized_symbol}: {str(e)}")
            raise

    def update_simulation_results(self, strategy_name, symbol):
        """Updates simulation results for a strategy."""
        try:
            normalized_symbol = normalize_symbol(symbol)
            summary_file = Path(__file__).resolve().parents[2] / "paper" / strategy_name / normalized_symbol / "summary.json"
            if not summary_file.exists():
                logging.warning(f"No summary.json for strategy {strategy_name} on {normalized_symbol}")
                return
            
            with open(summary_file, "r", encoding="utf-8") as f:
                summary_data = json.load(f)
            
            for strategy in self.data["strategies"]:
                if strategy["name"] == strategy_name and strategy["symbol"] == normalized_symbol:
                    strategy["days"] = summary_data.get("days_active", 0)
                    strategy["max_dd"] = summary_data.get("max_drawdown_usd", 0.0) / strategy["start_capital"] * 100 if strategy["start_capital"] > 0 else 0.0
                    strategy["max_profit"] = summary_data.get("max_profit_usd", 0.0) / strategy["start_capital"] * 100 if strategy["start_capital"] > 0 else 0.0
                    strategy["profit_total"] = summary_data.get("net_profit_usd", 0.0) / strategy["start_capital"] * 100 if strategy["start_capital"] > 0 else 0.0
                    if strategy.get("reinvest") == "Enabled":
                        strategy["capital_current"] += summary_data.get("net_profit_usd", 0.0)
                    break
            else:
                logging.warning(f"Strategy {strategy_name} with symbol {normalized_symbol} not found in czacha.json, adding new")
                new_strategy = {
                    "name": strategy_name,
                    "symbol": normalized_symbol,
                    "capital_percentage": 10.0,
                    "trade_percentage": 2.0,
                    "start_capital": self.data["total_capital"] * 0.1,
                    "capital_current": self.data["total_capital"] * 0.1,
                    "is_first_trade": True,
                    "reinvest": "Disabled",
                    "promotion": "Enabled",
                    "days": summary_data.get("days_active", 0),
                    "max_dd": summary_data.get("max_drawdown_usd", 0.0) / (self.data["total_capital"] * 0.1) * 100 if self.data["total_capital"] > 0 else 0.0,
                    "max_profit": summary_data.get("max_profit_usd", 0.0) / (self.data["total_capital"] * 0.1) * 100 if self.data["total_capital"] > 0 else 0.0,
                    "profit_live": 0.0,
                    "profit_total": summary_data.get("net_profit_usd", 0.0) / (self.data["total_capital"] * 0.1) * 100 if self.data["total_capital"] > 0 else 0.0
                }
                self.data["strategies"].append(new_strategy)
            
            self.save_data()
            logging.info(f"Updated paper trading results for {strategy_name} on {normalized_symbol}")
        except Exception as e:
            self.error_handler.log_error("Updating paper trading results", f"Error updating paper trading results for {strategy_name} on {normalized_symbol}: {str(e)}")
            raise