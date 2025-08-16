# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_gui_simulation.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import asyncio
import threading
import ccxt.async_support as ccxt
from datetime import datetime
from zoneinfo import ZoneInfo
from src.core.trade_manager_simulation import TradeManagerSimulation
from src.tabs.symbols import SymbolsTab
from src.tabs.strategies.strategies_data import StrategyData
from pathlib import Path
import json
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

class StrategiesTabSimulation:
    """Klasa obsługująca symulacje w zakładce Strategie."""

    def __init__(self, frame, symbols_tab: SymbolsTab, simulation_tab, strategy_data: StrategyData, trade_manager: TradeManagerSimulation):
        self.frame = frame
        self.symbols_tab = symbols_tab
        self.simulation_tab = simulation_tab
        self.strategy_data = strategy_data
        self.trade_manager = trade_manager
        self.strategies = self.strategy_data.load_strategies()
        self.simulation_tasks = {}
        self.error_handler = ErrorHandler()

    def run_historical_simulation(self):
        """Otwiera okno do uruchamiania symulacji historycznej."""
        try:
            if not self.strategies:
                self.error_handler.log_and_show_error(self.frame, "Running historical simulation", "No strategies available for simulation")
                return
            
            window = tk.Toplevel(self.frame)
            window.title("Historical Simulation")
            window.geometry("600x400")
            window.transient(self.frame)
            window.grab_set()
            
            tk.Label(window, text="Strategy:").pack(pady=5)
            strategy_var = tk.StringVar(value=self.strategies[0]["name"] if self.strategies else "")
            strategy_combo = ttk.Combobox(window, textvariable=strategy_var, values=[s["name"] for s in self.strategies], state="readonly")
            strategy_combo.pack(pady=5)
            
            tk.Label(window, text="Symbol:").pack(pady=5)
            strategy = next((s for s in self.strategies if s["name"] == strategy_var.get()), None)
            default_symbol = strategy.get("symbol", "") if strategy else ""
            if not default_symbol:
                fresh_symbols = self.symbols_tab.get_active_symbols()
                default_symbol = fresh_symbols[0] if fresh_symbols else ""
            symbol_var = tk.StringVar(value=default_symbol)
            fresh_symbols = self.symbols_tab.get_active_symbols()
            if not fresh_symbols:
                self.error_handler.log_and_show_error(self.frame, "Running historical simulation", "No active symbols available")
                window.destroy()
                return
            symbol_combo = ttk.Combobox(window, textvariable=symbol_var, values=fresh_symbols, state="readonly")
            symbol_combo.pack(pady=5)
            symbol_combo.bind("<<ComboboxSelected>>", lambda e: self._on_symbol_selected(strategy_var.get(), symbol_var.get(), None))
            
            tk.Label(window, text="Period (number of candles):").pack(pady=5)
            period_var = tk.StringVar(value="2000")
            period_entry = ttk.Entry(window, textvariable=period_var)
            period_entry.pack(pady=5)
            
            tk.Label(window, text="Interval:").pack(pady=5)
            interval_var = tk.StringVar(value="1m")
            interval_combo = ttk.Combobox(window, textvariable=interval_var, values=["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo"], state="readonly")
            interval_combo.pack(pady=5)
            
            def run_simulation_action():
                try:
                    strategy_name = strategy_var.get()
                    symbol = symbol_var.get()
                    period = int(period_var.get())
                    interval = interval_var.get()
                    if period < 1:
                        raise ValueError("Period must be greater than 0")
                    if not symbol:
                        self.error_handler.log_and_show_error(self.frame, "Running historical simulation", "No symbol selected")
                        return
                    
                    strategies_tab = self.frame.master.children['!notebook'].children['!frame2'].children['!strategiestab']
                    strategies_tab.progress_label.config(text=f"Starting historical simulation for {strategy_name}...")
                    result = self.trade_manager.start_simulation(strategy_name, symbol, interval, mode="history", limit=period)
                    self.simulation_tab._refresh_results([result])
                    strategies_tab.progress_label.config(text="")
                    tk.messagebox.showinfo("Success", f"Started historical simulation for {strategy_name} on {symbol}")
                    window.destroy()
                except Exception as e:
                    strategies_tab = self.frame.master.children['!notebook'].children['!frame2'].children['!strategiestab']
                    strategies_tab.progress_label.config(text="")
                    self.error_handler.log_and_show_error(self.frame, "Running historical simulation", f"Błąd podczas symulacji historycznej: {str(e)}")
            
            ttk.Button(window, text="Run Simulation", command=run_simulation_action).pack(pady=10)
            ttk.Button(window, text="Close", command=window.destroy).pack(pady=10)
            logging.info("Opened historical simulation window")
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Opening historical simulation window", f"Błąd podczas otwierania okna symulacji: {str(e)}")

    def _on_symbol_selected(self, strategy_name: str, new_symbol: str, window):
        """Obsługuje zmianę symbolu w oknie symulacji."""
        try:
            logging.info(f"Selected symbol {new_symbol} for strategy {strategy_name}")
            if not new_symbol:
                self.error_handler.log_and_show_error(self.frame, "Selecting symbol", "No symbol selected")
                return
            if window:
                window.destroy()
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Selecting symbol", f"Błąd podczas wybierania symbolu: {str(e)}")

    async def _start_simulation_async(self, strategy_name: str, symbol: str, interval: str, mode: str):
        """Uruchamia asynchroniczną symulację Paper Trading."""
        try:
            logging.info(f"Starting async paper trading for strategy {strategy_name} on {symbol} with interval {interval} and mode {mode}")
            promotion_file = Path(__file__).resolve().parents[3] / "data" / "promotion.json"
            strategies_file = Path(__file__).resolve().parents[3] / "data" / "strategies.json"
            simulation_settings_file = Path(__file__).resolve().parents[3] / "data" / "simulation_settings.json"
            
            # Load simulation settings
            try:
                with open(simulation_settings_file, "r", encoding="utf-8") as f:
                    simulation_settings = json.load(f)
                limit = int(simulation_settings.get("Ilosc dni symulacji", 1)) * 1440  # Convert days to minutes for 1m candles
                logging.info(f"Loaded simulation settings: limit={limit} candles")
            except Exception as e:
                self.error_handler.log_error("Loading simulation settings", f"Error loading simulation_settings.json: {str(e)}")
                limit = 1440  # Default to 1 day
                logging.info(f"Using default simulation limit: {limit} candles")
            
            # Dynamic volatility filter
            strategy = next((s for s in self.strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
            if not strategy:
                self.error_handler.log_error("Starting simulation", f"Strategy {strategy_name} with symbol {symbol} not found")
                raise ValueError(f"Strategy {strategy_name} with symbol {symbol} not found")
            min_volatility = strategy.get("parameters", {}).get("min_volatility", 0.1)
            logging.info(f"Using min_volatility={min_volatility} for strategy {strategy_name}")
            
            # Validate symbol and interval
            exchange_name = strategy.get("exchange", "MEXC").lower()
            api_keys = self.trade_manager.load_api_keys()
            api_key_data = next((key for key in api_keys if key["exchange"].lower() == exchange_name), None)
            if not api_key_data:
                self.error_handler.log_error("Starting simulation", f"No API key found for exchange {exchange_name}")
                raise ValueError(f"No API key found for exchange {exchange_name}")
            if not api_key_data["api_key"] or not api_key_data["api_secret"]:
                self.error_handler.log_error("Starting simulation", f"Invalid API key or secret for exchange {exchange_name}")
                raise ValueError(f"Invalid API key or secret for exchange {exchange_name}")
            
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class({
                "apiKey": api_key_data["api_key"],
                "secret": api_key_data["api_secret"],
                "password": api_key_data.get("passphrase", ""),
                "rateLimit": api_key_data.get("rate_limit_requests", 1800),
                "timeout": api_key_data.get("timeout_seconds", 30) * 1000
            })
            try:
                symbol = await self.trade_manager.validate_symbol_and_interval(exchange, symbol, interval)
                logging.info(f"Symbol {symbol} and interval {interval} validated successfully for {exchange_name}")
            except Exception as e:
                self.error_handler.log_error("Validating symbol", f"Symbol {symbol} or interval {interval} validation failed: {str(e)}")
                await exchange.close()
                raise
            
            start_time = datetime.now(tz=ZoneInfo("Europe/Warsaw"))
            while True:
                # Check current mode
                with open(strategies_file, "r", encoding="utf-8") as f:
                    try:
                        strategies = json.load(f)
                    except json.JSONDecodeError as e:
                        self.error_handler.log_error("Loading strategies", f"Invalid JSON in strategies.json: {str(e)}")
                        raise ValueError(f"Invalid JSON in strategies.json: {str(e)}")
                strategy = next((s for s in strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
                if not strategy or strategy["mode"] not in ["Paper", "Auto"]:
                    logging.info(f"Stopping paper trading for {strategy_name} as mode is {strategy.get('mode', 'unknown') if strategy else 'not found'}")
                    break
                
                # Run paper trading
                try:
                    result = await self.trade_manager.paper_trade(strategy_name, symbol, interval, mode=mode)
                    logging.info(f"Paper trading iteration completed for {strategy_name} on {symbol}, signals: {result.get('signals', [])}")
                except Exception as e:
                    self.error_handler.log_and_show_error(self.frame, "Running paper trading", f"Paper trading failed for {strategy_name} on {symbol}: {str(e)}")
                    await asyncio.sleep(60)
                    continue
                
                # Apply volatility filter to signals
                if result["signals"] and result["close"]:
                    filtered_signals = []
                    prev_price = None
                    for i, signal in enumerate(result["signals"]):
                        current_price = result["close"][i]
                        if prev_price is not None:
                            volatility = abs((current_price - prev_price) / prev_price * 100)
                            if volatility < min_volatility and signal in ["buy", "sell"]:
                                logging.info(f"Filtered signal for {strategy_name} on {symbol} at index {i}: volatility {volatility:.2f}% < {min_volatility}%")
                                filtered_signals.append(None)
                            else:
                                filtered_signals.append(signal)
                        else:
                            filtered_signals.append(signal)
                        prev_price = current_price
                    result["signals"] = filtered_signals
                    logging.info(f"Applied volatility filter to signals for {strategy_name} on {symbol}: {result['signals']}")
                
                # Update SimulationTab results
                try:
                    self.simulation_tab._refresh_results([result])
                    logging.info(f"Updated SimulationTab results for {strategy_name} on {symbol}")
                except Exception as e:
                    self.error_handler.log_error("Updating SimulationTab", f"Error updating SimulationTab for {strategy_name} on {symbol}: {str(e)}")
                
                if mode == "auto":
                    # Load promotion settings
                    try:
                        with open(promotion_file, "r", encoding="utf-8") as f:
                            promotion_data = json.load(f)
                        auto_days = promotion_data.get("auto_settings", {}).get("auto_days", 30.0)
                        required_profit = promotion_data.get("auto_settings", {}).get("required_profit", 20.0)
                    except Exception as e:
                        self.error_handler.log_error("Loading promotion settings", f"Error loading promotion.json: {str(e)}")
                        auto_days, required_profit = 30.0, 20.0
                        logging.info(f"Using default auto settings: auto_days={auto_days}, required_profit={required_profit}")
                    
                    # Check if Auto mode should transition to Live
                    days_elapsed = (datetime.now(tz=ZoneInfo("Europe/Warsaw")) - start_time).days
                    if days_elapsed >= auto_days and result["profit_percentage"] >= required_profit:
                        logging.info(f"Strategy {strategy_name} meets Auto mode criteria, transitioning to Live")
                        self.strategy_data.update_strategy_mode(strategy_name, symbol, "Live")
                        strategies_tab = self.frame.master.children['!notebook'].children['!frame2'].children['!strategiestab']
                        strategies_tab.handlers.update_strategies_display()
                        self.simulation_tab.update_strategies_display()
                        strategies_tab.progress_label.config(text=f"Aktywowano Live dla {strategy_name} na {symbol}")
                        break
                
                # Wait 1 minute before next iteration
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            logging.info(f"Paper trading task cancelled for strategy {strategy_name}")
            raise
        except Exception as e:
            self.error_handler.log_and_show_error(self.frame, "Running paper trading", f"Error in paper trading for {strategy_name} on {symbol}: {str(e)}")
            raise
        finally:
            if f"{strategy_name}_{symbol}" in self.simulation_tasks:
                self.simulation_tasks.pop(f"{strategy_name}_{symbol}")
                strategies_tab = self.frame.master.children['!notebook'].children['!frame2'].children['!strategiestab']
                strategies_tab.handlers.update_strategies_display()
                self.simulation_tab.update_strategies_display()
            if "exchange" in locals():
                await exchange.close()