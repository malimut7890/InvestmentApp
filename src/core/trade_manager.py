# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager.py
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
import json
import logging
import os
import glob
import time
from datetime import datetime, timedelta
from pathlib import Path
from strategies.indicators import get_strategy_indicators
import importlib.util
import math
from zoneinfo import ZoneInfo
import shutil
import uuid
from src.core.trade_manager_base import TradeManagerBase
from src.core.trade_manager_results import TradeManagerResults
from src.tabs.czacha_data import CzachaData

class TradeManager(TradeManagerBase):
    async def fetch_alternative_ohlcv(self, symbol, timeframe, limit, primary_exchange_name):
        try:
            api_keys = self.load_api_keys()
            alternative_exchanges = [key for key in api_keys if key["exchange"].lower() != primary_exchange_name.lower()]
            for alt_key in alternative_exchanges:
                exchange_name = alt_key["exchange"].lower()
                logging.info(f"Attempting to fetch OHLCV from alternative exchange {exchange_name} for {symbol}")
                exchange_class = getattr(ccxt, exchange_name)
                exchange = exchange_class({
                    "apiKey": alt_key["api_key"],
                    "secret": alt_key["api_secret"],
                    "password": alt_key.get("passphrase", ""),
                    "rateLimit": alt_key.get("rate_limit_requests", 1800),
                    "timeout": alt_key.get("timeout_seconds", 30) * 1000
                })
                try:
                    await self.synchronize_time(exchange, exchange_name)
                    symbol = await self.validate_symbol_and_interval(exchange, symbol, timeframe)
                    last_ts = self.last_signal_time.get(f"{symbol}_{timeframe}", 0)
                    ohlcv = await asyncio.wait_for(
                        exchange.fetch_ohlcv(symbol, timeframe, since=last_ts + 1, limit=limit),
                        timeout=alt_key.get("timeout_seconds", 30)
                    )
                    if ohlcv:
                        logging.info(f"Successfully fetched {len(ohlcv)} OHLCV candles from {exchange_name} for {symbol} and {timeframe}")
                        self.save_fallback_ohlcv(symbol, timeframe, ohlcv)
                        await exchange.close()
                        return ohlcv
                    else:
                        logging.warning(f"No OHLCV data returned from {exchange_name} for {symbol}")
                except Exception as e:
                    logging.warning(f"Failed to fetch OHLCV from {exchange_name} for {timeframe}: {str(e)}")
                finally:
                    await exchange.close()
            logging.warning(f"No OHLCV data fetched from alternative exchanges for {symbol}")
            return None
        except Exception as e:
            logging.error(f"Error fetching alternative OHLCV for {symbol}: {str(e)}")
            return None

    async def validate_symbol_and_interval(self, exchange, symbol, timeframe):
        try:
            symbol, timeframe = self.normalize_symbol_and_interval(symbol, timeframe)
            available_symbols = await self.fetch_available_symbols(exchange)
            if symbol == "WBTC/USDT":
                if "WBTC/USDT" not in available_symbols:
                    logging.warning(f"WBTC/USDT not found, trying alternative format WBTCUSDT")
                    symbol = "WBTCUSDT"
                    if symbol not in available_symbols:
                        logging.error(f"Symbol {symbol} not found in exchange markets: {available_symbols[:5]}...")
                        raise ValueError(f"Symbol {symbol} not supported by exchange")
            elif symbol not in available_symbols:
                logging.error(f"Symbol {symbol} not found in exchange markets: {available_symbols[:5]}...")
                raise ValueError(f"Symbol {symbol} not supported by exchange")
            if timeframe not in exchange.timeframes:
                logging.error(f"Timeframe {timeframe} not supported by exchange: {list(exchange.timeframes.keys())}")
                raise ValueError(f"Timeframe {timeframe} not supported by exchange")
            logging.info(f"Validated symbol {symbol} and timeframe {timeframe}")
            return symbol
        except Exception as e:
            logging.error(f"Error validating symbol {symbol} and timeframe {timeframe}: {str(e)}")
            raise

    def verify_ohlcv_data(self, df):
        try:
            if df.empty:
                raise ValueError("OHLCV data is empty")
            if not all(col in df.columns for col in ["timestamp", "open", "high", "low", "close", "volume"]):
                raise ValueError("Missing required OHLCV columns")
            if df["timestamp"].isnull().any():
                raise ValueError("Missing timestamps in OHLCV data")
            if not df["timestamp"].is_monotonic_increasing:
                raise ValueError("Timestamps are not in ascending order")
            if (df[["open", "high", "low", "close", "volume"]] < 0).any().any():
                raise ValueError("Negative values in OHLCV data")
            if df["timestamp"].duplicated().any():
                logging.warning(f"Found {df['timestamp'].duplicated().sum()} duplicate timestamps in OHLCV data, removing duplicates")
                df = df.drop_duplicates(subset="timestamp", keep="last").reset_index(drop=True)
            logging.info("OHLCV data verification passed")
            return df
        except Exception as e:
            logging.error(f"OHLCV data verification failed: {str(e)}")
            raise

    def verify_results(self, trades, total_profit, win_rate, avg_max_dd, profit_factor):
        try:
            calculated_profit = sum(t["profit_usd"] for t in trades if "profit_usd" in t)
            calculated_wins = len([t for t in trades if "profit_usd" in t and t["profit_usd"] > 0])
            calculated_win_rate = (calculated_wins / len([t for t in trades if "profit_usd" in t]) * 100) if any("profit_usd" in t for t in trades) else 0
            calculated_max_dd = sum(t["max_dd_usd"] for t in trades if "max_dd_usd" in t) / len([t for t in trades if "max_dd_usd" in t]) if any("max_dd_usd" in t for t in trades) else 0
            positive_profits = sum(t["profit_usd"] for t in trades if "profit_usd" in t and t["profit_usd"] > 0)
            negative_profits = abs(sum(t["profit_usd"] for t in trades if "profit_usd" in t and t["profit_usd"] < 0))
            calculated_profit_factor = positive_profits / negative_profits if negative_profits > 0 else (0 if positive_profits == 0 else float("inf"))
            
            assert abs(calculated_profit - total_profit) < 0.01, f"Profit mismatch: calculated={calculated_profit}, reported={total_profit}"
            assert abs(calculated_win_rate - win_rate) < 0.01, f"Win rate mismatch: calculated={calculated_win_rate}, reported={win_rate}"
            assert abs(calculated_max_dd - avg_max_dd) < 0.01, f"Max DD mismatch: calculated={calculated_max_dd}, reported={avg_max_dd}"
            if negative_profits == 0 and positive_profits == 0:
                logging.info("No profits or losses, setting profit factor to 0, verification passed")
                calculated_profit_factor = 0
            elif negative_profits == 0 and math.isinf(profit_factor):
                logging.info("Profit factor is infinite for both calculated and reported, verification passed")
            else:
                assert abs(calculated_profit_factor - profit_factor) < 0.01, f"Profit factor mismatch: calculated={calculated_profit_factor}, reported={profit_factor}"
            logging.info("Simulation results verification passed")
        except AssertionError as e:
            logging.error(f"Simulation results verification failed: {str(e)}")
            error_file = self.base_dir / "simulations" / "errors.log"
            error_file.parent.mkdir(parents=True, exist_ok=True)
            with open(error_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now(tz=ZoneInfo('Europe/Warsaw')).isoformat()}: Simulation error: {str(e)}\n")
            raise
        except Exception as e:
            logging.error(f"Error verifying simulation results: {str(e)}")
            raise

    def verify_signals(self, signal, df, strategy_instance, parameters):
        try:
            if signal in ["buy", "sell"]:
                if df["timestamp"].iloc[-1].tzinfo is None:
                    raise ValueError("Timestamp of last candle is not timezone-aware")
            logging.info("Signal verification passed")
            return True
        except Exception as e:
            logging.error(f"Signal verification failed: {str(e)}")
            return False

    def update_active_strategy(self, strategy_name, symbol, start_time):
        """Aktualizuje informacje o aktywności strategii"""
        key = f"{strategy_name}_{symbol}"
        if key not in self.active_strategies:
            self.active_strategies[key] = {
                "start_date": start_time.date().isoformat(),
                "last_active": start_time.date().isoformat()
            }
        else:
            self.active_strategies[key]["last_active"] = start_time.date().isoformat()
        try:
            active_file = self.base_dir / "data" / "active_strategies.json"
            with open(active_file, "w", encoding="utf-8") as f:
                json.dump(self.active_strategies, f, indent=4, ensure_ascii=False)
            logging.info(f"Updated active strategies in {active_file}")
        except Exception as e:
            logging.error(f"Error updating active strategies: {str(e)}")

    def reset_for_new_symbol(self, strategy_name, symbol):
        try:
            strategy_key = f"{strategy_name}_{symbol.replace('/', '_')}"
            if strategy_key in self.positions:
                del self.positions[strategy_key]
                logging.info(f"Reset positions for strategy {strategy_name} on {symbol}")
        except Exception as e:
            logging.error(f"Error resetting positions for {strategy_name} on {symbol}: {str(e)}")
            raise

    def reset_for_new_strategy(self, strategy_name, symbol, timeframe):
        try:
            key = f"{strategy_name}_{symbol}"
            for mode in ["simulations", "live"]:
                old_dir = self.base_dir / mode / strategy_name / symbol.replace('/', '_')
                shutil.rmtree(old_dir, ignore_errors=True)
                logging.info(f"Removed directory {old_dir} for strategy {strategy_name} and symbol {symbol}")
            self.last_signal_time.pop(key, None)
            self.positions.pop(key, None)
            self.order_lock.pop(key, None)
            self.active_strategies.pop(key, None)
            
            # Clear data/summary.json for the strategy and symbol
            data_summary_file = self.base_dir / "data" / "summary.json"
            if data_summary_file.exists():
                with open(data_summary_file, "r", encoding="utf-8-sig") as f:
                    summary_data = json.load(f)
                if isinstance(summary_data, dict) and summary_data.get("strategy") == strategy_name and summary_data.get("symbol") == symbol:
                    data_summary_file.unlink(missing_ok=True)
                    logging.info(f"Cleared summary.json for strategy {strategy_name} and symbol {symbol} in data folder")
                elif isinstance(summary_data, list):
                    summary_data = [s for s in summary_data if not (s.get("strategy") == strategy_name and s.get("symbol") == symbol)]
                    with open(data_summary_file, "w", encoding="utf-8") as f:
                        json.dump(summary_data, f, indent=4, ensure_ascii=False)
                    logging.info(f"Updated summary.json by removing {strategy_name} and {symbol} in data folder")
            
            # Clear active strategies file
            active_file = self.base_dir / "data" / "active_strategies.json"
            if active_file.exists():
                with open(active_file, "r", encoding="utf-8") as f:
                    active_data = json.load(f)
                active_data.pop(key, None)
                with open(active_file, "w", encoding="utf-8") as f:
                    json.dump(active_data, f, indent=4, ensure_ascii=False)
                logging.info(f"Cleared active strategy {key} from {active_file}")
            
            logging.info(f"Reset state for {strategy_name} on {symbol}")
        except Exception as e:
            logging.error(f"Error resetting state for {strategy_name} on {symbol}: {str(e)}")
            raise