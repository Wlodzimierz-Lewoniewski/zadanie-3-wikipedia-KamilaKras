import re, requests
import itertools

# Wzorce wyrażeń regularnych dla różnych typów odnośników Wikipedii
wzorzec_odn_artykul = r'<li[^>]*>.*<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>.*</li>'
wzorzec_odn_wewn = r'<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
wzorzec_odn_obrazek = r'<img[^>]*src=\"(//upload\.wikimedia\.org/[^"]+)\"[^>]*/>'
wzorzec_odn_zewnetrzny = r'<a[^>]*class=\"external[^"]*\"[^>]*href=\"([^"]+)\"[^>]*>'
wzorzec_odn_kategoria = r'<a[^>]*href=\"(/wiki/Kategoria:[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'


# Funkcja pomocnicza do formatowania i wyświetlania danych
def wyswietl_wynik(lista_elementow):
    wynik = ' | '.join(lista_elementow).strip()  # Łączenie elementów, usuwanie zbędnych spacji
    print(wynik)


# Wyciąganie głównego tekstu z artykułu
def wyciagnij_zawartosc(html):
    return html[html.find('<div id="mw-content-text"'):html.find('<div id="catlinks"')]


# Uzyskanie HTML-a sekcji przypisów (na końcu strony)
def wyciagnij_html_przypisy(html):
    html = html[html.find('id="Przypisy"'):]
    html = html[:html.find('<div class="mw-heading')]
    return html


# Pobieranie części HTML zawierającej linki do kategorii
def wyciagnij_html_kategorii(html):
    return html[html.find('<div id="catlinks"'):]


# Znajdowanie pasujących wyrażeń regularnych w tekście z limitem wyników
def znajdz_wzorce(wzorzec, tekst, flaga=0, maks=5):
    return list(map(lambda x: x.groups(), itertools.islice(re.finditer(wzorzec, tekst, flags=flaga), maks)))


# Tworzenie linku do kategorii na Wikipedii, zamienia spacje na "_"
def generuj_url_kategorii(kategoria_nazwa):
    nazwa_dopasowana = kategoria_nazwa.replace(' ', '_')
    return f'https://pl.wikipedia.org/wiki/Kategoria:{nazwa_dopasowana}'


# Pobieranie listy artykułów dla danej kategorii
def pobierz_artykuly_z_kategorii(nazwa_kat, maks=3):
    url_kategorii = generuj_url_kategorii(nazwa_kat)
    odp = requests.get(url_kategorii)
    html = odp.text
    artykuly = znajdz_wzorce(wzorzec_odn_artykul, html, maks=maks)
    return artykuly


# Pobranie pełnej treści artykułu na podstawie jego linku
def pobierz_zawartosc_artykulu(link):
    odp = requests.get("https://pl.wikipedia.org" + link)
    html = odp.text
    return html


# Pobieranie linków wewnętrznych z artykułu
def pobierz_linki_wewn(artykul, maks=5):
    html = wyciagnij_zawartosc(artykul)
    linki_wewn = znajdz_wzorce(wzorzec_odn_wewn, html, maks=maks)
    return linki_wewn


# Pobieranie obrazków z artykułu
def pobierz_obrazki(artykul, maks=3):
    html = wyciagnij_zawartosc(artykul)
    obrazki = znajdz_wzorce(wzorzec_odn_obrazek, html, maks=maks)
    return obrazki


# Pobieranie linków zewnętrznych w sekcji przypisów
def pobierz_linki_zewnetrzne(artykul, maks=3):
    html = wyciagnij_html_przypisy(artykul)
    zewnetrzne_linki = znajdz_wzorce(wzorzec_odn_zewnetrzny, html, maks=maks)
    return zewnetrzne_linki


# Pobieranie listy kategorii przypisanych do artykułu
def pobierz_kategorie(artykul, maks=3):
    html = wyciagnij_html_kategorii(artykul)
    kategorie = znajdz_wzorce(wzorzec_odn_kategoria, html, maks=maks)
    return kategorie


# Główna funkcja wykonująca całą procedurę
def main():
    kat = input().strip()
    artykuly = pobierz_artykuly_z_kategorii(kat)

    for link_art, tytul_art in artykuly:
        tresc = pobierz_zawartosc_artykulu(link_art)

        # Zbieranie i formatowanie wyników do wyświetlenia
        linki_wewn = pobierz_linki_wewn(tresc)
        wyswietl_wynik([el[1] for el in linki_wewn])

        obrazki = pobierz_obrazki(tresc)
        wyswietl_wynik([el[0] for el in obrazki])

        linki_zewn = pobierz_linki_zewnetrzne(tresc)
        wyswietl_wynik([el[0] for el in linki_zewn])

        kategorie = pobierz_kategorie(tresc)
        wyswietl_wynik([el[1].removeprefix('Kategoria:') for el in kategorie])


if __name__ == '__main__':
    main()
