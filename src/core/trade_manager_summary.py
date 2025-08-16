# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager_summary.py
import logging
import json
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from src.core.trade_manager_base import TradeManagerBase
from src.tabs.czacha_data import CzachaData

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TradeManagerSummary(TradeManagerBase):
    """Class responsible for generating summaries of trading results."""

    def __init__(self):
        super().__init__()
        self.czacha_data = CzachaData()

    def generate_summary(self, strategy_name, symbol, trades, mode="simulations"):
        """Generates a summary of trading results.

        Args:
            strategy_name (str): Name of the strategy.
            symbol (str): Trading symbol.
            trades (list): List of trades.
            mode (str): Mode of operation ('simulations' by default).

        Returns:
            dict: Summary of trading results.
        """
        try:
            # Load initial capital from czacha.json
            czacha_data = self.czacha_data.load_data()
            strategy_data = next((s for s in czacha_data["strategies"] if s["name"] == strategy_name and s["symbol"] == symbol), None)
            initial_capital = strategy_data["start_capital"] if strategy_data else 1000.0
            capital = initial_capital
            profit = 0
            max_dd = 0
            max_profit = 0
            equity_curve = [initial_capital]
            
            for i in range(1, len(trades), 2):
                if i < len(trades):
                    buy_price = trades[i-1]["price"]
                    sell_price = trades[i]["price"]
                    trade_profit = (sell_price - buy_price) * (capital / buy_price)
                    profit += trade_profit
                    capital += trade_profit
                    equity_curve.append(capital)
                    max_profit = max(max_profit, profit)
            
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
            
            summary = {
                "strategy": strategy_name,
                "symbol": symbol,
                "days_active": (datetime.now(tz=ZoneInfo("Europe/Warsaw")) - pd.to_datetime(trades[0]["timestamp"])).days if trades else 0,
                "net_profit_usd": profit,
                "max_drawdown_usd": max_dd,
                "max_profit_usd": max_profit,
                "total_trades": total_trades,
                "total_transactions": len(trades),
                "winrate_pct": winrate_pct,
                "profit_factor": profit_factor
            }
            
            summary_file = Path(__file__).resolve().parents[2] / mode / strategy_name / symbol.replace('/', '_') / "summary.json"
            summary_file.parent.mkdir(parents=True, exist_ok=True)
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Generated summary for {strategy_name} on {symbol} in mode {mode}")
            return summary
        except Exception as e:
            logging.error(f"Error generating summary for {strategy_name} on {symbol}: {str(e)}", exc_info=True)
            raise