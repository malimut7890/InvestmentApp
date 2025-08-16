# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\src\core\error_handler.py

import logging
import traceback
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

class ErrorHandler:
    """Centralny moduł do obsługi błędów w aplikacji.

    Odpowiada za logowanie błędów do pliku oraz wyświetlanie komunikatów w GUI.

    Attributes:
        logger (logging.Logger): Logger dla błędów.
    """

    def __init__(self, log_file: str = "C:\\Users\\Msi\\Desktop\\investmentapp\\logs\\error.log"):
        """Inicjalizuje ErrorHandler z konfiguracją logowania.

        Args:
            log_file (str): Ścieżka do pliku logów błędów.
        """
        self.logger = logging.getLogger("ErrorHandler")
        self.logger.setLevel(logging.ERROR)
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s | Traceback: %(exc_info)s"
        ))
        self.logger.handlers = [handler]

    def log_error(self, context: str, message: str, exc_info: bool = True) -> None:
        """Loguje błąd z kontekstem i szczegółami.

        Args:
            context (str): Kontekst błędu (np. nazwa operacji lub modułu).
            message (str): Wiadomość błędu.
            exc_info (bool): Czy dołączyć traceback (domyślnie True).
        """
        self.logger.error(f"{context}: {message}", exc_info=exc_info)

    def show_gui_error(self, parent: tk.Tk, title: str, message: str, exc_info: bool = False) -> None:
        """Wyświetla komunikat błędu w GUI i loguje go.

        Args:
            parent (tk.Tk): Rodzicielskie okno Tkinter.
            title (str): Tytuł okna błędu.
            message (str): Wiadomość błędu.
            exc_info (bool): Czy dołączyć traceback do logu (domyślnie False dla GUI).
        """
        full_message = f"{message}\nTraceback: {traceback.format_exc()}" if exc_info else message
        self.log_error(title, full_message, exc_info=exc_info)
        messagebox.showerror(title, full_message, parent=parent)

    def log_and_show_error(self, parent: tk.Tk, context: str, message: str, exc_info: bool = True) -> None:
        """Loguje i wyświetla błąd jednocześnie.

        Args:
            parent (tk.Tk): Rodzicielskie okno Tkinter.
            context (str): Kontekst błędu.
            message (str): Wiadomość błędu.
            exc_info (bool): Czy dołączyć traceback.
        """
        self.log_error(context, message, exc_info)
        messagebox.showerror(context, f"{message}\nTraceback: {traceback.format_exc()}" if exc_info else message, parent=parent)