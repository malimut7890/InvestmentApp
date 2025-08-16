# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\tabs\promotion.py
import tkinter as tk
from tkinter import ttk
import json
import os
import logging
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    filename="C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\app.log",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    filemode="w"
)

class PromotionTab:
    def __init__(self, frame):
        try:
            self.frame = frame
            self.promotion_data = self.load_promotion_data()
            
            # Sekcja ustawień ogólnych (Awans)
            self.fields_frame = ttk.LabelFrame(self.frame, text="Ustawienia Awansu")
            self.fields_frame.pack(pady=10, padx=10, fill="x")
            
            tk.Label(self.fields_frame, text="Dni:").pack(anchor="w", padx=5)
            self.days_var = tk.StringVar(value=str(self.promotion_data.get("days", 7)))
            self.days_entry = ttk.Entry(self.fields_frame, textvariable=self.days_var, width=10)
            self.days_entry.pack(anchor="w", padx=5)
            self.days_error = tk.Label(self.fields_frame, text="", foreground="red")
            self.days_error.pack(anchor="w", padx=5)
            
            tk.Label(self.fields_frame, text="Próg awansu %:").pack(anchor="w", padx=5)
            self.promotion_threshold_var = tk.StringVar(value=str(self.promotion_data.get("promotion_threshold", 100)))
            self.promotion_threshold_entry = ttk.Entry(self.fields_frame, textvariable=self.promotion_threshold_var, width=10)
            self.promotion_threshold_entry.pack(anchor="w", padx=5)
            self.promotion_threshold_error = tk.Label(self.fields_frame, text="", foreground="red")
            self.promotion_threshold_error.pack(anchor="w", padx=5)
            
            tk.Label(self.fields_frame, text="Stopień awansu %:").pack(anchor="w", padx=5)
            self.promotion_increment_var = tk.StringVar(value=str(self.promotion_data.get("promotion_increment", 0.2)))
            self.promotion_increment_entry = ttk.Entry(self.fields_frame, textvariable=self.promotion_increment_var, width=10)
            self.promotion_increment_entry.pack(anchor="w", padx=5)
            self.promotion_increment_error = tk.Label(self.fields_frame, text="", foreground="red")
            self.promotion_increment_error.pack(anchor="w", padx=5)
            
            tk.Label(self.fields_frame, text="Max % awans:").pack(anchor="w", padx=5)
            self.max_trade_percent_var = tk.StringVar(value=str(self.promotion_data.get("max_trade_percent", 5)))
            self.max_trade_percent_entry = ttk.Entry(self.fields_frame, textvariable=self.max_trade_percent_var, width=10)
            self.max_trade_percent_entry.pack(anchor="w", padx=5)
            self.max_trade_percent_error = tk.Label(self.fields_frame, text="", foreground="red")
            self.max_trade_percent_error.pack(anchor="w", padx=5)
            
            tk.Label(self.fields_frame, text="Próg degradacji %:").pack(anchor="w", padx=5)
            self.demotion_threshold_var = tk.StringVar(value=str(self.promotion_data.get("demotion_threshold", 20)))
            self.demotion_threshold_entry = ttk.Entry(self.fields_frame, textvariable=self.demotion_threshold_var, width=10)
            self.demotion_threshold_entry.pack(anchor="w", padx=5)
            self.demotion_threshold_error = tk.Label(self.fields_frame, text="", foreground="red")
            self.demotion_threshold_error.pack(anchor="w", padx=5)
            
            tk.Label(self.fields_frame, text="Stopień degradacji %:").pack(anchor="w", padx=5)
            self.demotion_decrement_var = tk.StringVar(value=str(self.promotion_data.get("demotion_decrement", 0.25)))
            self.demotion_decrement_entry = ttk.Entry(self.fields_frame, textvariable=self.demotion_decrement_var, width=10)
            self.demotion_decrement_entry.pack(anchor="w", padx=5)
            self.demotion_decrement_error = tk.Label(self.fields_frame, text="", foreground="red")
            self.demotion_decrement_error.pack(anchor="w", padx=5)
            
            ttk.Button(self.fields_frame, text="Zapisz", command=self.save_promotion_data).pack(pady=10)
            
            # Sekcja trybu Auto
            self.auto_frame = ttk.LabelFrame(self.frame, text="Ustawienia Trybu Auto")
            self.auto_frame.pack(pady=10, padx=10, fill="x")
            
            tk.Label(self.auto_frame, text="Ilość dni trybu:").pack(anchor="w", padx=5)
            self.auto_days_var = tk.StringVar(value=str(self.promotion_data.get("auto_settings", {}).get("auto_days", 7)))
            self.auto_days_entry = ttk.Entry(self.auto_frame, textvariable=self.auto_days_var, width=10)
            self.auto_days_entry.pack(anchor="w", padx=5)
            self.auto_days_error = tk.Label(self.auto_frame, text="", foreground="red")
            self.auto_days_error.pack(anchor="w", padx=5)
            
            tk.Label(self.auto_frame, text="Konieczny zysk %:").pack(anchor="w", padx=5)
            self.required_profit_var = tk.StringVar(value=str(self.promotion_data.get("auto_settings", {}).get("required_profit", 50)))
            self.required_profit_entry = ttk.Entry(self.auto_frame, textvariable=self.required_profit_var, width=10)
            self.required_profit_entry.pack(anchor="w", padx=5)
            self.required_profit_error = tk.Label(self.auto_frame, text="", foreground="red")
            self.required_profit_error.pack(anchor="w", padx=5)
            
            ttk.Button(self.auto_frame, text="Zapisz", command=self.save_auto_settings).pack(pady=10)
            
            logging.debug("PromotionTab zainicjalizowany")
        except Exception as e:
            logging.error(f"Błąd inicjalizacji PromotionTab: {str(e)}")

    def load_promotion_data(self):
        data_dir = "C:\\Users\\Msi\\Desktop\\investmentapp\\data"
        data_file = os.path.join(data_dir, "promotion.json")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(data_file):
            default_data = {
                "days": 7,
                "promotion_threshold": 100,
                "promotion_increment": 0.2,
                "max_trade_percent": 5,
                "demotion_threshold": 20,
                "demotion_decrement": 0.25,
                "auto_settings": {
                    "auto_days": 7,
                    "required_profit": 50
                }
            }
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=4)
            logging.debug("Utworzono pusty plik promotion.json")
            return default_data
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                logging.debug(f"Wczytano promotion.json: {data}")
                return data
        except json.JSONDecodeError as e:
            logging.error(f"Błąd wczytywania promotion.json: {str(e)}")
            default_data = {
                "days": 7,
                "promotion_threshold": 100,
                "promotion_increment": 0.2,
                "max_trade_percent": 5,
                "demotion_threshold": 20,
                "demotion_decrement": 0.25,
                "auto_settings": {
                    "auto_days": 7,
                    "required_profit": 50
                }
            }
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=4)
            return default_data

    def save_promotion_data(self):
        try:
            days = float(self.days_var.get())
            promotion_threshold = float(self.promotion_threshold_var.get())
            promotion_increment = float(self.promotion_increment_var.get())
            max_trade_percent = float(self.max_trade_percent_var.get())
            demotion_threshold = float(self.demotion_threshold_var.get())
            demotion_decrement = float(self.demotion_decrement_var.get())
            
            if days <= 0:
                self.days_error.config(text="Wartość musi być większa od 0")
                logging.error("Dni muszą być większe od 0")
                return
            if promotion_threshold < 0:
                self.promotion_threshold_error.config(text="Wartość musi być nieujemna")
                logging.error("Próg awansu musi być nieujemny")
                return
            if promotion_increment < 0:
                self.promotion_increment_error.config(text="Wartość musi być nieujemna")
                logging.error("Stopień awansu musi być nieujemny")
                return
            if max_trade_percent <= 0:
                self.max_trade_percent_error.config(text="Wartość musi być większa od 0")
                logging.error("Max % awans musi być większy od 0")
                return
            if demotion_threshold < 0:
                self.demotion_threshold_error.config(text="Wartość musi być nieujemna")
                logging.error("Próg degradacji musi być nieujemny")
                return
            if demotion_decrement < 0:
                self.demotion_decrement_error.config(text="Wartość musi być nieujemna")
                logging.error("Stopień degradacji musi być nieujemny")
                return
            
            self.days_error.config(text="")
            self.promotion_threshold_error.config(text="")
            self.promotion_increment_error.config(text="")
            self.max_trade_percent_error.config(text="")
            self.demotion_threshold_error.config(text="")
            self.demotion_decrement_error.config(text="")
            
            self.promotion_data = {
                "days": days,
                "promotion_threshold": promotion_threshold,
                "promotion_increment": promotion_increment,
                "max_trade_percent": max_trade_percent,
                "demotion_threshold": demotion_threshold,
                "demotion_decrement": demotion_decrement,
                "auto_settings": self.promotion_data.get("auto_settings", {
                    "auto_days": 7,
                    "required_profit": 50
                })
            }
            
            data_file = "C:\\Users\\Msi\\Desktop\\investmentapp\\data\\promotion.json"
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(self.promotion_data, f, indent=4)
            logging.debug("Zapisano dane promotion")
        except ValueError as e:
            logging.error(f"Błąd zapisu danych promotion: {str(e)}")

    def save_auto_settings(self):
        try:
            auto_days = float(self.auto_days_var.get())
            required_profit = float(self.required_profit_var.get())
            
            if auto_days <= 0:
                self.auto_days_error.config(text="Wartość musi być większa od 0")
                logging.error("Ilość dni trybu musi być większa od 0")
                return
            if required_profit <= 0:
                self.required_profit_error.config(text="Wartość musi być większa od 0")
                logging.error("Konieczny zysk % musi być większy od 0")
                return
            
            self.auto_days_error.config(text="")
            self.required_profit_error.config(text="")
            
            self.promotion_data["auto_settings"] = {
                "auto_days": auto_days,
                "required_profit": required_profit
            }
            
            data_file = "C:\\Users\\Msi\\Desktop\\investmentapp\\data\\promotion.json"
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(self.promotion_data, f, indent=4)
            logging.debug(f"Zapisano ustawienia Auto: auto_days={auto_days}, required_profit={required_profit}")
        except ValueError as e:
            self.auto_days_error.config(text="Nieprawidłowa wartość")
            logging.error(f"Błąd zapisu ustawień Auto: {str(e)}")