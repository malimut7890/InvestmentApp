# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_data.py

import json
import logging
from pathlib import Path
from src.core.trade_manager_results_handler import TradeManagerResultsHandler
from src.core.trade_manager_summary import TradeManagerSummary
from src.core.error_handler import ErrorHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class StrategyData:
    """Klasa zarządzająca danymi strategii handlowych."""

    def __init__(self):
        try:
            logging.debug("Initializing StrategyData")
            self.results_handler = TradeManagerResultsHandler()
            self.summary_handler = TradeManagerSummary()
            self.error_handler = ErrorHandler()
            self.strategies_file = Path(__file__).resolve().parents[3] / "data" / "strategies.json"
            logging.debug("StrategyData initialized")
        except Exception as e:
            self.error_handler.log_error("Initializing StrategyData", f"Error initializing StrategyData: {str(e)}")
            raise

    def load_strategies(self):
        """Ładuje strategie z pliku strategies.json.

        Returns:
            list: Lista strategii.
        """
        try:
            if not self.strategies_file.exists():
                logging.warning("No strategies.json file found, creating empty one")
                with open(self.strategies_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
                return []
            with open(self.strategies_file, "r", encoding="utf-8-sig") as f:
                strategies = json.load(f)
            logging.info(f"Loaded strategies: {', '.join(s['name'] + '_' + s['symbol'] for s in strategies)}")
            return strategies
        except Exception as e:
            self.error_handler.log_error("Loading strategies", f"Error loading strategies: {str(e)}")
            return []

    def save_strategies(self, strategies=None):
        """Zapisuje strategie do pliku strategies.json.

        Args:
            strategies (list, optional): Lista strategii do zapisania. Jeśli None, ładuje istniejące strategie.
        """
        try:
            if strategies is None:
                strategies = self.load_strategies()
            with open(self.strategies_file, "w", encoding="utf-8") as f:
                json.dump(strategies, f, indent=2, ensure_ascii=False)
            logging.info(f"Saved strategies to {self.strategies_file}")
        except Exception as e:
            self.error_handler.log_error("Saving strategies", f"Error saving strategies: {str(e)}")
            raise

    def update_strategy_mode(self, strategy_name: str, symbol: str, mode: str):
        """Aktualizuje tryb strategii.

        Args:
            strategy_name (str): Nazwa strategii.
            symbol (str): Symbol handlowy.
            mode (str): Nowy tryb (Wylaczona, Live, Paper, Auto).
        """
        try:
            strategies = self.load_strategies()
            for strategy in strategies:
                if strategy["name"] == strategy_name and strategy["symbol"] == symbol:
                    strategy["mode"] = mode
                    break
            else:
                logging.warning(f"Strategy {strategy_name} with symbol {symbol} not found, adding new")
                strategies.append({"name": strategy_name, "symbol": symbol, "mode": mode, "interval": "1m", "exchange": "MEXC", "parameters": {}, "file_path": ""})
            self.save_strategies(strategies)
            logging.info(f"Updated mode for strategy {strategy_name} with symbol {symbol} to {mode}")
        except Exception as e:
            self.error_handler.log_error("Updating strategy mode", f"Error updating mode for {strategy_name} with symbol {symbol}: {str(e)}")
            raise

    def update_strategy_symbol(self, strategy_name: str, new_symbol: str):
        """Aktualizuje symbol strategii.

        Args:
            strategy_name (str): Nazwa strategii.
            new_symbol (str): Nowy symbol.
        """
        try:
            strategies = self.load_strategies()
            for strategy in strategies:
                if strategy["name"] == strategy_name:
                    strategy["symbol"] = new_symbol
                    break
            else:
                logging.warning(f"Strategy {strategy_name} not found, adding new")
                strategies.append({"name": strategy_name, "symbol": new_symbol, "mode": "Wylaczona", "interval": "1m", "exchange": "MEXC", "parameters": {}, "file_path": ""})
            self.save_strategies(strategies)
            logging.info(f"Updated symbol for strategy {strategy_name} to {new_symbol}")
        except Exception as e:
            self.error_handler.log_error("Updating strategy symbol", f"Error updating symbol for {strategy_name}: {str(e)}")
            raise

    def update_strategy_interval(self, strategy_name: str, new_interval: str):
        """Aktualizuje interwał strategii.

        Args:
            strategy_name (str): Nazwa strategii.
            new_interval (str): Nowy interwał.
        """
        try:
            strategies = self.load_strategies()
            for strategy in strategies:
                if strategy["name"] == strategy_name:
                    strategy["interval"] = new_interval
                    break
            else:
                logging.warning(f"Strategy {strategy_name} not found, adding new")
                strategies.append({"name": strategy_name, "symbol": "", "mode": "Wylaczona", "interval": new_interval, "exchange": "MEXC", "parameters": {}, "file_path": ""})
            self.save_strategies(strategies)
            logging.info(f"Updated interval for strategy {strategy_name} to {new_interval}")
        except Exception as e:
            self.error_handler.log_error("Updating strategy interval", f"Error updating interval for {strategy_name}: {str(e)}")
            raise

    def update_strategy_exchange(self, strategy_name: str, new_exchange: str):
        """Aktualizuje giełdę strategii.

        Args:
            strategy_name (str): Nazwa strategii.
            new_exchange (str): Nowa giełda.
        """
        try:
            strategies = self.load_strategies()
            for strategy in strategies:
                if strategy["name"] == strategy_name:
                    strategy["exchange"] = new_exchange
                    break
            else:
                logging.warning(f"Strategy {strategy_name} not found, adding new")
                strategies.append({"name": strategy_name, "symbol": "", "mode": "Wylaczona", "interval": "1m", "exchange": new_exchange, "parameters": {}, "file_path": ""})
            self.save_strategies(strategies)
            logging.info(f"Updated exchange for strategy {strategy_name} to {new_exchange}")
        except Exception as e:
            self.error_handler.log_error("Updating strategy exchange", f"Error updating exchange for {strategy_name}: {str(e)}")
            raise

    def update_strategy_parameters(self, strategy_name: str, parameters: dict, symbol: str):
        """Aktualizuje parametry strategii.

        Args:
            strategy_name (str): Nazwa strategii.
            parameters (dict): Nowe parametry.
            symbol (str): Symbol handlowy.
        """
        try:
            strategies = self.load_strategies()
            for strategy in strategies:
                if strategy["name"] == strategy_name and strategy["symbol"] == symbol:
                    strategy["parameters"] = parameters
                    break
            else:
                logging.warning(f"Strategy {strategy_name} with symbol {symbol} not found, adding new")
                strategies.append({"name": strategy_name, "symbol": symbol, "mode": "Wylaczona", "interval": "1m", "exchange": "MEXC", "parameters": parameters, "file_path": ""})
            self.save_strategies(strategies)
            logging.info(f"Updated parameters for strategy {strategy_name} with symbol {symbol}: {parameters}")
        except Exception as e:
            self.error_handler.log_error("Updating strategy parameters", f"Error updating parameters for {strategy_name} with symbol {symbol}: {str(e)}")
            raise

    def delete_strategy(self, strategy_name: str, symbol: str):
        """Usuwa strategię.

        Args:
            strategy_name (str): Nazwa strategii.
            symbol (str): Symbol handlowy.
        """
        try:
            strategies = self.load_strategies()
            strategies = [s for s in strategies if not (s["name"] == strategy_name and s["symbol"] == symbol)]
            self.save_strategies(strategies)
            logging.info(f"Deleted strategy {strategy_name} with symbol {symbol}")
        except Exception as e:
            self.error_handler.log_error("Deleting strategy", f"Error deleting strategy {strategy_name} with symbol {symbol}: {str(e)}")
            raise