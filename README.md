# Sklep zdarzeniowy

Projekt to *proof of concept* sklepu opartego o rozproszoną architekturę i komunikację poprzez Kafkę. Bardziej precyzyjny opis znajduje się na [blogu](https://blog.prokulski.science).

W sklepie mogą się pojawić przykładowe zdarzenia:

+ operator sklepu dodaje produkt do listy dostępnych w sklepie produktów
+ klient rejestruje się w sklepie i od teraz może robić zakupy
+ klient kupuje produkt i tym samym dodaje go listy posiadanych rzeczy

## Użycie

1. Klonujemy repozytorium
1. Tworzymy środowisko wirtualne (Python 3.9+) np. przez `virtualenv venv`
1. Aktywujemy środowisko wirtualne przez `source venv/bin/activate`
1. Instalujemy potrzebne pakiety przez `pip install -r requirements.txt`
1. Uruchamiamy potrzebne komponenty (Apache Kafka + MongoDB) przez `docker-compose up -d`

### Stworzenie klientów

Na początek potrzebujemy przykładowych klientów. Tworzymy ich przez `python tools/make_customers_db.py`

Listę klientów możemy podejrzeć przez `python tools/list_customers.py`

### Stworzenie produktów

Podobnie tworzymy przykładowe produkty dostępne w sklepie `python tools/make_products_db.py`

Listę dostępnych produktów zobaczymy dzięki `python tools/list_products.py`

## Flowchart całego procesu

```mermaid
flowchart 
    Sklep[Operator sklepu] --> NowyProdukt[/dodanie produktu/];
    Klient[Klient sklepu] --> NowyKlient[/rejestracja klienta/];
    Klient --> ZakupProduktu[/zakup produktu/];
    NowyProdukt --> PreprocesingIn{Zdefiniowanie akcji}
    NowyKlient --> PreprocesingIn;
    ZakupProduktu --> PreprocesingIn;
    PreprocesingIn --> Kafka{{pas transmisyjny - Apache Kafka}};
    Kafka --> PreprocesingOut{Rozpoznanie akcji};
    PreprocesingOut --> DodanieKlienta[/nowy klient/];
    PreprocesingOut --> DodanieProduktu[/nowy produkt w sklepie/];
    PreprocesingOut --> UpdateProduktu[/zakup produktu/];
    DodanieKlienta --> BazaKlient[(Baza danych klientów)];
    UpdateProduktu --> BazaKlient
    DodanieProduktu --> BazaProd[(Baza danych produktów)];
```

Działanie poszczególnych zdarzeń w szczegółach opisują kolejne punkty.

### Dodanie produktu do oferty sklepu

```mermaid
flowchart LR
    LoadClient[przygotowanie produktu] --> SaveProduct[/dodanie produktu do listy produktów w sklepie/];
    SaveProduct --> BazaProd[(Baza danych produktów)];
```

### Rejestracja klienta w sklepie

```mermaid
flowchart LR
    PrepareClient[przygotowanie klienta] --> SaveClient[/zapisanie klienta/];
    SaveClient --> BazaKlient[(Baza danych klientów)];
```

### Zakup produktu przez klienta

```mermaid
flowchart LR
    BazaKlient[(Baza danych klientów)] --> LoadClient[/pobranie klienta/];
    LoadClient --> UpdateClient[/dodanie produktu do listy produktów klienta/];
    UpdateClient --> SaveClient[/zapisanie klienta/];
    SaveClient --> BazaKlient;
```
