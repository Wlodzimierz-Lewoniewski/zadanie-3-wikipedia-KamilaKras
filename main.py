import re, requests
import itertools

# Pobieranie zawartosi aartykulu
def pobierz_zawartosc(html):
    return html[html.find('<div id="mw-content-text"'):html.find('<div id="catlinks"')]

# Pobieranie przypisów
def pobierz_przyp_html(html):
    html = html[html.find('id="Przypisy"'):]
    html = html[:html.find('<div class="mw-heading')]
    return html

# Pobieranie kategorii
def pobierz_kat_html(html):
    return html[html.find('<div id="catlinks"'):]
# Znajdowanie pasujących wyraazen reg.
def znajdz_wzorce(wzorzec, tekst, flaga=0, maks=5):
    return list(map(lambda x: x.groups(), itertools.islice(re.finditer(wzorzec, tekst, flags=flaga), maks)))

# Zamiana spacji na "_"
def generuj_url_kat(kategoria_nazwa):
    nazwa_dopasowana = kategoria_nazwa.replace(' ', '_')
    return f'https://pl.wikipedia.org/wiki/Kategoria:{nazwa_dopasowana}'
# Pobieranie listy artykułów z kategorii
def pobierz_artykuly_z_kategorii(nazwa_kat, maks=3):
    url_kategorii = generuj_url_kat(nazwa_kat)
    odp = requests.get(url_kategorii)
    html = odp.text
    artykuly = znajdz_wzorce(wzorzec_odn_artykul, html, maks=maks)
    return artykuly
# Pobranie artykułu
def pobierz_zawartosc_artykulu(link):
    odp = requests.get("https://pl.wikipedia.org" + link)
    html = odp.text
    return html
# Pobieranie obrazków
def pobierz_obrazki(artykul, maks=3):
    html = pobierz_zawartosc(artykul)
    obrazki = znajdz_wzorce(wzorzec_odn_obrazek, html, maks=maks)
    return obrazki

# Pobieranie linków wewnętrznych
def pobierz_linki_wewn(artykul, maks=5):
    html = pobierz_zawartosc(artykul)
    linki_wewn = znajdz_wzorce(wzorzec_odn_wewn, html, maks=maks)
    return linki_wewn
# Pobieranie linków zewnętrznych
def pobierz_linki_zewnetrzne(artykul, maks=3):
    html = pobierz_przyp_html(artykul)
    zewnetrzne_linki = znajdz_wzorce(wzorzec_odn_zewnetrzny, html, maks=maks)
    return zewnetrzne_linki

# Pobieranie listy kategorii do artykułu
def pobierz_kategorie(artykul, maks=3):
    html = pobierz_kat_html(artykul)
    kategorie = znajdz_wzorce(wzorzec_odn_kategoria, html, maks=maks)
    return kategorie
# Formatowanie i wyświetlanie danych
def wyswietl_wynik(lista_elementow):
    wynik = ' | '.join(lista_elementow).strip()  #usuwanie zbędnych spacji!
    print(wynik)

# Wzorce wyr. regularnych -regex
wzorzec_odn_artykul = r'<li[^>]*>.*<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>.*</li>'
wzorzec_odn_kategoria = r'<a[^>]*href=\"(/wiki/Kategoria:[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
wzorzec_odn_obrazek = r'<img[^>]*src=\"(//upload\.wikimedia\.org/[^"]+)\"[^>]*/>'
wzorzec_odn_zewnetrzny = r'<a[^>]*class=\"external[^"]*\"[^>]*href=\"([^"]+)\"[^>]*>'
wzorzec_odn_wewn = r'<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'

def main():
    kat = input().strip()
    artykuly = pobierz_artykuly_z_kategorii(kat)
    for link_art, tytul_art in artykuly:
        tresc = pobierz_zawartosc_artykulu(link_art)

        # Zbieranie, formatowanie wyników
        linki_wewn = pobierz_linki_wewn(tresc)
        wyswietl_wynik([elem[1] for elem in linki_wewn])
        obrazki = pobierz_obrazki(tresc)
        wyswietl_wynik([elem[0] for elem in obrazki])
        linki_zewn = pobierz_linki_zewnetrzne(tresc)
        wyswietl_wynik([elem[0] for elem in linki_zewn])
        kategorie = pobierz_kategorie(tresc)
        wyswietl_wynik([elem[1].removeprefix('Kategoria:') for elem in kategorie])

if __name__ == '__main__':
    main()
