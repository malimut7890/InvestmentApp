# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_error_handler.py

import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock
from src.core.error_handler import ErrorHandler
import logging

@pytest.fixture
def error_handler(tmp_path):
    """Inicjalizuje ErrorHandler z tymczasowym plikiem logów."""
    log_file = tmp_path / "error.log"
    return ErrorHandler(log_file=str(log_file))

@pytest.fixture
def root():
    """Inicjalizuje główne okno Tkinter."""
    return tk.Tk()

def test_log_error(error_handler, tmp_path):
    """Testuje logowanie błędu do pliku."""
    context = "TestError"
    message = "Błąd testowy"
    error_handler.log_error(context, message, exc_info=False)
    
    with open(tmp_path / "error.log", "r", encoding="utf-8") as f:
        log_content = f.read()
    
    assert f"{context}: {message}" in log_content

def test_show_gui_error(error_handler, root, tmp_path):
    """Testuje wyświetlanie błędu w GUI i logowanie."""
    with patch("tkinter.messagebox.showerror") as mock_showerror:
        error_handler.show_gui_error(root, "TestTitle", "TestMessage", exc_info=False)
        mock_showerror.assert_called_once_with("TestTitle", "TestMessage", parent=root)
        
        with open(tmp_path / "error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
        assert "TestTitle: TestMessage" in log_content

def test_log_and_show_error(error_handler, root, tmp_path):
    """Testuje jednoczesne logowanie i wyświetlanie błędu."""
    with patch("tkinter.messagebox.showerror") as mock_showerror:
        error_handler.log_and_show_error(root, "TestContext", "TestMessage", exc_info=False)
        mock_showerror.assert_called_once_with("TestContext", "TestMessage", parent=root)
        
        with open(tmp_path / "error.log", "r", encoding="utf-8") as f:
            log_content = f.read()
        assert "TestContext: TestMessage" in log_content

def test_log_error_with_traceback(error_handler, tmp_path):
    """Testuje logowanie błędu z tracebackiem."""
    try:
        raise ValueError("Testowy wyjątek")
    except ValueError as e:
        error_handler.log_error("TestContext", "Błąd z wyjątkiem", exc_info=True)
    
    with open(tmp_path / "error.log", "r", encoding="utf-8") as f:
        log_content = f.read()
    
    assert "TestContext: Błąd z wyjątkiem" in log_content
    assert "Traceback (most recent call last)" in log_content
    assert "ValueError: Testowy wyjątek" in log_content