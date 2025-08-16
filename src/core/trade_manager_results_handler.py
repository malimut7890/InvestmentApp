# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager_results_handler.py

import logging
import json
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from src.core.trade_manager_base import TradeManagerBase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class TradeManagerResultsHandler(TradeManagerBase):
    """Klasa odpowiedzialna za zapisywanie wyników symulacji i backtestów.

    Metody:
        save_simulation_results: Zapisuje wyniki symulacji do plików trades.json, open_trades.json, summary.json i miesięcznych raportów.
    """

    def save_simulation_results(self, base_dir: Path, strategy_name: str, symbol: str, trades: list, open_trades: list, total_profit: float, total_trades: int, winning_trades: int, avg_max_dd: float, initial_capital: float, start_time_sim: datetime, df: pd.DataFrame) -> None:
        """Zapisuje wyniki symulacji do odpowiednich plików.

        Args:
            base_dir (Path): Katalog docelowy dla zapisu wyników.
            strategy_name (str): Nazwa strategii.
            symbol (str): Symbol handlowy (np. BTC/USDT).
            trades (list): Lista zamkniętych transakcji.
            open_trades (list): Lista otwartych transakcji.
            total_profit (float): Całkowity zysk z symulacji.
            total_trades (int): Liczba zamkniętych transakcji.
            winning_trades (int): Liczba zwycięskich transakcji.
            avg_max_dd (float): Średni maksymalny spadek (drawdown).
            initial_capital (float): Początkowy kapitał.
            start_time_sim (datetime): Czas rozpoczęcia symulacji.
            df (pd.DataFrame): DataFrame z danymi OHLCV.

        Raises:
            Exception: W przypadku błędu zapisu do pliku.
        """
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
            # Test zapisu do pliku
            test_file = base_dir / "test_write.txt"
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("test")
            os.remove(test_file)
            
            # Zapis zamkniętych transakcji
            trades_file = base_dir / "trades.json"
            with open(trades_file, "w", encoding="utf-8") as f:
                for trade in trades:
                    json.dump(trade, f, ensure_ascii=False)
                    f.write("\n")
            logging.info(f"Zapisano {len(trades)} zamkniętych transakcji do {trades_file}")
            
            # Zapis otwartych transakcji
            open_trades_file = base_dir / "open_trades.json"
            with open(open_trades_file, "w", encoding="utf-8") as f:
                json.dump({"open_trades": open_trades}, f, indent=4, ensure_ascii=False)
            logging.info(f"Zapisano {len(open_trades)} otwartych transakcji do {open_trades_file}")
            
            # Obliczanie statystyk
            total_transactions = len(trades) + len(open_trades)
            winning_trades = sum(1 for t in trades if t.get("profit_usd", 0) > 0)
            total_profit = sum(t.get("profit_usd", 0) for t in trades)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            positive_profits = sum(t["profit_usd"] for t in trades if "profit_usd" in t and t["profit_usd"] > 0)
            negative_profits = abs(sum(t["profit_usd"] for t in trades if "profit_usd" in t and t["profit_usd"] < 0))
            profit_factor = positive_profits / negative_profits if negative_profits > 0 else (0 if positive_profits == 0 else float("inf"))
            avg_profit = (total_profit / total_trades) if total_trades > 0 else 0
            max_drawdown_usd = min([t["profit_usd"] for t in trades if "profit_usd" in t], default=0)
            max_profit_usd = max([t["profit_usd"] for t in trades if "profit_usd" in t], default=0)
            total_duration_minutes = sum(t["duration_minutes"] for t in trades if "duration_minutes" in t)
            average_duration_minutes = total_duration_minutes / total_trades if total_trades > 0 else 0
            
            # Obliczanie dni aktywności
            active_file = base_dir.parent.parent.parent / "data" / "active_strategies.json"
            if active_file.exists() and trades:
                with open(active_file, "r", encoding="utf-8") as f:
                    active_data = json.load(f)
                key = f"{strategy_name}_{symbol}"
                if key in active_data:
                    start_date = datetime.fromisoformat(active_data[key]["start_date"]).replace(tzinfo=ZoneInfo("Europe/Warsaw"))
                    days = (datetime.now(tz=ZoneInfo("Europe/Warsaw")).date() - start_date.date()).days
                else:
                    days = (df["timestamp"].iloc[-1] - datetime.fromisoformat(trades[0]["timestamp"]).replace(tzinfo=ZoneInfo("Europe/Warsaw"))).days if trades else 0
            else:
                days = (df["timestamp"].iloc[-1] - datetime.fromisoformat(trades[0]["timestamp"]).replace(tzinfo=ZoneInfo("Europe/Warsaw"))).days if trades else 0
            profit_percentage = (total_profit / initial_capital) * 100 if initial_capital > 0 else 0
            
            # Zapis wyników miesięcznych
            timestamp = datetime.now(tz=ZoneInfo("Europe/Warsaw")).strftime("%Y%m")
            monthly_file = base_dir / f"{timestamp}.json"
            month_trades = []
            if monthly_file.exists():
                with open(monthly_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    month_trades = existing_data.get("trades", [])
                month_trades = [t for t in month_trades if pd.to_datetime(t.get("timestamp", t.get("entry_time", ""))) >= df["timestamp"].iloc[0]]
            
            month_trades.extend([t for t in trades if t not in month_trades and pd.to_datetime(t.get("timestamp", t.get("entry_time", ""))) >= df["timestamp"].iloc[0]])
            
            monthly_results = {
                "strategy": strategy_name,
                "symbol": symbol,
                "trades": month_trades,
                "days": days,
                "total_trades": total_trades,
                "total_transactions": total_transactions,
                "win_rate_percentage": win_rate,
                "avg_profit_percentage": avg_profit / initial_capital * 100 if total_trades > 0 else 0,
                "avg_max_dd_percentage": avg_max_dd,
                "profit_factor": float(profit_factor) if profit_factor != float("inf") else "inf",
                "profit_percentage": profit_percentage,
                "total_profit": total_profit
            }
            with open(monthly_file, "w", encoding="utf-8") as f:
                json.dump(monthly_results, f, indent=4, ensure_ascii=False)
            logging.info(f"Zapisano wyniki miesięczne do {monthly_file}")
            
            # Zapis podsumowania
            summary_file = base_dir / "summary.json"
            summary_data = {
                "strategy": strategy_name,
                "symbol": symbol,
                "days_active": days,
                "total_trades": total_trades,
                "wins": winning_trades,
                "losses": total_trades - winning_trades,
                "winrate_pct": win_rate,
                "net_profit_usd": total_profit,
                "max_drawdown_usd": max_drawdown_usd,
                "max_profit_usd": max_profit_usd,
                "profit_factor": float(profit_factor) if profit_factor != float("inf") else "inf",
                "average_duration_minutes": average_duration_minutes,
                "total_duration_minutes": total_duration_minutes,
                "last_updated": datetime.now(tz=ZoneInfo("Europe/Warsaw")).isoformat()
            }
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=4, ensure_ascii=False)
            logging.info(f"Zapisano podsumowanie do {summary_file}")
        except Exception as e:
            error_file = base_dir / "errors.log"
            with open(error_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now(tz=ZoneInfo('Europe/Warsaw')).isoformat()}: Błąd zapisu wyników symulacji: {str(e)}\n")
            logging.error(f"Błąd zapisu wyników symulacji do {base_dir}: {str(e)}")
            raise