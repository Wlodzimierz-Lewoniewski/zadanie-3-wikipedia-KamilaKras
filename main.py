import re
import requests
import itertools

def pobierz_dane_artykulu(html: str) -> tuple[str, str]:
    """
    Pobiera i zwraca tekst główny artykułu oraz sekcję przypisów.
    """
    tekst_ciala_artykulu = html[html.find('<div id="mw-content-text"'):html.find('<div id="catlinks"')]
    html_przypisy = html[html.find('id="Przypisy"'):]
    html_przypisy = html_przypisy[:html_przypisy.find('<div class="mw-heading"')]
    return tekst_ciala_artykulu, html_przypisy


def pobierz_kategorie_art(html: str) -> str:
    """
    Pobiera sekcję kategorii z HTML artykułu.
    """
    return html[html.find('<div id="catlinks"'):]


def znajdz_w_limicie(wzorzec: str, tekst: str, flaga: int = 0, limit: int = 5) -> list:
    """
    Znajduje do `limit` wystąpień wzorca regex w podanym tekście.
    """
    return list(map(lambda m: m.groups(), itertools.islice(re.finditer(wzorzec, tekst, flags=flaga), limit)))


def pobierz_artykuly_z_kategorii(kategoria: str, limit: int = 3) -> list[tuple[str, str]]:
    """
    Pobiera listę artykułów z danej kategorii na Wikipedii.
    """

    def odnosnik_artykul():
        # Wyrażenie regularne do wyłapywania artykułów
        return r'<li[^>]*>.*?<a[^>]*href=\"(/wiki/(?![^":]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>.*?</li>'

    url_strony_kategorii = pobierz_url_kategorii(kategoria)
    odpowiedz = requests.get(url_strony_kategorii)
    html = odpowiedz.text
    artykuly = znajdz_w_limicie(odnosnik_artykul(), html, limit=limit)
    return artykuly

def pobierz_linki_wewnetrzne(artykuł: str, limit: int = 5) -> list[tuple[str, str]]:
    """
    Pobiera listę wewnętrznych linków w artykule.
    """

    def odnosnik_wewnetrzny():
        # Wyrażenie regularne do wewnętrznych linków
        return r'<a[^>]*href=\"(/wiki/(?![^":]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'

    html = pobierz_dane_artykulu(artykuł)[0]
    linki = znajdz_w_limicie(odnosnik_wewnetrzny(), html, limit=limit)
    return linki


def pobierz_obrazki(artykuł: str, limit: int = 3) -> list:
    """
    Pobiera listę obrazków z artykułu.
    """

    def odnosnik_obrazek():
        # Wyrażenie regularne do linków obrazków
        return r'<img[^>]*src=\"(//upload\.wikimedia\.org/[^"]+)\"[^>]*/?>'

    html = pobierz_dane_artykulu(artykuł)[0]
    obrazki = znajdz_w_limicie(odnosnik_obrazek(), html, limit=limit)
    return obrazki


def pobierz_linki_zewnetrzne(artykuł: str, limit: int = 3) -> list:
    """
    Pobiera listę zewnętrznych linków w artykule.
    """

    def odnosnik_zewnetrzny():
        # Wyrażenie regularne do zewnętrznych linków
        return r'<a[^>]*class=\"external[^"]*\"[^>]*href=\"([^"]+)\"[^>]*>'


    html = pobierz_dane_artykulu(artykuł)[1]
    odnośniki = znajdz_w_limicie(odnosnik_zewnetrzny(), html, limit=limit)
    return odnośniki


def pobierz_kategorie(artykuł: str, limit: int = 3) -> list:
    """
    Pobiera listę kategorii przypisanych do artykułu.
    """

    def odnosnik_kategoria():
        # Wyrażenie regularne do linków kategorii
        return r'<a[^>]*href=\"(/wiki/Kategoria:[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'

    html = pobierz_kategorie_art(artykuł)
    kategorie = znajdz_w_limicie(odnosnik_kategoria(), html, limit=limit)
    return kategorie

def pobierz_artykul(url_artykulu: str) -> str:
    odpowiedz = requests.get("https://pl.wikipedia.org" + url_artykulu)
    html = odpowiedz.text
    return html
def pobierz_url_kategorii(kategoria: str) -> str:
    """
    Tworzy URL dla danej kategorii na Wikipedii.
    """
    przetworzona_kategoria = kategoria.replace(' ', '_')
    return f'https://pl.wikipedia.org/wiki/Kategoria:{przetworzona_kategoria}'


def formatowanie_wyniku(iterable):
    """
    Formatuje wynik iterowalny jako ciąg znaków z separatorem ` | `.
    """
    polaczone = ' | '.join(iterable)
    print(polaczone)


def main():
    """
    Funkcja główna pobierająca artykuły z kategorii i wyświetlająca ich treść, linki i obrazy.
    """
    kategoria = input().strip()
    artykuly = pobierz_artykuly_z_kategorii(kategoria)
    for link_artykulu, tytul_artykulu in artykuly:
        artykul = pobierz_artykul(link_artykulu)
        tekst_ciala_artykulu, html_przypisy = pobierz_dane_artykulu(artykul)
        linki_wewnetrzne = pobierz_linki_wewnetrzne(artykul)
        obrazki = pobierz_obrazki(artykul)
        linki_zewnetrzne = pobierz_linki_zewnetrzne(artykul)
        kategorie = pobierz_kategorie(artykul)

        formatowanie_wyniku(map(lambda x: x[1], linki_wewnetrzne))
        formatowanie_wyniku(map(lambda x: x[0], obrazki))
        formatowanie_wyniku(map(lambda x: x[0], linki_zewnetrzne))
        formatowanie_wyniku(map(lambda x: x[1].removeprefix('Kategoria:'), kategorie))


if __name__ == '__main__':
    main()
