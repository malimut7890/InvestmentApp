# -*- coding: utf-8 -*-
# Path: C:\Users\Msi\Desktop\investmentapp\src\tabs\live\live.py
import tkinter as tk
from tkinter import ttk
import logging

class LiveTab:
    def __init__(self, frame):
        try:
            logging.info("=== Initializing LiveTab ===")
            self.frame = frame
            
            # Placeholder label
            tk.Label(self.frame, text="Live Tab (Empty)").pack(pady=10)
            
            logging.info("=== LiveTab initialized ===")
        except Exception as e:
            logging.error(f"Error initializing LiveTab: {str(e)}")
            raise