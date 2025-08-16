# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\core\trade_manager_results_handler.py
import logging
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
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

class TradeManagerResultsHandler(TradeManagerBase):
    def save_simulation_results(self, strategy_name, symbol, results, mode="simulations"):
        try:
            sim_dir = Path(__file__).resolve().parents[2] / mode / strategy_name / symbol.replace('/', '_')
            sim_dir.mkdir(parents=True, exist_ok=True)
            
            # Save trades to JSONL
            trades_file = sim_dir / "trades.json"
            with open(trades_file, "a", encoding="utf-8") as f:
                for trade in results.get("trades", []):
                    json.dump(trade, f, ensure_ascii=False)
                    f.write("\n")
            
            # Save summary
            summary_file = sim_dir / "summary.json"
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Save to monthly file
            monthly_file = sim_dir / f"{datetime.now().strftime('%Y%m')}.json"
            with open(monthly_file, "a", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False)
                f.write("\n")
            
            logging.info(f"Saved simulation results for {strategy_name} on {symbol} to {summary_file}")
        except Exception as e:
            logging.error(f"Error saving simulation results for {strategy_name} on {symbol}: {str(e)}", exc_info=True)
            raise