# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_symbols.py
import json
import os

def test_add_symbol():
    """Test dodawania symbolu"""
    print("Test 1: Dodawanie symbolu")
    print("Kroki: W zakładce Symbole wpisz 'BTC/USDT', kliknij Dodaj")
    print("Oczekiwany wynik: Symbol na liście, w data/symbols.json: [{'symbol': 'BTC/USDT', 'selected': false}]")
    print("Ręczny test: Wykonaj kroki i sprawdź wynik.")

def test_add_non_usdt_symbol():
    """Test dodawania symbolu bez /USDT"""
    print("Test 2: Dodawanie symbolu bez /USDT")
    print("Kroki: W zakładce Symbole wpisz 'AAPL', kliknij Dodaj")
    print("Oczekiwany wynik: Symbol na liście, w data/symbols.json: [{'symbol': 'AAPL', 'selected': false}]")
    print("Ręczny test: Wykonaj kroki i sprawdź wynik.")

def test_add_duplicate_symbol():
    """Test dodawania zduplikowanego symbolu"""
    print("Test 3: Dodawanie zduplikowanego symbolu")
    print("Kroki: Dodaj 'BTC/USDT', potem spróbuj dodać 'BTC/USDT' ponownie")
    print("Oczekiwany wynik: Brak duplikatu w liście i data/symbols.json")
    print("Ręczny test: Wykonaj kroki i sprawdź wynik.")

def test_add_empty_symbol():
    """Test dodawania pustego symbolu"""
    print("Test 4: Dodawanie pustego symbolu")
    print("Kroki: Zostaw pole puste, kliknij Dodaj")
    print("Oczekiwany wynik: Brak zapisu w data/symbols.json")
    print("Ręczny test: Wykonaj kroki i sprawdź wynik.")

def test_toggle_symbol():
    """Test zaznaczania/odznaczania symbolu"""
    print("Test 5: Zaznaczanie/odznaczania symbolu")
    print("Kroki: Dodaj 'BTC/USDT', zaznacz checkbox, potem odznacz")
    print("Oczekiwany wynik: Checkbox zmienia stan, data/symbols.json aktualizuje 'selected': true/false")
    print("Ręczny test: Wykonaj kroki, sprawdź data/symbols.json.")

def test_delete_symbol():
    """Test usuwania symbolu"""
    print("Test 6: Usuwanie symbolu")
    print("Kroki: Dodaj 'BTC/USDT', kliknij Usuń")
    print("Oczekiwany wynik: Symbol znika z listy, data/symbols.json: []")
    print("Ręczny test: Wykonaj kroki i sprawdź wynik.")

def test_top_cryptos():
    """Test wyświetlania top 10 kryptowalut"""
    print("Test 7: Top 10 kryptowalut")
    print("Kroki: Sprawdź sekcję 'Top 10 kryptowalut' w zakładce Symbole")
    print("Oczekiwany wynik: Lista 10 par (np. BTC/USDT, ETH/USDT) bez stablecoinów")
    print("Ręczny test: Wykonaj kroki i sprawdź wynik.")

def run_tests():
    print("=== Testy zakładki Symbole ===")
    test_add_symbol()
    test_add_non_usdt_symbol()
    test_add_duplicate_symbol()
    test_add_empty_symbol()
    test_toggle_symbol()
    test_delete_symbol()
    test_top_cryptos()
    print("=== Koniec testów ===")

if __name__ == "__main__":
    run_tests()