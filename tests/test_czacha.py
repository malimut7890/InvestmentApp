# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_czacha.py

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

from src.tabs.czacha import CzachaTab
from src.tabs.strategies.strategies_data import StrategyData

class TestCzacha(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.frame = tk.Frame(self.root)
        self.tab = CzachaTab(self.frame)
        self.strategy_data = StrategyData()
        # Wyczyść czacha.json i strategies.json
        with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\czacha.json", "w", encoding="utf-8-sig") as f:
            json.dump({"total_capital": 55.0, "strategies": []}, f, indent=4)
        with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\strategies.json", "w", encoding="utf-8-sig") as f:
            json.dump([], f, indent=4)

    def test_load_active_strategies(self):
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
            self.tab.load_data()
            items = self.tab.tree.get_children()
            self.assertGreater(len(items), 0, "Aktywne strategie nie zostały wczytane")
            values = self.tab.tree.item(items[0], "values")
            self.assertEqual(values[0], "Auto", "Tryb strategii niepoprawny w tabelce Czacha")
            print("Test wczytywania aktywnych strategii zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu wczytywania aktywnych strategii: {str(e)}")
            self.fail(f"Błąd testu wczytywania aktywnych strategii: {str(e)}")

    def test_edit_fields(self):
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
            self.tab.load_data()
            czacha_data = {"total_capital": 55.0, "strategies": [
                {
                    "name": "strategy_test",
                    "symbol": "ETH/USDT",
                    "capital_percentage": 10.0,
                    "trade_percentage": 5.0,
                    "start_capital": 5.5,
                    "capital_current": 5.5,
                    "is_first_trade": True,
                    "reinvest": "Wyłączona",
                    "promotion": "Włączony",
                    "days": 0,
                    "max_dd": 0.0,
                    "max_profit": 0.0,
                    "profit_live": 0.0,
                    "profit_total": 0.0
                }
            ]}
            with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\czacha.json", "w", encoding="utf-8-sig") as f:
                json.dump(czacha_data, f, indent=4)
            self.tab.load_data()
            with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\czacha.json", "r", encoding="utf-8-sig") as f:
                czacha_data = json.load(f)
            trade_percentage = next((s["trade_percentage"] for s in czacha_data["strategies"] if s["name"] == "strategy_test"), None)
            self.assertEqual(trade_percentage, 5.0, "Zmiana % na zagranie nie zapisana")
            print("Test edycji pól zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu edycji pól: {str(e)}")
            self.fail(f"Błąd testu edycji pól: {str(e)}")

    def test_start_capital_non_editable(self):
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
            czacha_data = {"total_capital": 55.0, "strategies": [
                {
                    "name": "strategy_test",
                    "symbol": "ETH/USDT",
                    "capital_percentage": 10.0,
                    "trade_percentage": 2.0,
                    "start_capital": 5.5,
                    "capital_current": 5.5,
                    "is_first_trade": True,
                    "reinvest": "Wyłączona",
                    "promotion": "Włączony",
                    "days": 0,
                    "max_dd": 0.0,
                    "max_profit": 0.0,
                    "profit_live": 0.0,
                    "profit_total": 0.0
                }
            ]}
            with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\czacha.json", "w", encoding="utf-8-sig") as f:
                json.dump(czacha_data, f, indent=4)
            self.tab.load_data()
            with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\czacha.json", "r", encoding="utf-8-sig") as f:
                czacha_data = json.load(f)
            total_capital = czacha_data["total_capital"]
            expected_start_capital = total_capital * 0.1
            start_capital = next((s["start_capital"] for s in czacha_data["strategies"] if s["name"] == "strategy_test"), None)
            self.assertEqual(start_capital, expected_start_capital, f"Kapitał start niepoprawny: {start_capital} != {expected_start_capital}")
            print("Test nieedytowalności Kapitał start zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu nieedytowalności Kapitał start: {str(e)}")
            self.fail(f"Błąd testu nieedytowalności Kapitał start: {str(e)}")

    def test_editable_background(self):
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
            self.tab.load_data()
            self.tab.tree.insert("", tk.END, values=(
                "Auto", "strategy_test", "ETH/USDT", "5.50", "2.0", "0.11", "10.0", "5.50", "0", "0.0", "0.0", "0.0", "0.0", "Wyłączona", "Włączony"
            ), tags=("strategy_test", "editable"))
            style = ttk.Style()
            background = style.lookup("Editable.Treeview", "background")
            self.assertEqual(background, "#E0FFE0", "Edytowalne pola nie mają poprawnego tła")
            print("Test tła edytowalnych pól zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu tła edytowalnych pól: {str(e)}")
            self.fail(f"Błąd testu tła edytowalnych pól: {str(e)}")

    def test_total_capital_update(self):
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
            self.tab.total_capital_var.set("100.0")
            self.tab.save_total_capital()
            with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\czacha.json", "r", encoding="utf-8-sig") as f:
                czacha_data = json.load(f)
            total_capital = czacha_data["total_capital"]
            self.assertEqual(total_capital, 100.0, "Całkowity kapitał nie został zaktualizowany")
            start_capital = next((s["start_capital"] for s in czacha_data["strategies"] if s["name"] == "strategy_test"), None)
            self.assertEqual(start_capital, 10.0, "Kapitał start nie został zaktualizowany na podstawie Całkowitego kapitału")
            capital_current = next((s["capital_current"] for s in czacha_data["strategies"] if s["name"] == "strategy_test"), None)
            self.assertEqual(capital_current, 10.0, "Kapitał strategii nie został zaktualizowany na podstawie Całkowitego kapitału")
            position_value = next((s["trade_percentage"] * s["capital_current"] / 100 for s in czacha_data["strategies"] if s["name"] == "strategy_test"), None)
            self.assertEqual(position_value, 0.2, "Wartość pozycji nie została zaktualizowana")
            print("Test aktualizacji Całkowitego kapitału zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu aktualizacji Całkowitego kapitału: {str(e)}")
            self.fail(f"Błąd testu aktualizacji Całkowitego kapitału: {str(e)}")

    def test_export_czacha_csv(self):
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
            self.tab.load_data()
            self.tab.export_to_csv()
            export_file = f"C:\\Users\\Msi\\Desktop\\investmentapp\\data\\exports\\czacha_export_*.csv"
            self.assertTrue(any(os.path.exists(f) for f in glob.glob(export_file)), "Brak pliku CSV z danymi Czacha")
            print("Test eksportu danych Czacha do CSV zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu eksportu danych Czacha do CSV: {str(e)}")
            self.fail(f"Błąd testu eksportu danych Czacha do CSV: {str(e)}")

    def test_save_total_capital(self):
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
            self.tab.total_capital_var.set("200.0")
            self.tab.save_total_capital()
            with open("C:\\Users\\Msi\\Desktop\\investmentapp\\data\\czacha.json", "r", encoding="utf-8-sig") as f:
                czacha_data = json.load(f)
            self.assertEqual(czacha_data["total_capital"], 200.0, "Całkowity kapitał nie został zapisany")
            print("Test zapisu Całkowitego kapitału zakończony sukcesem")
        except Exception as e:
            print(f"Błąd testu zapisu Całkowitego kapitału: {str(e)}")
            self.fail(f"Błąd testu zapisu Całkowitego kapitału: {str(e)}")

    def tearDown(self):
        self.root.destroy()

if __name__ == "__main__":
    unittest.main()