# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\tabs\api\api.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import logging
import ccxt.async_support as ccxt

class ApiTab:
    def __init__(self, frame):
        try:
            logging.info("=== Initializing ApiTab ===")
            self.frame = frame
            self.api_keys_file = "C:\\Users\\Msi\\Desktop\\investmentapp\\data\\api_keys.json"
            self.supported_exchanges = ["MEXC", "KUCOIN"]  # Added KUCOIN
            
            # Add API key button
            ttk.Button(self.frame, text="Add API Key", command=self.add_api_key).pack(pady=5)
            
            # API keys table
            self.tree = ttk.Treeview(self.frame, columns=("Exchange", "API Key", "Edit", "Delete", "Test"), show="headings")
            self.tree.heading("Exchange", text="Exchange")
            self.tree.heading("API Key", text="API Key")
            self.tree.heading("Edit", text="Edit")
            self.tree.heading("Delete", text="Delete")
            self.tree.heading("Test", text="Test")
            for col in self.tree["columns"]:
                self.tree.column(col, width=100, anchor="center")
            self.tree.pack(pady=10, fill="both", expand=True)
            
            self.tree.bind("<Double-1>", self.on_tree_double_click)
            
            self.update_api_keys_display()
            logging.info("=== ApiTab initialized ===")
        except Exception as e:
            logging.error(f"Error initializing ApiTab: {str(e)}")
            tk.messagebox.showerror("Error", f"Error initializing tab: {str(e)}")
            raise

    def load_api_keys(self):
        try:
            if not os.path.exists(self.api_keys_file):
                logging.info("No api_keys.json file, returning empty list")
                return []
            with open(self.api_keys_file, "r", encoding="utf-8-sig") as f:
                api_keys = json.load(f)
            logging.info(f"Loaded API keys: {api_keys}")
            return api_keys
        except Exception as e:
            logging.error(f"Error loading API keys: {str(e)}")
            return []

    def save_api_keys(self, api_keys):
        try:
            with open(self.api_keys_file, "w", encoding="utf-8") as f:
                json.dump(api_keys, f, indent=4, ensure_ascii=False)
            logging.info(f"Saved API keys: {api_keys}")
        except Exception as e:
            logging.error(f"Error saving API keys: {str(e)}")
            raise

    def add_api_key(self):
        try:
            window = tk.Toplevel(self.frame)
            window.title("Add API Key")
            window.geometry("400x400")
            
            tk.Label(window, text="Exchange:").pack(pady=5)
            exchange_var = tk.StringVar(value=self.supported_exchanges[0])
            exchange_combo = ttk.Combobox(window, textvariable=exchange_var, values=self.supported_exchanges, state="readonly")
            exchange_combo.pack(pady=5)
            
            tk.Label(window, text="API Key:").pack(pady=5)
            api_key_var = tk.StringVar()
            ttk.Entry(window, textvariable=api_key_var).pack(pady=5)
            
            tk.Label(window, text="API Secret:").pack(pady=5)
            api_secret_var = tk.StringVar()
            ttk.Entry(window, textvariable=api_secret_var, show="*").pack(pady=5)
            
            tk.Label(window, text="Passphrase (for KuCoin):").pack(pady=5)
            passphrase_var = tk.StringVar()
            ttk.Entry(window, textvariable=passphrase_var, show="*").pack(pady=5)
            
            tk.Label(window, text="Limit żądań/min:").pack(pady=5)
            rate_limit_var = tk.StringVar(value="1800")
            ttk.Entry(window, textvariable=rate_limit_var).pack(pady=5)
            
            tk.Label(window, text="Timeout (s):").pack(pady=5)
            timeout_var = tk.StringVar(value="10")
            ttk.Entry(window, textvariable=timeout_var).pack(pady=5)
            
            def save_key():
                try:
                    exchange = exchange_var.get().upper()
                    api_key = api_key_var.get()
                    api_secret = api_secret_var.get()
                    passphrase = passphrase_var.get() if exchange == "KUCOIN" else ""
                    rate_limit = int(rate_limit_var.get())
                    timeout = int(timeout_var.get())
                    
                    if not api_key or not api_secret:
                        raise ValueError("API Key and API Secret are required")
                    if exchange == "KUCOIN" and not passphrase:
                        raise ValueError("Passphrase is required for KuCoin")
                    if rate_limit < 1:
                        raise ValueError("Rate limit must be greater than 0")
                    if timeout < 1:
                        raise ValueError("Timeout must be greater than 0")
                    
                    api_keys = self.load_api_keys()
                    api_keys.append({
                        "exchange": exchange,
                        "api_key": api_key,
                        "api_secret": api_secret,
                        "passphrase": passphrase,
                        "rate_limit_requests": rate_limit,
                        "timeout_seconds": timeout
                    })
                    self.save_api_keys(api_keys)
                    self.update_api_keys_display()
                    window.destroy()
                    logging.info(f"Added API key for exchange {exchange}")
                    tk.messagebox.showinfo("Success", f"Added API key for {exchange}")
                except Exception as e:
                    logging.error(f"Error adding API key: {str(e)}")
                    tk.messagebox.showerror("Error", f"Error adding API key: {str(e)}")
            
            ttk.Button(window, text="Save", command=save_key).pack(pady=10)
            ttk.Button(window, text="Cancel", command=window.destroy).pack(pady=10)
            logging.info("Opened add API key window")
        except Exception as e:
            logging.error(f"Error opening add API key window: {str(e)}")
            tk.messagebox.showerror("Error", f"Error opening window: {str(e)}")

    def update_api_keys_display(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            api_keys = self.load_api_keys()
            for key in api_keys:
                self.tree.insert("", tk.END, values=(
                    key["exchange"],
                    key["api_key"],
                    "Edit",
                    "Delete",
                    "Test"
                ), tags=(key["exchange"],))
            logging.info(f"API keys table updated, keys: {[key['exchange'] for key in api_keys]}")
        except Exception as e:
            logging.error(f"Error updating API keys table: {str(e)}")
            tk.messagebox.showerror("Error", f"Error updating table: {str(e)}")
            raise

    def on_tree_double_click(self, event):
        try:
            item = self.tree.selection()
            if not item:
                logging.info("No item selected in API keys table")
                return
            item = item[0]
            col = self.tree.identify_column(event.x)
            exchange = self.tree.item(item, "tags")[0]
            logging.info(f"Double-click on exchange {exchange}, column {col}")
            
            if col == "#3":  # Edit
                api_keys = self.load_api_keys()
                key_data = next((key for key in api_keys if key["exchange"] == exchange), None)
                if not key_data:
                    logging.error(f"No API key found for exchange {exchange}")
                    tk.messagebox.showerror("Error", f"No API key found for {exchange}")
                    return
                
                window = tk.Toplevel(self.frame)
                window.title(f"Edit API Key: {exchange}")
                window.geometry("400x400")
                
                tk.Label(window, text="Exchange:").pack(pady=5)
                exchange_var = tk.StringVar(value=exchange)
                ttk.Combobox(window, textvariable=exchange_var, values=self.supported_exchanges, state="readonly").pack(pady=5)
                
                tk.Label(window, text="API Key:").pack(pady=5)
                api_key_var = tk.StringVar(value=key_data["api_key"])
                ttk.Entry(window, textvariable=api_key_var).pack(pady=5)
                
                tk.Label(window, text="API Secret:").pack(pady=5)
                api_secret_var = tk.StringVar(value=key_data["api_secret"])
                ttk.Entry(window, textvariable=api_secret_var, show="*").pack(pady=5)
                
                tk.Label(window, text="Passphrase (for KuCoin):").pack(pady=5)
                passphrase_var = tk.StringVar(value=key_data.get("passphrase", ""))
                ttk.Entry(window, textvariable=passphrase_var, show="*").pack(pady=5)
                
                tk.Label(window, text="Limit żądań/min:").pack(pady=5)
                rate_limit_var = tk.StringVar(value=str(key_data.get("rate_limit_requests", 1800)))
                ttk.Entry(window, textvariable=rate_limit_var).pack(pady=5)
                
                tk.Label(window, text="Timeout (s):").pack(pady=5)
                timeout_var = tk.StringVar(value=str(key_data.get("timeout_seconds", 10)))
                ttk.Entry(window, textvariable=timeout_var).pack(pady=5)
                
                def save_key():
                    try:
                        new_exchange = exchange_var.get().upper()
                        api_key = api_key_var.get()
                        api_secret = api_secret_var.get()
                        passphrase = passphrase_var.get() if new_exchange == "KUCOIN" else ""
                        rate_limit = int(rate_limit_var.get())
                        timeout = int(timeout_var.get())
                        
                        if not api_key or not api_secret:
                            raise ValueError("API Key and API Secret are required")
                        if new_exchange == "KUCOIN" and not passphrase:
                            raise ValueError("Passphrase is required for KuCoin")
                        if rate_limit < 1:
                            raise ValueError("Rate limit must be greater than 0")
                        if timeout < 1:
                            raise ValueError("Timeout must be greater than 0")
                        
                        api_keys = self.load_api_keys()
                        api_keys = [key for key in api_keys if key["exchange"] != exchange]
                        api_keys.append({
                            "exchange": new_exchange,
                            "api_key": api_key,
                            "api_secret": api_secret,
                            "passphrase": passphrase,
                            "rate_limit_requests": rate_limit,
                            "timeout_seconds": timeout
                        })
                        self.save_api_keys(api_keys)
                        self.update_api_keys_display()
                        window.destroy()
                        logging.info(f"Updated API key for exchange {new_exchange}")
                        tk.messagebox.showinfo("Success", f"Updated API key for {new_exchange}")
                    except Exception as e:
                        logging.error(f"Error updating API key: {str(e)}")
                        tk.messagebox.showerror("Error", f"Error updating API key: {str(e)}")
                
                ttk.Button(window, text="Save", command=save_key).pack(pady=10)
                ttk.Button(window, text="Cancel", command=window.destroy).pack(pady=10)
                logging.info(f"Opened edit API key window for {exchange}")
            
            elif col == "#4":  # Delete
                try:
                    api_keys = self.load_api_keys()
                    api_keys = [key for key in api_keys if key["exchange"] != exchange]
                    self.save_api_keys(api_keys)
                    self.update_api_keys_display()
                    logging.info(f"Deleted API key for exchange {exchange}")
                    tk.messagebox.showinfo("Success", f"Deleted API key for {exchange}")
                except Exception as e:
                    logging.error(f"Error deleting API key for exchange {exchange}: {str(e)}")
                    tk.messagebox.showerror("Error", f"Error deleting API key: {str(e)}")
            
            elif col == "#5":  # Test
                try:
                    api_keys = self.load_api_keys()
                    key_data = next((key for key in api_keys if key["exchange"] == exchange), None)
                    if not key_data:
                        logging.error(f"No API key found for exchange {exchange}")
                        tk.messagebox.showerror("Error", f"No API key found for {exchange}")
                        return
                    
                    exchange_class = getattr(ccxt, exchange.lower())
                    exchange_instance = exchange_class({
                        "apiKey": key_data["api_key"],
                        "secret": key_data["api_secret"],
                        "password": key_data.get("passphrase", "") if exchange == "KUCOIN" else None,
                        "rateLimit": key_data.get("rate_limit_requests", 1800),
                        "timeout": key_data.get("timeout_seconds", 10) * 1000  # Convert to milliseconds
                    })
                    
                    async def test_connection():
                        try:
                            await exchange_instance.load_markets()
                            await exchange_instance.close()
                            logging.info(f"Successfully tested API key for {exchange}")
                            tk.messagebox.showinfo("Success", f"API key for {exchange} is valid")
                        except Exception as e:
                            logging.error(f"Error testing API key for {exchange}: {str(e)}")
                            tk.messagebox.showerror("Error", f"Error testing API key: {str(e)}")
                    
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(test_connection())
                    loop.close()
                except Exception as e:
                    logging.error(f"Error testing API key for {exchange}: {str(e)}")
                    tk.messagebox.showerror("Error", f"Error testing API key: {str(e)}")
        
        except Exception as e:
            logging.error(f"Error editing API keys table: {str(e)}")
            tk.messagebox.showerror("Error", f"Error editing table: {str(e)}")