# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager_simulation.py
import logging
import json
import ccxt.async_support as ccxt
import pandas as pd
import importlib.util
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import asyncio
import threading
from src.core.trade_manager_base import TradeManagerBase
from src.core.trade_manager_results_handler import TradeManagerResultsHandler
from src.core.error_handler import ErrorHandler
from src.tabs.czacha_data import CzachaData
from utils.normalization import normalize_symbol, normalize_interval

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TradeManagerSimulation(TradeManagerBase):
    """Class responsible for trading simulations, including real-time Paper Trading."""

    def __init__(self):
        super().__init__()
        self.strategies = {}
        self.active_trades = {}
        self.results_handler = TradeManagerResultsHandler()
        self.error_handler = ErrorHandler()
        self.czacha_data = CzachaData()
        self.loop = asyncio.new_event_loop()

    def load_strategies(self):
        """Loads strategies from strategies.json.

        Returns:
            list: List of strategies.
        """
        try:
            strategies_file = Path(__file__).resolve().parents[2] / "data" / "strategies.json"
            if not strategies_file.exists():
                logging.warning("No strategies.json file found")
                return []
            with open(strategies_file, "r", encoding="utf-8-sig") as f:
                strategies = json.load(f)
            logging.info(f"Loaded strategies: {[s['name'] for s in strategies]}")
            return strategies
        except Exception as e:
            self.error_handler.log_error("Loading strategies", f"Error loading strategies: {str(e)}")
            return []

    def reset_for_new_symbol(self, strategy_name: str, old_symbol: str):
        """Resets state for a new symbol.

        Args:
            strategy_name (str): Name of the strategy.
            old_symbol (str): Previous symbol.
        """
        try:
            normalized_old_symbol = normalize_symbol(old_symbol)
            if strategy_name in self.active_trades and normalized_old_symbol in self.active_trades[strategy_name]:
                del self.active_trades[strategy_name][normalized_old_symbol]
                logging.info(f"Reset state for strategy {strategy_name} and symbol {normalized_old_symbol}")
        except Exception as e:
            self.error_handler.log_error("Resetting symbol", f"Error resetting state for {strategy_name} and {old_symbol}: {str(e)}")

    def reset_for_new_strategy(self, strategy_name: str):
        """Resets state for a new strategy.

        Args:
            strategy_name (str): Name of the strategy.
        """
        try:
            if strategy_name in self.active_trades:
                del self.active_trades[strategy_name]
                logging.info(f"Reset state for strategy {strategy_name}")
        except Exception as e:
            self.error_handler.log_error("Resetting strategy", f"Error resetting state for {strategy_name}: {str(e)}")

    async def paper_trade(self, strategy_name: str, symbol: str, interval: str, mode: str = "simulations") -> dict:
        """Simulates real-time trading (Paper Trading) without actual transactions.

        Args:
            strategy_name (str): Name of the strategy.
            symbol (str): Trading symbol (e.g., BTC/USDT).
            interval (str): Time interval (e.g., '1m').
            mode (str): Mode for saving results ('simulations' by default).

        Returns:
            dict: Simulation results (signals, trades, statistics).

        Raises:
            ValueError: If the strategy, symbol, or OHLCV data is invalid.
        """
        try:
            normalized_symbol = normalize_symbol(symbol)
            normalized_interval = normalize_interval(interval)
            logging.info(f"Starting paper trading for strategy {strategy_name} on {normalized_symbol} with interval {normalized_interval}")
            strategies_file = Path(__file__).resolve().parents[2] / "data" / "strategies.json"
            start_time = datetime.now(tz=ZoneInfo("Europe/Warsaw"))
            
            # Load initial capital from czacha.json
            czacha_data = self.czacha_data.load_data()
            strategy_data = next((s for s in czacha_data["strategies"] if s["name"] == strategy_name and s["symbol"] == normalized_symbol), None)
            initial_capital = strategy_data["start_capital"] if strategy_data else 1000.0
            capital = initial_capital
            position = 0
            entry_price = 0
            profit = 0
            max_dd = 0
            max_profit = 0
            equity_curve = [initial_capital]
            trades = []

            # Initialize strategy
            with open(strategies_file, "r", encoding="utf-8-sig") as f:
                strategies = json.load(f)
            strategy_data = next((s for s in strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
            if not strategy_data:
                raise ValueError(f"Strategy {strategy_name} with symbol {symbol} not found")

            file_path = strategy_data.get("file_path")
            if not file_path or not Path(file_path).exists():
                raise ValueError(f"No valid file path for strategy {strategy_name}: {file_path}")

            spec = importlib.util.spec_from_file_location(strategy_name, file_path)
            if spec is None:
                raise ValueError(f"Invalid file path for strategy {strategy_name}: {file_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            strategy = getattr(module, "Strategy", None)
            if not strategy:
                raise ValueError(f"No Strategy class in {file_path}")

            strategy_instance = strategy()
            strategy_instance.update_indicators(strategy_data.get("parameters", {}))

            # Initialize exchange
            api_keys = self.load_api_keys()
            api_key_data = next((key for key in api_keys if key["exchange"].lower() == strategy_data.get("exchange", "MEXC").lower()), None)
            if not api_key_data:
                raise ValueError(f"No API key found for exchange {strategy_data.get('exchange', 'MEXC')}")

            exchange_class = getattr(ccxt, strategy_data.get("exchange", "MEXC").lower())
            exchange = exchange_class({
                "apiKey": api_key_data["api_key"],
                "secret": api_key_data["api_secret"],
                "password": api_key_data.get("passphrase", ""),
                "rateLimit": api_key_data.get("rate_limit_requests", 1800),
                "timeout": api_key_data.get("timeout_seconds", 30) * 1000
            })

            # Validate symbol and interval
            normalized_symbol = await self.validate_symbol_and_interval(exchange, normalized_symbol, normalized_interval)
            await self.synchronize_time(exchange, strategy_data.get("exchange", "MEXC"), max_time_diff_ms=10000)

            # Main Paper Trading loop
            while True:
                # Check strategy mode
                with open(strategies_file, "r", encoding="utf-8-sig") as f:
                    strategies = json.load(f)
                strategy_data = next((s for s in strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
                if not strategy_data or strategy_data["mode"] != "Paper":
                    logging.info(f"Stopping paper trading for {strategy_name} as mode is {strategy_data.get('mode', 'unknown') if strategy_data else 'not found'}")
                    break

                # Fetch OHLCV data
                ohlcv = await exchange.fetch_ohlcv(normalized_symbol, normalized_interval, limit=2)
                if not ohlcv or len(ohlcv) < 2:
                    logging.warning(f"No sufficient OHLCV data for {normalized_symbol} on {normalized_interval}, trying fallback")
                    df = self.load_fallback_ohlcv(normalized_symbol, normalized_interval)
                    if df is None or df.empty:
                        logging.error(f"No sufficient OHLCV data for {normalized_symbol} on {normalized_interval}")
                        await asyncio.sleep(60)
                        continue
                else:
                    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

                # Generate indicators and signal
                indicators = strategy_instance.get_indicators(df)
                if not indicators or not isinstance(indicators, list) or not indicators[0]:
                    logging.error(f"No valid indicators for strategy {strategy_name}")
                    await asyncio.sleep(60)
                    continue

                for indicator in indicators[0]:
                    df[indicator] = indicators[0][indicator]

                signal = strategy_instance.get_signal(df.iloc[[-1]])
                logging.debug(f"Generated signal for {strategy_name} on {normalized_symbol}: {signal}")

                # Simulate trades
                if signal == "buy" and position == 0:
                    position = capital / df["close"].iloc[-1]
                    entry_price = df["close"].iloc[-1]
                    trades.append({
                        "type": "buy",
                        "price": entry_price,
                        "timestamp": df["timestamp"].iloc[-1].isoformat(),
                        "profit_usd": 0,
                        "duration_minutes": 0
                    })
                    logging.info(f"Paper buy trade at {entry_price} for {strategy_name} on {normalized_symbol}")
                elif signal == "sell" and position > 0:
                    exit_price = df["close"].iloc[-1]
                    trade_profit = position * (exit_price - entry_price)
                    profit += trade_profit
                    capital += trade_profit
                    position = 0
                    trades.append({
                        "type": "sell",
                        "price": exit_price,
                        "timestamp": df["timestamp"].iloc[-1].isoformat(),
                        "profit_usd": trade_profit,
                        "duration_minutes": (df["timestamp"].iloc[-1] - pd.to_datetime(trades[-1]["timestamp"])).total_seconds() / 60
                    })
                    max_profit = max(max_profit, profit)
                    logging.info(f"Paper sell trade at {exit_price} for {strategy_name} on {normalized_symbol}")
                equity_curve.append(capital)

                # Calculate statistics
                equity_series = pd.Series(equity_curve)
                rolling_max = equity_series.cummax()
                drawdown = equity_series - rolling_max
                max_dd = drawdown.min()
                total_trades = len(trades) // 2
                winning_trades = sum(1 for i in range(1, len(trades), 2) if trades[i]["price"] > trades[i-1]["price"])
                winrate_pct = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                positive_profits = sum(trades[i]["price"] - trades[i-1]["price"] for i in range(1, len(trades), 2) if trades[i]["price"] > trades[i-1]["price"])
                negative_profits = abs(sum(trades[i]["price"] - trades[i-1]["price"] for i in range(1, len(trades), 2) if trades[i]["price"] < trades[i-1]["price"]))
                profit_factor = positive_profits / negative_profits if negative_profits > 0 else (0 if positive_profits == 0 else "inf")

                # Save results
                result = {
                    "strategy": strategy_name,
                    "symbol": normalized_symbol,
                    "days_active": (datetime.now(tz=ZoneInfo("Europe/Warsaw")) - start_time).days,
                    "net_profit_usd": profit,
                    "max_drawdown_usd": max_dd,
                    "max_profit_usd": max_profit,
                    "total_trades": total_trades,
                    "total_transactions": len(trades),
                    "winrate_pct": winrate_pct,
                    "profit_factor": profit_factor,
                    "signals": [signal] if signal else [],
                    "close": [df["close"].iloc[-1]]
                }

                simulations_dir = Path(__file__).resolve().parents[2] / "simulations" / strategy_name / normalized_symbol
                self.results_handler.save_simulation_results(
                    base_dir=simulations_dir,
                    strategy_name=strategy_name,
                    symbol=normalized_symbol,
                    trades=trades,
                    open_trades=[] if position == 0 else [{"type": "buy", "price": entry_price, "timestamp": trades[-1]["timestamp"]}],
                    total_profit=profit,
                    total_trades=total_trades,
                    winning_trades=winning_trades,
                    avg_max_dd=max_dd,
                    initial_capital=initial_capital,
                    start_time_sim=start_time,
                    df=df
                )

                # Wait for the next interval
                await asyncio.sleep(60)

            await exchange.close()
            logging.info(f"Paper trading completed for {strategy_name} on {normalized_symbol}")
            return result

        except asyncio.CancelledError:
            logging.info(f"Paper trading cancelled for {strategy_name} on {normalized_symbol}")
            if "exchange" in locals():
                await exchange.close()
            raise
        except Exception as e:
            self.error_handler.log_error("Paper trading", f"Error in paper trading for {strategy_name} on {normalized_symbol}: {str(e)}")
            if "exchange" in locals():
                await exchange.close()
            raise

    def start_simulation(self, strategy_name: str, symbol: str, interval: str, mode: str = "simulations", limit: int = 1000) -> dict:
        """Starts a Paper Trading simulation.

        Args:
            strategy_name (str): Name of the strategy.
            symbol (str): Trading symbol.
            interval (str): Time interval.
            mode (str): Simulation mode ('simulations' by default).
            limit (int): Limit of candles (used only for historical data).

        Returns:
            dict: Simulation results.
        """
        try:
            normalized_symbol = normalize_symbol(symbol)
            normalized_interval = normalize_interval(interval)
            if not self.loop.is_running():
                loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
                loop_thread.start()
                logging.info("Started asyncio event loop in separate thread")
            return asyncio.run_coroutine_threadsafe(self.paper_trade(strategy_name, normalized_symbol, normalized_interval, mode), self.loop).result()
        except Exception as e:
            self.error_handler.log_error("Starting paper trading", f"Error starting paper trading for {strategy_name} on {normalized_symbol}: {str(e)}")
            raise

    def load_fallback_ohlcv(self, symbol: str, interval: str) -> pd.DataFrame:
        """Loads fallback OHLCV data from fallback_ohlcv.json.

        Args:
            symbol (str): Trading symbol.
            interval (str): Time interval.

        Returns:
            pd.DataFrame: DataFrame with OHLCV data or None if error occurs.
        """
        try:
            normalized_symbol = normalize_symbol(symbol)
            normalized_interval = normalize_interval(interval)
            fallback_file = Path(__file__).resolve().parents[2] / "data" / "fallback_ohlcv.json"
            if not fallback_file.exists():
                logging.warning(f"No fallback_ohlcv.json file found for {normalized_symbol} on {normalized_interval}")
                return None
            with open(fallback_file, "r", encoding="utf-8") as f:
                ohlcv_data = json.load(f)
            symbol_normalized = normalized_symbol.replace('/', '_')
            ohlcv_symbol_data = ohlcv_data.get(symbol_normalized, {}).get(normalized_interval, [])
            if not ohlcv_symbol_data:
                logging.warning(f"No OHLCV data for {normalized_symbol} on {normalized_interval} in fallback_ohlcv.json")
                return None
            df = pd.DataFrame(ohlcv_symbol_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            logging.info(f"Loaded fallback OHLCV data for {normalized_symbol} on {normalized_interval}")
            return df
        except Exception as e:
            self.error_handler.log_error("Loading fallback OHLCV", f"Error loading fallback OHLCV data for {normalized_symbol} on {normalized_interval}: {str(e)}")
            return None