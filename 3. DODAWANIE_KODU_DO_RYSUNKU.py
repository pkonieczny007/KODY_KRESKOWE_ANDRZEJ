import os
import io
from PyPDF2 import PdfReader, PdfWriter, PageObject
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image

# Funkcja do dodawania kodu kreskowego na samym końcu, po scaleniu stron PDF
def dodaj_kod_do_pdf(plik_pdf, plik_png, sciezka_docelowa):
    # Wczytanie pliku PDF
    pdf_reader = PdfReader(plik_pdf)
    pdf_writer = PdfWriter()

    # Wczytanie obrazu z kodem kreskowym (plik PNG)
    barcode_img = Image.open(plik_png)
    barcode_img_width, barcode_img_height = barcode_img.size

    # Zmniejszenie wielkości kodu kreskowego o 3x
    barcode_img_width //= 3
    barcode_img_height //= 3

    # Wysokość dodatkowego obszaru roboczego pod rysunkiem równa wysokości kodu kreskowego
    dodatkowy_obszar_roboczy = barcode_img_height + 20  # Dodajemy 20 jednostek marginesu

    # Iteracja po stronach PDF
    for page_num, page in enumerate(pdf_reader.pages):
        # Pobieranie wymiarów oryginalnej strony
        page_width = page.mediabox.width
        page_height = page.mediabox.height

        # Tworzymy nową stronę z większą wysokością tylko na dole, nie przesuwając rysunku w górę
        new_page = PageObject.create_blank_page(width=page_width, height=page_height + dodatkowy_obszar_roboczy)

        # Łączymy oryginalną stronę z nową stroną bez przesuwania
        new_page.merge_page(page)

        # Dodanie nowej strony do wynikowego PDF bez rysowania kodu kreskowego
        pdf_writer.add_page(new_page)

    # Zapisujemy połączone strony bez kodu kreskowego
    tymczasowy_pdf = "tymczasowy.pdf"
    with open(tymczasowy_pdf, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    # Teraz wczytujemy scalony PDF i dodajemy kod kreskowy
    pdf_reader = PdfReader(tymczasowy_pdf)
    pdf_writer = PdfWriter()

    for page_num, page in enumerate(pdf_reader.pages):
        # Tworzymy nowe płótno do rysowania kodu kreskowego na stronie
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height + dodatkowy_obszar_roboczy))

        # Pozycjonowanie kodu kreskowego w lewym górnym rogu
        x_position = 0  # Lewa krawędź
        y_position = page_height + dodatkowy_obszar_roboczy - barcode_img_height  # Górna krawędź
        image = ImageReader(plik_png)
        can.drawImage(image, x_position, y_position, width=barcode_img_width, height=barcode_img_height)
        can.save()

        # Dodajemy kod kreskowy na wierzchu już scalonej strony
        packet.seek(0)
        barcode_page = PdfReader(packet).pages[0]
        page.merge_page(barcode_page)

        # Dodanie nowej strony z kodem kreskowym do wynikowego PDF
        pdf_writer.add_page(page)

    # Zapis nowego pliku PDF z kodem kreskowym
    with open(sciezka_docelowa, "wb") as output_pdf:
        pdf_writer.write(output_pdf)

    # Usunięcie tymczasowego pliku
    os.remove(tymczasowy_pdf)

    print(f"Zapisano plik z kodem kreskowym jako: {sciezka_docelowa}")

# Funkcja do dopasowania plików na podstawie części nazwy przed znakiem rozdzielającym
def pobierz_glowna_nazwe(nazwa_pliku):
    # Szukamy pierwszego wystąpienia znaku rozdzielającego i bierzemy początek nazwy
    for separator in ['_', '-', ',', '.']:
        if separator in nazwa_pliku:
            return nazwa_pliku.split(separator)[0]
    return nazwa_pliku  # Jeśli nie ma separatora, zwróć całą nazwę

# Główna funkcja przetwarzania katalogów
def przetwarzaj_rysunki_z_kodami(katalog_pdf, katalog_kody, katalog_docelowy):
    # Sprawdzamy, czy katalog docelowy istnieje, jeśli nie - tworzymy go
    if not os.path.exists(katalog_docelowy):
        os.makedirs(katalog_docelowy)

    # Iterujemy po plikach PDF i dopasowujemy do nich odpowiednie pliki PNG z kodami
    for plik_pdf in os.listdir(katalog_pdf):
        if plik_pdf.endswith('.pdf'):
            nazwa_plik_pdf = os.path.splitext(plik_pdf)[0]  # Usunięcie rozszerzenia .pdf
            glowna_nazwa_pdf = pobierz_glowna_nazwe(nazwa_plik_pdf)  # Główna część nazwy pliku PDF

            # Szukamy odpowiadającego pliku PNG, który zaczyna się od tej samej głównej nazwy
            for plik_png in os.listdir(katalog_kody):
                glowna_nazwa_png = pobierz_glowna_nazwe(os.path.splitext(plik_png)[0])  # Główna część nazwy pliku PNG
                if glowna_nazwa_pdf == glowna_nazwa_png and plik_png.endswith('.png'):
                    sciezka_pdf = os.path.join(katalog_pdf, plik_pdf)
                    sciezka_kreskowy_png = os.path.join(katalog_kody, plik_png)
                    sciezka_docelowa = os.path.join(katalog_docelowy, f"{nazwa_plik_pdf}+kod.pdf")  # Nowa nazwa pliku z kodem

                    # Dodajemy kod kreskowy do pliku PDF
                    dodaj_kod_do_pdf(sciezka_pdf, sciezka_kreskowy_png, sciezka_docelowa)
                    break
            else:
                print(f"Nie znaleziono pliku z kodem kreskowym dla: {plik_pdf}")

# Ścieżki katalogów
katalog_pdf = 'rysunki'  # Katalog z plikami PDF
katalog_kody = 'kody'  # Katalog z plikami PNG kodów kreskowych
katalog_docelowy = 'rysunki_z_kodami'  # Katalog do zapisania nowych plików PDF

# Uruchamiamy przetwarzanie plików
przetwarzaj_rysunki_z_kodami(katalog_pdf, katalog_kody, katalog_docelowy)
