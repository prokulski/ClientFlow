# Flow

Coś generuje różne eventy na kafkę

+ nowy produkt
+ nowy klient
+ klient kupuje produkt

Coś innego odbiera te eventy i odpowiednio na nie reaguje:

+ dodaje produkt do listy dostępnych produktów
+ dodaje klienta do listy klientów
+ dodaje produkt do listy kupionych przez klienta rzeczy

## Flowchart całego procesu

```mermaid
flowchart 
    Sklep[Operator sklepu] --> NowyProdukt[/dodanie produktu/];
    Klient[Klient sklepu] --> NowyKlient[/rejestracja klienta/];
    Klient --> ZakupProduktu[/zakup produktu/];
    NowyProdukt --> Kafka{{pas transmisyjny}};
    NowyKlient --> Kafka;
    ZakupProduktu --> Kafka;
    Kafka --> Preprocesing{Rozpoznanie akcji};
    Preprocesing --> DodanieKlienta[/nowy klient/];
    Preprocesing --> DodanieProduktu[/nowy produkt w sklepie/];
    Preprocesing --> UpdateProduktu[/zakup produktu/];
    DodanieKlienta --> BazaKlient[(Baza danych klientów)];
    UpdateProduktu --> BazaKlient
    DodanieProduktu --> BazaProd[(Baza danych produktów)];
```

## Dodanie produktu do oferty sklepu

```mermaid
flowchart LR
    LoadClient[przygotowanie produktu] --> SaveProduct[/dodanie produktu do listy produktów w sklepie/];
    SaveProduct --> BazaProd[(Baza danych produktów)];
```



## Rejestracja klienta w sklepie

```mermaid
flowchart LR
    PrepareClient[przygotowanie klienta] --> SaveClient[/zapisanie klienta/];
    SaveClient --> BazaKlient[(Baza danych klientów)];
```

## Zakup produktu przez klienta

```mermaid
flowchart LR
    BazaKlient[(Baza danych klientów)] --> LoadClient[/pobranie klienta/];
    LoadClient --> UpdateClient[/dodanie produktu do listy produktów klienta/];
    UpdateClient --> SaveClient[/zapisanie klienta/];
    SaveClient --> BazaKlient;
```

