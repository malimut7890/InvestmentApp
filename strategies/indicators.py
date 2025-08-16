# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\strategies\indicators.py
import importlib.util
import logging
import os
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log", encoding="utf-8"),
        logging.FileHandler("C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# Konfiguracja handlera dla error.log (tylko błędy)
error_handler = logging.getLogger('').handlers[1]
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s | Traceback: %(exc_info)s"))

def get_strategy_indicators(strategy_name, file_path=None):
    """Return the indicators defined in the strategy file."""
    try:
        if file_path is None:
            logging.warning(f"No file path provided for strategy {strategy_name}, assuming default indicators")
            return {}
        
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        if base_name != strategy_name and not strategy_name.startswith(base_name):
            logging.warning(f"Strategy name {strategy_name} does not match file base name {base_name}, using file base name")
            strategy_name = base_name
        
        spec = importlib.util.spec_from_file_location(strategy_name, file_path)
        if spec is None:
            logging.error(f"Failed to create spec for strategy file {file_path}", exc_info=True)
            return {}
        strategy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(strategy_module)
        
        # Sprawdź, czy strategia zawiera klasę Strategy
        if not hasattr(strategy_module, "Strategy"):
            logging.error(f"Strategy file {file_path} does not contain a Strategy class", exc_info=True)
            return {}
        
        strategy_instance = strategy_module.Strategy()
        
        # Zwraca parametry zdefiniowane w strategii
        if hasattr(strategy_instance, "parameters"):
            logging.info(f"Loaded parameters for strategy {strategy_name}: {strategy_instance.parameters}")
            return strategy_instance.parameters
        
        # Domyślne parametry dla znanych strategii
        if strategy_name.startswith("strategy_dual_ma"):
            logging.info(f"No parameters defined in strategy {strategy_name}, using default Dual MA parameters")
            return {
                "fast_ema_period": 12,
                "slow_ema_period": 26,
                "adx_period": 14,
                "adx_threshold": 25
            }
        elif strategy_name.startswith("strategy_test"):
            logging.info(f"No parameters defined in strategy {strategy_name}, using default test parameters")
            return {
                "signal_alternate": True
            }
        else:
            logging.warning(f"No parameters defined for strategy {strategy_name}, returning empty dict")
            return {}
    except Exception as e:
        logging.error(f"Error loading indicators for strategy {strategy_name} from {file_path}: {str(e)}", exc_info=True)
        return {}