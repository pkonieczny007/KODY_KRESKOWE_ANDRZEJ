import os
import io
import requests
from PyPDF2 import PdfReader, PdfWriter, PageObject
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image

# URL do logo na GitHubie
logo_url = 'https://github.com/pkonieczny007/KODY_KRESKOWE_ANDRZEJ/blob/main/logo.png?raw=true'

# Funkcja do pobrania obrazu z URL-a
def pobierz_logo_z_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception(f"Nie udało się pobrać logo z URL: {url}")

# Funkcja do dodawania kodu kreskowego, logo i numeru zlecenia do pliku PDF
def dodaj_kod_logo_nr_do_pdf(plik_pdf, plik_png, sciezka_docelowa, numer_zlecenia=None, pusty=False):
    pdf_writer = PdfWriter()

    # Wczytanie obrazu z kodem kreskowym
    barcode_img = Image.open(plik_png)
    barcode_img_width, barcode_img_height = barcode_img.size

    # Zmniejszenie wielkości kodu kreskowego o 3x
    barcode_img_width //= 3
    barcode_img_height //= 3

    # Pobranie logo
    logo_img = pobierz_logo_z_url(logo_url)
    logo_img_width, logo_img_height = logo_img.size

    # Zmniejszenie wielkości logo
    logo_img_width //= 3
    logo_img_height //= 3

    # Dodatkowy obszar roboczy na dole na kod kreskowy
    dodatkowy_obszar_roboczy = barcode_img_height + 20

    # Sprawdzamy, czy plik PDF istnieje, jeśli nie, tworzymy pusty PDF
    if pusty or not os.path.exists(plik_pdf):
        print(f"Brak rysunku, tworzenie pliku z samym kodem kreskowym: {plik_pdf}")
        blank_page = PageObject.create_blank_page(width=210 * mm, height=297 * mm)
        pdf_writer.add_page(blank_page)
        with open(plik_pdf, "wb") as blank_pdf:
            pdf_writer.write(blank_pdf)
        pdf_reader = PdfReader(plik_pdf)
    else:
        pdf_reader = PdfReader(plik_pdf)

    # Stworzenie tymczasowego pliku PDF bez kodu
    tymczasowy_pdf = "tymczasowy.pdf"
    for page_num, page in enumerate(pdf_reader.pages):
        page_width = page.mediabox.width
        page_height = page.mediabox.height
        new_page = PageObject.create_blank_page(width=page_width, height=page_height + dodatkowy_obszar_roboczy)
        new_page.merge_page(page)
        pdf_writer.add_page(new_page)

    with open(tymczasowy_pdf, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    # Teraz dodajemy kod kreskowy, logo i numer zlecenia
    pdf_reader = PdfReader(tymczasowy_pdf)
    pdf_writer = PdfWriter()

    for page_num, page in enumerate(pdf_reader.pages):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height + dodatkowy_obszar_roboczy))

        # Dodanie kodu kreskowego
        x_position_kod = 0
        y_position_kod = page_height + dodatkowy_obszar_roboczy - barcode_img_height

        # Konwersja na float, aby uniknąć błędów typów
        x_position_kod = float(x_position_kod)
        y_position_kod = float(y_position_kod)

        image_kod = ImageReader(plik_png)
        can.drawImage(image_kod, x_position_kod, y_position_kod, width=barcode_img_width, height=barcode_img_height)

        # Dodanie logo
        x_position_logo = page_width - logo_img_width
        y_position_logo = page_height + dodatkowy_obszar_roboczy - logo_img_height

        x_position_logo = float(x_position_logo)
        y_position_logo = float(y_position_logo)

        can.drawImage(ImageReader(logo_img), x_position_logo, y_position_logo, width=logo_img_width, height=logo_img_height)

        # Dodanie numeru zlecenia, jeśli został podany
        if numer_zlecenia:
            can.setFont("Helvetica", 20)
            x_position_nr = float(barcode_img_width + 5)  # Konwersja na float
            y_position_nr = float(page_height + dodatkowy_obszar_roboczy - 30)  # Konwersja na float
            can.drawString(x_position_nr, y_position_nr, numer_zlecenia)

        can.save()

        packet.seek(0)
        barcode_page = PdfReader(packet).pages[0]
        page.merge_page(barcode_page)
        pdf_writer.add_page(page)

    with open(sciezka_docelowa, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    os.remove(tymczasowy_pdf)
    print(f"Zapisano plik z kodem kreskowym jako: {sciezka_docelowa}")

# Funkcja do dopasowania plików na podstawie głównej części nazwy przed znakiem rozdzielającym
def pobierz_glowna_nazwe(nazwa_pliku):
    for separator in ['_', '-', ',', '.']:
        if separator in nazwa_pliku:
            return nazwa_pliku.split(separator)[0]
    return nazwa_pliku

# Funkcja główna do przetwarzania kodów kreskowych i rysunków
def przetwarzaj_kody_z_rysunkami(katalog_pdf, katalog_kody, katalog_docelowy):
    if not os.path.exists(katalog_docelowy):
        os.makedirs(katalog_docelowy)

    numer_zlecenia = input("Podaj numer zlecenia (lub naciśnij Enter, aby pominąć): ").strip() or None

    for plik_png in os.listdir(katalog_kody):
        if plik_png.endswith('.png'):
            # Pobieramy główną nazwę z pliku kodu kreskowego
            glowna_nazwa_png = pobierz_glowna_nazwe(os.path.splitext(plik_png)[0])
            
            # Szukamy rysunku PDF na podstawie głównej nazwy
            rysunek_pdf = None
            for plik_pdf in os.listdir(katalog_pdf):
                if plik_pdf.startswith(glowna_nazwa_png) and plik_pdf.endswith('.pdf'):
                    rysunek_pdf = os.path.join(katalog_pdf, plik_pdf)
                    break

            # Jeśli nie znaleziono rysunku, ustalamy pusty rysunek
            pusty = False
            if rysunek_pdf is None:
                rysunek_pdf = os.path.join(katalog_docelowy, f"{glowna_nazwa_png}_empty.pdf")
                pusty = True

            sciezka_kreskowy_png = os.path.join(katalog_kody, plik_png)
            if pusty:
                sciezka_docelowa = os.path.join(katalog_docelowy, f"{os.path.splitext(plik_png)[0]}_pusty+kod.pdf")
            else:
                sciezka_docelowa = os.path.join(katalog_docelowy, f"{os.path.splitext(plik_png)[0]}+kod.pdf")

            # Dodajemy kod kreskowy, logo i numer zlecenia do pliku PDF
            dodaj_kod_logo_nr_do_pdf(rysunek_pdf, sciezka_kreskowy_png, sciezka_docelowa, numer_zlecenia, pusty)

# Ścieżki katalogów
katalog_pdf = 'rysunki'
katalog_kody = 'kody'
katalog_docelowy = 'rysunki_z_kodami'

# Uruchomienie przetwarzania
przetwarzaj_kody_z_rysunkami(katalog_pdf, katalog_kody, katalog_docelowy)
