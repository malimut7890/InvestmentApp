# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager_live.py
import logging
import json
import ccxt.async_support as ccxt
import pandas as pd
import importlib.util
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import asyncio
from src.core.trade_manager_base import TradeManagerBase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TradeManagerLive(TradeManagerBase):
    def __init__(self):
        super().__init__()
        self.strategies = {}
        self.active_trades = {}

    async def start_live_trading(self, strategy_name, symbol, interval):
        try:
            logging.info(f"Starting live trading for strategy {strategy_name} on {symbol} with interval {interval}")
            strategies_file = Path(__file__).resolve().parents[2] / "data" / "strategies.json"
            with open(strategies_file, "r", encoding="utf-8-sig") as f:
                strategies = json.load(f)
            strategy_data = next((s for s in strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
            if not strategy_data:
                logging.error(f"Strategy {strategy_name} with symbol {symbol} not found")
                raise ValueError(f"Strategy {strategy_name} with symbol {symbol} not found")
            
            file_path = strategy_data.get("file_path")
            if not file_path or not Path(file_path).exists():
                logging.error(f"No valid file path for strategy {strategy_name}: {file_path}")
                raise ValueError(f"No valid file path for strategy {strategy_name}")
            
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
            
            await self.synchronize_time(exchange, strategy_data.get("exchange", "MEXC"))
            
            start_time = datetime.now(tz=ZoneInfo("Europe/Warsaw"))
            initial_capital = 1000.0
            capital = initial_capital
            position = 0
            entry_price = 0
            profit = 0
            max_dd = 0
            max_profit = 0
            equity_curve = [initial_capital]
            trades = []
            
            while True:
                with open(strategies_file, "r", encoding="utf-8-sig") as f:
                    strategies = json.load(f)
                strategy_data = next((s for s in strategies if s["name"] == strategy_name and s["symbol"] == symbol), None)
                if not strategy_data or strategy_data["mode"] != "Live":
                    logging.info(f"Stopping live trading for {strategy_name} as mode is {strategy_data.get('mode', 'unknown') if strategy_data else 'not found'}")
                    break
                
                ohlcv = await exchange.fetch_ohlcv(symbol, interval, limit=2)
                if not ohlcv or len(ohlcv) < 2:
                    logging.error(f"No sufficient OHLCV data for {symbol} on {interval}")
                    await asyncio.sleep(60)
                    continue
                
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                if df.empty:
                    logging.warning(f"Empty OHLCV DataFrame for {symbol} on {interval}")
                    continue
                
                indicators = strategy_instance.get_indicators(df)
                if not indicators or not isinstance(indicators, list) or not indicators[0]:
                    logging.warning(f"No valid indicators for strategy {strategy_name} on {symbol}")
                    await asyncio.sleep(60)
                    continue
                
                for indicator in indicators[0]:
                    df[indicator] = indicators[0][indicator]
                
                signal = strategy_instance.get_signal(df.iloc[[-1]])
                logging.debug(f"Signal for {strategy_name} on {symbol}: {signal}")
                
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
                    logging.info(f"Live buy order placed for {strategy_name} on {symbol} at {entry_price}")
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
                    logging.info(f"Live sell order placed for {strategy_name} on {symbol} at {exit_price}")
                equity_curve.append(capital)
                
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
                
                result = {
                    "strategy": strategy_name,
                    "symbol": symbol,
                    "days_active": (datetime.now(tz=ZoneInfo("Europe/Warsaw")) - start_time).days,
                    "net_profit_usd": profit,
                    "max_drawdown_usd": max_dd,
                    "max_profit_usd": max_profit,
                    "total_trades": total_trades,
                    "total_transactions": len(trades),
                    "winrate_pct": winrate_pct,
                    "profit_factor": profit_factor
                }
                
                live_dir = Path(__file__).resolve().parents[2] / "live" / strategy_name / symbol.replace('/', '_')
                live_dir.mkdir(parents=True, exist_ok=True)
                trades_file = live_dir / "trades.json"
                with open(trades_file, "a", encoding="utf-8") as f:
                    for trade in trades:
                        json.dump(trade, f, ensure_ascii=False)
                        f.write("\n")
                
                summary_file = live_dir / "summary.json"
                with open(summary_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                await asyncio.sleep(60)
            
            await exchange.close()
            logging.info(f"Live trading stopped for {strategy_name} on {symbol}")
            return result
        except Exception as e:
            logging.error(f"Error in live trading for {strategy_name} on {symbol}: {str(e)}", exc_info=True)
            if "exchange" in locals():
                await exchange.close()
            raise