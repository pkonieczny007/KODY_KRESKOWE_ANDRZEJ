import os
import pandas as pd
from tkinter import Tk, filedialog

# Funkcja do wyboru pliku Excel przez okno dialogowe
def wybierz_plik():
    root = Tk()
    root.withdraw()  # Ukryj główne okno
    plik = filedialog.askopenfilename(filetypes=[("Pliki Excel", "*.xlsx")])
    return plik

# Funkcja do znalezienia domyślnych plików w folderze
def znajdz_plik_zlecen():
    for file in os.listdir('.'):
        if file.startswith("Zlecenia produkcyjne") and file.endswith(".xlsx"):
            return file
    return None

# Funkcja do odczytu pliku wykazu roboczego i zleceń
def wczytaj_wykazy():
    # Wczytanie pliku roboczego przez okno dialogowe
    print("Wybierz wykaz roboczy")
    plik_roboczy = wybierz_plik()
    if not plik_roboczy:
        print("Nie wybrano pliku wykazu roboczego.")
        return
    
    # Wczytanie pliku zleceń produkcyjnych (domyślnie szuka w folderze)
    plik_zlecen = znajdz_plik_zlecen()
    if not plik_zlecen:
        print("Nie znaleziono domyślnego pliku zleceń produkcyjnych.")
        return
    
    # Wczytaj dane z plików Excel
    wykaz_roboczy = pd.read_excel(plik_roboczy)
    zlecenia = pd.read_excel(plik_zlecen)

    return wykaz_roboczy, zlecenia

# Funkcja do dopasowania elementów na podstawie REFERENCJA_ELEMENTU i Produkt
def dopasuj_elementy(wykaz_roboczy, zlecenia):
    # Tworzymy kopię wykazu roboczego
    wynik = wykaz_roboczy.copy()

    # Dopasowanie danych na podstawie kolumn 'REFERENCJA_ELEMENTU' i 'Produkt'
    for idx, row in wynik.iterrows():
        referencja = row['REFERENCJA_ELEMENTU']

        # Filtrujemy zlecenia na podstawie REFERENCJA_ELEMENTU (znajdującego się w Produkt)
        dopasowanie = zlecenia[zlecenia['Produkt'] == referencja]
        
        if not dopasowanie.empty:
            identyfikator_elementu = dopasowanie.iloc[0]['Identyfikator elementu']
            wynik.loc[idx, 'Identyfikator elementu'] = identyfikator_elementu
            # Utworzenie nowej kolumny ID z formatem "PO#<Identyfikator elementu>"
            wynik.loc[idx, 'ID'] = f"PO#{identyfikator_elementu}"
        else:
            wynik.loc[idx, 'Identyfikator elementu'] = 'brak'
            wynik.loc[idx, 'ID'] = 'brak'

    return wynik

# Funkcja do zapisu wyników do pliku Excel
def zapisz_wynik(wynik):
    wynik.to_excel('wynik.xlsx', index=False)
    print("Wynik zapisany do pliku wynik.xlsx")

# Główna funkcja
def main():
    wykaz_roboczy, zlecenia = wczytaj_wykazy()
    if wykaz_roboczy is not None and zlecenia is not None:
        wynik = dopasuj_elementy(wykaz_roboczy, zlecenia)
        zapisz_wynik(wynik)

if __name__ == '__main__':
    main()
