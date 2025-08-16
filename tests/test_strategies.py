# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_strategies.py

import os
import sys
import json
import unittest
import tkinter as tk
from tkinter import ttk
import glob
from datetime import datetime

# Dodaj folder projektu do sys.path
project_dir = "C:\\Users\\Msi\\Desktop\\investmentapp"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from src.tabs.strategies.strategies_data import StrategyData
from src.tabs.strategies.strategies_logic import import_strategy
from src.tabs.strategies.strategies_gui import StrategiesTab

class TestStrategies(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.tab = StrategiesTab(self.frame)
        self.strategy_data = StrategyData()
        with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\strategies.json", "w", encoding="utf-8-sig") as f:
            json.dump([], f, indent=4)
        with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\api_keys.json", "w", encoding="utf-8-sig") as f:
            json.dump([{"exchange": "MEXC"}, {"exchange": "Binance"}], f, indent=4)

    def test_import_strategy(self):
        try:
            self.tab.strategies = []
            self.tab.exchanges = ["MEXC", "Binance"]
            import_strategy(self.tab)
            self.tab.update_strategies_display()
            strategies = self.strategy_data.load_strategies()
            self.assertGreater(len(strategies), 0, "Strategia nie została zaimportowana")
            print(f"Test importu strategii zakończony sukcesem: {strategies}")
        except Exception as e:
            print(f"Błąd testu importu strategii: {str(e)}")
            self.fail(f"Błąd testu importu strategii: {str(e)}")

    def test_update_mode(self):
        try:
            strategy = {
                "name": "strategy_test",
                "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py",
                "mode": "Wyłączona",
                "interval": "1h",
                "exchange": "MEXC",
                "parameters": {"ma_period": 14}
            }
            self.strategy_data.strategies = [strategy]
            self.strategy_data.save_strategies()
            self.strategy_data.update_strategy_mode("strategy_test", "ETH/USDT", "Auto")
            strategies = self.strategy_data.load_strategies()
            mode = next((s["mode"] for s in strategies if s["name"] == "strategy_test"), None)
            self.assertEqual(mode, "Auto", "Tryb strategii nie został zaktualizowany")
            print(f"Test zmiany trybu zakończony sukcesem: {strategies}")
        except Exception as e:
            print(f"Błąd testu zmiany trybu: {str(e)}")
            self.fail(f"Błąd testu zmiany trybu: {str(e)}")

    def test_update_interval(self):
        try:
            strategy = {
                "name": "strategy_test",
                "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py",
                "mode": "Wyłączona",
                "interval": "1h",
                "exchange": "MEXC",
                "parameters": {"ma_period": 14}
            }
            self.strategy_data.strategies = [strategy]
            self.strategy_data.save_strategies()
            self.strategy_data.update_strategy_interval("strategy_test", "5m")
            strategies = self.strategy_data.load_strategies()
            interval = next((s["interval"] for s in strategies if s["name"] == "strategy_test"), None)
            self.assertEqual(interval, "5m", "Interwał strategii nie został zaktualizowany")
            print(f"Test zmiany interwału zakończony sukcesem: {strategies}")
        except Exception as e:
            print(f"Błąd testu zmiany interwału: {str(e)}")
            self.fail(f"Błąd testu zmiany interwału: {str(e)}")

    def test_update_exchange(self):
        try:
            strategy = {
                "name": "strategy_test",
                "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py",
                "mode": "Wyłączona",
                "interval": "1h",
                "exchange": "MEXC",
                "parameters": {"ma_period": 14}
            }
            self.strategy_data.strategies = [strategy]
            self.strategy_data.save_strategies()
            self.strategy_data.update_strategy_exchange("strategy_test", "Binance")
            strategies = self.strategy_data.load_strategies()
            exchange = next((s["exchange"] for s in strategies if s["name"] == "strategy_test"), None)
            self.assertEqual(exchange, "Binance", "Giełda strategii nie została zaktualizowana")
            print(f"Test zmiany giełdy zakończony sukcesem: {strategies}")
        except Exception as e:
            print(f"Błąd testu zmiany giełdy: {str(e)}")
            self.fail(f"Błąd testu zmiany giełdy: {str(e)}")

    def test_edit_parameters(self):
        try:
            strategy = {
                "name": "strategy_test",
                "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py",
                "mode": "Wyłączona",
                "interval": "1h",
                "exchange": "MEXC",
                "parameters": {"ma_period": 14}
            }
            self.strategy_data.strategies = [strategy]
            self.strategy_data.save_strategies()
            self.strategy_data.update_strategy_parameters("strategy_test", {"ma_period": 20}, "ETH/USDT")
            strategies = self.strategy_data.load_strategies()
            ma_period = next((s["parameters"]["ma_period"] for s in strategies if s["name"] == "strategy_test"), None)
            self.assertEqual(ma_period, 20, "Parametr strategii nie został zaktualizowany")
            print(f"Test zmiany parametrów zakończony sukcesem: {strategies}")
        except Exception as e:
            print(f"Błąd testu edycji parametrów: {str(e)}")
            self.fail(f"Błąd testu edycji parametrów: {str(e)}")

    def test_editable_background(self):
        try:
            strategy = {
                "name": "strategy_test",
                "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py",
                "mode": "Wyłączona",
                "interval": "1h",
                "exchange": "MEXC",
                "parameters": {"ma_period": 14}
            }
            self.strategy_data.strategies = [strategy]
            self.strategy_data.save_strategies()
            self.tab.update_strategies_display()
            self.tab.tree.insert("", tk.END, values=(
                "strategy_test", "Wyłączona", "ETH/USDT", "1h", "MEXC", "Edytuj", "Backtest", "Paper Trading", "Usuń"
            ), tags=("strategy_test", "editable"))
            style = ttk.Style()
            background = style.lookup("Editable.Treeview", "background")
            self.assertEqual(background, "#E0FFE0", "Edytowalne pola nie mają poprawnego tła")
            print("Test tła edytowalnych pól zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu tła edytowalnych pól: {str(e)}")
            self.fail(f"Błąd testu tła edytowalnych pól: {str(e)}")

    def test_export_backtest_csv(self):
        try:
            strategy = {
                "name": "strategy_test",
                "file_path": "C:\\Users\\Msi\\Desktop\\investmentapp\\strategies\\strategy_test.py",
                "mode": "Auto",
                "interval": "1h",
                "exchange": "MEXC",
                "parameters": {"ma_period": 14}
            }
            self.strategy_data.strategies = [strategy]
            self.strategy_data.save_strategies()
            backtest_dir = f"C:\\Users\\Msi\\Desktop\\investmentapp\\backtests\\strategy_test\\{datetime.now().year}\\{datetime.now().month:02d}"
            os.makedirs(backtest_dir, exist_ok=True)
            backtest_file = f"{backtest_dir}\\backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backtest_file, "w", encoding="utf-8") as f:
                json.dump([{
                    "symbol": "BTC/USDT",
                    "days": 100,
                    "profit": 10.0,
                    "profit_percentage": 5.0,
                    "max_dd_percentage": 2.0,
                    "min_price": 40000.0,
                    "max_price": 50000.0,
                    "signals": []
                }], f)
            self.tab.export_backtest_to_csv()
            export_file = f"C:\\Users\\Msi\\Desktop\\investmentapp\\backtests\\strategy_test\\{datetime.now().year}\\{datetime.now().month:02d}\\backtest_export_*.csv"
            summary_file = f"C:\\Users\\Msi\\Desktop\\investmentapp\\data\\exports\\summary_*.csv"
            self.assertTrue(any(os.path.exists(f) for f in glob.glob(export_file)), "Brak pliku CSV dla strategii")
            self.assertTrue(any(os.path.exists(f) for f in glob.glob(summary_file)), "Brak pliku CSV z podsumowaniem")
            print("Test eksportu backtestów do CSV zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu eksportu backtestów do CSV: {str(e)}")
            self.fail(f"Błąd testu eksportu backtestów do CSV: {str(e)}")

    def tearDown(self):
        self.root.destroy()

if __name__ == "__main__":
    unittest.main()