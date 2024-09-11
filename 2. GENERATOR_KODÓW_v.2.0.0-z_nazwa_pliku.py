import os
import pandas as pd
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

# Funkcja do odczytu pliku Excel
def wczytaj_dane(plik_excel):
    print(f"Ładowanie danych z pliku {plik_excel}...")
    df = pd.read_excel(plik_excel)
    return df

# Funkcja do generowania kodów kreskowych Code 128
def generuj_kod_code128(id):
    return Code128(id, writer=ImageWriter())  # Generowanie kodu Code 128

# Funkcja do zapisywania kodu kreskowego jako plik PNG
def zapisz_kod_jako_png(kod_kreskowy, sciezka):
    if kod_kreskowy:
        # Nie dodajemy ręcznie rozszerzenia .png, ponieważ jest dodawane automatycznie
        kod_kreskowy.save(sciezka)  # Bez .png tutaj
        sciezka_png = f"{sciezka}.png"  # Ścieżka do wygenerowanego pliku z rozszerzeniem .png
        print(f"Zapisano kod kreskowy jako {sciezka_png}")
        return sciezka_png
    else:
        print(f"Nie udało się zapisać kodu kreskowego dla {sciezka}")
        return None

# Funkcja do dodawania tekstu pod kodem kreskowym
def dodaj_nazwe_pliku_do_obrazka(sciezka_png, nazwa_pliku):
    # Sprawdzenie, czy plik istnieje przed jego otwarciem
    if not os.path.exists(sciezka_png):
        print(f"Plik {sciezka_png} nie został znaleziony.")
        return

    # Otwieramy wygenerowany obrazek kodu kreskowego
    img = Image.open(sciezka_png)
    draw = ImageDraw.Draw(img)

    # Definiujemy czcionkę i rozmiar tekstu
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Ścieżka do czcionki (zmień jeśli inna lokalizacja)
    font_code = ImageFont.truetype(font_path, 15)  # Rozmiar domyślny dla kodu kreskowego
    font_nazwa = ImageFont.truetype(font_path, 13)  # 2 punkty mniejsza czcionka

    # Pozycjonowanie tekstu
    width, height = img.size
    text_width, text_height = draw.textsize(nazwa_pliku, font=font_nazwa)
    x = (width - text_width) / 2
    y = height - text_height - 5  # Dajemy 5px odstępu od dołu

    # Dodajemy tekst
    draw.text((x, y), nazwa_pliku, font=font_nazwa, fill="black")

    # Zapisujemy obrazek z dodanym tekstem
    img.save(sciezka_png)
    print(f"Dodano nazwę pliku {nazwa_pliku} na obrazie {sciezka_png}")

# Główna funkcja do przetwarzania danych i generowania kodów
def generuj_kody_z_plikow(plik_excel):
    dane = wczytaj_dane(plik_excel)

    # Iteracja po wierszach i generowanie kodów kreskowych
    for idx, row in dane.iterrows():
        id_value = str(row['ID'])  # Zachowujemy prefix "PO#"
        referencja_value = str(row['REFERENCJA_ELEMENTU'])  # Tylko referencja

        # Sprawdzenie, czy wartości ID i Referencja są prawidłowe
        print(f"Przetwarzanie wiersza {idx}: ID={id_value}, Referencja={referencja_value}")

        # Generujemy nazwę pliku na podstawie Referencji (bez Zeinr)
        nazwa_pliku = f"{referencja_value}"  # Tylko referencja
        sciezka_pliku = os.path.join('kody', nazwa_pliku)

        # Generujemy kod Code 128
        kod_kreskowy = generuj_kod_code128(id_value)

        # Zapisujemy kod jako plik PNG (domyślnie PNG)
        sciezka_png = zapisz_kod_jako_png(kod_kreskowy, sciezka_pliku)

        # Dodajemy nazwę pliku na obrazek, jeśli kod został poprawnie zapisany
        if sciezka_png:
            dodaj_nazwe_pliku_do_obrazka(sciezka_png, referencja_value)

# Tworzymy folder do przechowywania kodów kreskowych
if not os.path.exists('kody'):
    os.makedirs('kody')

# Uruchamiamy proces generowania kodów
plik_excel = 'wynik.xlsx'  # Nazwa pliku, który znajduje się w katalogu skryptu
generuj_kody_z_plikow(plik_excel)

print("Proces generowania kodów kreskowych zakończony.")
