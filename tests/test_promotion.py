# -*- coding: utf-8 -*-
# Ścieżka: C:\Users\Msi\Desktop\investmentapp\tests\test_promotion.py
import json
import os

def test_save_promotion_data():
    """Test zapisu danych w zakładce Awans"""
    print("Test 1: Zapis danych w zakładce Awans")
    print("Kroki: W zakładce Awans wpisz wartości: Dni=7, Próg awansu=100, Stopień awansu=0.2, Max % awans=5, Próg degradacji=20, Stopień degradacji=0.25, kliknij Zapisz")
    print("Oczekiwany wynik: Dane zapisane w data/promotion.json")
    print("Ręczny test: Wykonaj kroki, sprawdź data/promotion.json.")

def test_invalid_days():
    """Test niepoprawnych wartości dla Dni"""
    print("Test 2: Niepoprawne wartości dla Dni")
    print("Kroki: W zakładce Awans wpisz Dni=-1, kliknij Zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być większa od 0', log w app.log: 'Dni muszą być większe od 0'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def test_invalid_promotion_threshold():
    """Test niepoprawnych wartości dla Próg awansu"""
    print("Test 3: Niepoprawne wartości dla Próg awansu")
    print("Kroki: W zakładce Awans wpisz Próg awansu=-10, kliknij Zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być nieujemna', log w app.log: 'Próg awansu musi być nieujemny'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def test_invalid_promotion_increment():
    """Test niepoprawnych wartości dla Stopień awansu"""
    print("Test 4: Niepoprawne wartości dla Stopień awansu")
    print("Kroki: W zakładce Awans wpisz Stopień awansu=-0.2, kliknij Zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być nieujemna', log w app.log: 'Stopień awansu musi być nieujemny'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def test_invalid_max_trade_percent():
    """Test niepoprawnych wartości dla Max % awans"""
    print("Test 5: Niepoprawne wartości dla Max % awans")
    print("Kroki: W zakładce Awans wpisz Max % awans=0, kliknij Zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być większa od 0', log w app.log: 'Max % awans musi być większy od 0'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def test_invalid_demotion_threshold():
    """Test niepoprawnych wartości dla Próg degradacji"""
    print("Test 6: Niepoprawne wartości dla Próg degradacji")
    print("Kroki: W zakładce Awans wpisz Próg degradacji=-10, kliknij Zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być nieujemna', log w app.log: 'Próg degradacji musi być nieujemny'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def test_invalid_demotion_decrement():
    """Test niepoprawnych wartości dla Stopień degradacji"""
    print("Test 7: Niepoprawne wartości dla Stopień degradacji")
    print("Kroki: W zakładce Awans wpisz Stopień degradacji=-0.25, kliknij Zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być nieujemna', log w app.log: 'Stopień degradacji musi być nieuemny'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def test_auto_settings():
    """Test zapisu ustawień trybu Auto"""
    print("Test 8: Zapis ustawień trybu Auto")
    print("Kroki: W zakładce Awans kliknij dwukrotnie na Ilość dni trybu w tabelce Auto, wpisz 10, zapisz, kliknij na Konieczny zysk %, wpisz 50, zapisz")
    print("Oczekiwany wynik: Dane zapisane w data/promotion.json w sekcji auto_settings")
    print("Ręczny test: Wykonaj kroki, sprawdź data/promotion.json.")

def test_invalid_auto_days():
    """Test niepoprawnych wartości dla Ilość dni trybu"""
    print("Test 9: Niepoprawne wartości dla Ilość dni trybu")
    print("Kroki: W zakładce Awans kliknij dwukrotnie na Ilość dni trybu, wpisz 0, zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być większa od 0', log w app.log: 'Niepoprawna wartość dla auto_days: ...'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def test_invalid_required_profit():
    """Test niepoprawnych wartości dla Konieczny zysk %"""
    print("Test 10: Niepoprawne wartości dla Konieczny zysk %")
    print("Kroki: W zakładce Awans kliknij dwukrotnie na Konieczny zysk %, wpisz -10, zapisz")
    print("Oczekiwany wynik: Etykieta błędu w GUI: 'Wartość musi być większa od 0', log w app.log: 'Niepoprawna wartość dla required_profit: ...'")
    print("Ręczny test: Wykonaj kroki, sprawdź GUI i app.log.")

def run_tests():
    print("=== Testy zakładki Awans ===")
    test_save_promotion_data()
    test_invalid_days()
    test_invalid_promotion_threshold()
    test_invalid_promotion_increment()
    test_invalid_max_trade_percent()
    test_invalid_demotion_threshold()
    test_invalid_demotion_decrement()
    test_auto_settings()
    test_invalid_auto_days()
    test_invalid_required_profit()
    print("=== Koniec testów ===")

if __name__ == "__main__":
    run_tests()