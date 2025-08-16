# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\strategies\strategies_backtest.py
import logging
import json
import pandas as pd
import importlib.util
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import ccxt.async_support as ccxt
from src.core.trade_manager_fallback import TradeManagerFallback
from src.core.trade_manager_results_handler import TradeManagerResultsHandler
from src.core.trade_manager_summary import TradeManagerSummary
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

async def run_backtest(strategy_name, symbol, period=8760, interval="1h"):
    """Runs a backtest for the specified strategy and symbol.

    Args:
        strategy_name (str): Name of the strategy.
        symbol (str): Trading symbol.
        period (int): Number of candles to fetch (default: 8760).
        interval (str): Time interval (default: '1h').

    Returns:
        dict: Backtest results.
    """
    try:
        logging.info(f"Starting backtest for strategy {strategy_name} on {symbol} with period {period} and interval {interval}")
        czacha_data = CzachaData()
        strategies_file = Path(__file__).resolve().parents[3] / "data" / "strategies.json"
        with open(strategies_file, "r", encoding="utf-8-sig") as f:
            strategies = json.load(f)
        strategy_data = next((s for s in strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
        if not strategy_data:
            logging.error(f"Strategy {strategy_name} with symbol {symbol} not found")
            raise ValueError(f"Strategy {strategy_name} with symbol {symbol} not found")
        
        file_path = strategy_data.get("file_path")
        if not file_path:
            logging.error(f"No file path for strategy {strategy_name}")
            raise ValueError(f"No file path for strategy {strategy_name}")
        if not Path(file_path).exists():
            logging.error(f"File path {file_path} does not exist for strategy {strategy_name}")
            raise ValueError(f"File path {file_path} does not exist")
        
        spec = importlib.util.spec_from_file_location(strategy_name, file_path)
        if spec is None:
            logging.error(f"Invalid file path for strategy {strategy_name}: {file_path}")
            raise ValueError(f"Invalid file path for strategy {strategy_name}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        strategy = getattr(module, "Strategy", None)
        if not strategy:
            logging.error(f"No Strategy class in {file_path}")
            raise ValueError(f"No Strategy class in {file_path}")
        
        strategy_instance = strategy()
        strategy_instance.update_indicators(strategy_data.get("parameters", {}))
        
        trade_manager_fallback = TradeManagerFallback()
        trade_manager_results = TradeManagerResultsHandler()
        trade_manager_summary = TradeManagerSummary()
        
        api_keys_file = Path(__file__).resolve().parents[3] / "data" / "api_keys.json"
        api_keys = [{"exchange": "mexc", "api_key": "", "api_secret": "", "passphrase": "", "rate_limit_requests": 1800, "timeout_seconds": 30}]
        if api_keys_file.exists():
            with open(api_keys_file, "r", encoding="utf-8-sig") as f:
                api_keys = json.load(f)
        
        api_key_data = next((key for key in api_keys if key["exchange"].lower() == strategy_data.get("exchange", "MEXC").lower()), None)
        if not api_key_data:
            logging.error(f"No API key found for exchange {strategy_data.get('exchange', 'MEXC')}")
            raise ValueError(f"No API key found for exchange {strategy_data.get('exchange', 'MEXC')}")
        
        exchange_class = getattr(ccxt, strategy_data.get("exchange", "MEXC").lower())
        exchange = exchange_class({
            "apiKey": api_key_data["api_key"],
            "secret": api_key_data["api_secret"],
            "password": api_key_data.get("passphrase", ""),
            "rateLimit": api_key_data.get("rate_limit_requests", 1800),
            "timeout": api_key_data.get("timeout_seconds", 30) * 1000
        })
        
        normalized_symbol = normalize_symbol(symbol)
        normalized_interval = normalize_interval(interval)
        await trade_manager_fallback.synchronize_time(exchange, strategy_data.get("exchange", "MEXC"))
        
        try:
            ohlcv = await exchange.fetch_ohlcv(normalized_symbol, normalized_interval, limit=period)
        except Exception as e:
            logging.warning(f"Failed to fetch OHLCV data for {symbol} on {interval}: {str(e)}, using fallback data")
            df = trade_manager_fallback.load_fallback_ohlcv(symbol, interval)
            if df is None:
                logging.error(f"No fallback OHLCV data available for {symbol} on {interval}")
                raise ValueError(f"No OHLCV data available for {symbol}")
        else:
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        indicators = strategy_instance.get_indicators(df)
        if not indicators:
            logging.error(f"No indicators returned for strategy {strategy_name}")
            raise ValueError(f"No indicators returned for strategy {strategy_name}")
        if not isinstance(indicators, list) or not indicators or not isinstance(indicators[0], dict):
            logging.error(f"Invalid indicators format for strategy {strategy_name}")
            raise ValueError(f"Invalid indicators format for strategy {strategy_name}")
        
        for indicator in indicators[0]:
            df[indicator] = indicators[0][indicator]
        signals = []
        for i in range(len(df)):
            signal = strategy_instance.get_signal(df.iloc[[i]])
            signals.append(signal)
        df["signals"] = signals
        
        # Load initial capital from czacha.json
        czacha_data = czacha_data.load_data()
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
        
        for i in range(1, len(df)):
            if signals[i] == "buy" and position == 0:
                position = capital / df["close"].iloc[i]
                entry_price = df["close"].iloc[i]
                trades.append({"type": "buy", "price": entry_price, "timestamp": df["timestamp"].iloc[i].isoformat()})
            elif signals[i] == "sell" and position > 0:
                exit_price = df["close"].iloc[i]
                trade_profit = position * (exit_price - entry_price)
                profit += trade_profit
                capital += trade_profit
                position = 0
                trades.append({"type": "sell", "price": exit_price, "timestamp": df["timestamp"].iloc[i].isoformat()})
                max_profit = max(max_profit, profit)
            equity_curve.append(capital)
        
        equity_series = pd.Series(equity_curve)
        rolling_max = equity_series.cummax()
        drawdown = equity_series - rolling_max
        max_dd = drawdown.min()
        max_dd_percentage = (max_dd / initial_capital) * 100 if max_dd < 0 else 0.0
        
        result = {
            "strategy": strategy_name,
            "symbol": normalized_symbol,
            "days": (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).days,
            "profit": profit,
            "profit_percentage": (profit / initial_capital) * 100,
            "max_dd_percentage": max_dd_percentage,
            "total_trades": len(trades) // 2,
            "total_transactions": len(trades),
            "win_rate_percentage": (sum(1 for i, t in enumerate(trades[1::2]) if t["price"] > trades[i*2]["price"]) / (len(trades) // 2)) * 100 if trades else 0,
            "avg_profit_percentage": (profit / (len(trades) // 2) / initial_capital) * 100 if trades else 0,
            "profit_factor": sum(t["price"] - trades[i*2]["price"] for i, t in enumerate(trades[1::2]) if t["price"] > trades[i*2]["price"]) / abs(sum(t["price"] - trades[i*2]["price"] for i, t in enumerate(trades[1::2]) if t["price"] < trades[i*2]["price"])) if any(t["price"] < trades[i*2]["price"] for i, t in enumerate(trades[1::2])) else "inf",
            "signals": signals,
            "data": df.to_dict(orient="records"),
            "indicators": list(indicators[0].keys()) if indicators else [],
            "parameters": strategy_data.get("parameters", {}),
            "trades": trades
        }
        
        backtest_dir = Path(__file__).resolve().parents[3] / "backtests" / strategy_name / normalized_symbol
        backtest_dir.mkdir(parents=True, exist_ok=True)
        trade_manager_results.save_simulation_results(backtest_dir, strategy_name, symbol, trades, [], profit, len(trades) // 2, sum(1 for i, t in enumerate(trades[1::2]) if t["price"] > trades[i*2]["price"]), max_dd_percentage, initial_capital, df["timestamp"].iloc[0], df)
        trade_manager_summary.generate_summary(strategy_name, symbol, trades, mode="backtests")
        
        await exchange.close()
        logging.info(f"Backtest completed for {strategy_name} on {symbol}, results saved")
        return result
    except Exception as e:
        logging.error(f"Error in backtest for {strategy_name} on {symbol}: {str(e)}", exc_info=True)
        if "exchange" in locals():
            await exchange.close()
        raise