# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_api.py
import json
import os

def test_add_api_key():
    print("Test 1: Dodawanie klucza API")
    print("Kroki: W zakładce API wpisz klucz API i sekret, wybierz giełdę MEXC, kliknij Dodaj")
    print("Oczekiwany wynik: Klucz pojawia się w tabelce, zapisany w data/api_keys.json")
    print("Ręczny test: Wykonaj kroki, sprawdź tabelkę i data/api_keys.json.")

def test_duplicate_api_key():
    print("Test 2: Dodawanie zduplikowanego klucza API")
    print("Kroki: Dodaj klucz API, potem spróbuj dodać ten sam klucz ponownie")
    print("Oczekiwany wynik: Błąd w GUI (etykieta błędu), brak duplikatu w data/api_keys.json")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i data/api_keys.json.")

def test_delete_api_key():
    print("Test 3: Usuwanie klucza API")
    print("Kroki: Dodaj klucz API, kliknij Usuń")
    print("Oczekiwany wynik: Klucz znika z tabelki, usunięty z data/api_keys.json")
    print("Ręczny test: Wykonaj kroki, sprawdź tabelkę i data/api_keys.json.")

def test_test_api_key():
    print("Test 4: Testowanie klucza API")
    print("Kroki: Dodaj klucz API, kliknij Testuj")
    print("Oczekpaid result: Wynik testu w GUI (np. 'Połączenie API pomyślne' lub 'Błąd połączenia')")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI.")

def run_tests():
    print("=== Testy zakładki API ===")
    test_add_api_key()
    test_duplicate_api_key()
    test_delete_api_key()
    test_test_api_key()
    print("=== Koniec testów ===")

if __name__ == "__main__":
    run_tests()