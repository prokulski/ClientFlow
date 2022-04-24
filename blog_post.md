# Sklep rozproszony

Od kilku lat zajmuję się przede wszystkim wymyślaniem *jak coś ma działać*, opisywaniem tego i oddawaniem do zespołu developerskiego. Głównie są to rzeczy związane z real-time'owym działaniem systemów wszelakich. I dzisiaj przykład takiego działania. Dodatkowo - próbowałem napisać kod tak, żeby był łatwy do rozbudowy.

## O co chodzi?

Zbudujemy coś na kształt prostego sklepu internetowego. Całość będzie zbudowana w nowoczesny (a przynajmniej tak się mówi na konferencjach, a jest to właściwie *jedyny słuszny*) sposób, komponenty będą od siebie niezależne, a kod w zamyśle ma wspierać taką niezależność.

Nie będzie to też jakiś bardzo zaawansowany "sklep". Ot - klienci, produkty i możliwość kupienia produktu przez klienta. Nie będzie procesu płatności, budowania koszyka zakupów i przede wszystkim - nie będzie żadnego front-endu. Będzie za to *mikroserwisowo*.

Całość kodu znajdziecie [na GitHubie](https://github.com/prokulski/ClientFlow), a tutaj przedstawię tylko kluczowe elementy. W repozytorium jest też instrukcja jak używać całości.

## Komponenty

Oprzemy się na elementach *big data*. Tak więc dane będziemy trzymać w bazie typu NoSQL - tutaj będzie to MongoDB. Do komunikacji poszczególnych elementów ze sobą posłuży Apache Kafka. Oczywiście nie będziemy wszystkiego instalować, skorzystamy z gotowców w postaci **obrazów dockera**, konkretnie z *docker-compose*.

Zatem - budujemy plik [docker-compose.yml](https://github.com/prokulski/ClientFlow/blob/main/docker-compose.yml):

````yaml
version: '2'
services:
  mongodb:
    image: mongo:5.0
    ports:
      - 27017:27017
    volumes:
      - ./mongodata:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=rootpass

  zookeeper:
    image: 'bitnami/zookeeper:latest'
    ports:
      - '2181:2181'
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes

  kafka:
    image: 'bitnami/kafka:latest'
    ports:
      - '9092:9092'
      - '9093:9093'
    environment:
      - KAFKA_BROKER_ID=1
      - KAFKA_CFG_LISTENERS=PLAINTEXT://:9092
      - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092
      - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT
      - KAFKA_CFG_LISTENERS=CLIENT://:9092,EXTERNAL://:9093
      - KAFKA_CFG_ADVERTISED_LISTENERS=CLIENT://kafka:9092,EXTERNAL://localhost:9093
      - KAFKA_CFG_INTER_BROKER_LISTENER_NAME=CLIENT
    depends_on:
      - zookeeper
````

Jak widzicie korzystamy z trzech elementów: MongoDB, Kafki oraz Zookeepera (który potrzebny jest Kafce). Udostępniamy stosowne porty do komunikacji oraz podpinamy katalog `mongodata` jako miejsce w którym MongoDB będzie trzymać swoje dane. To pozwoli nam przechować dane nawet po *złożeniu* wszystkich zabawek.

Środowisko uruchamiamy przez standardową komendę `docker-compose up` (może być z `-d` jeśli chcemy wrócić do shella, ale polecam w celach edukacyjnych zostawić lecący log).

## Stworzenie klientów

Na początek tworzymy przykładowych klientów. Do opisu klienta powstała klasa **Customer** zdefiniowana jako *dataclass* w pliku [models/customers.py](https://github.com/prokulski/ClientFlow/blob/main/models/customer.py)

````python
@dataclass
class Customer:
    first_name: str
    last_name: str
    address: str
    products: List[Product] = field(default_factory=list, init=False)
    id: Optional[str] = None
````

Jak widzicie klient jest prosty - ma imię, nazwisko, adres i listę produktów. Produkty są klasy **Product** (o tym za chwilę).

Oprócz tego klasa posiada metody zwracające np. słownik (to przyda się do wysyłania na Kafkę) albo JSONa (możemy na przykład klienta zapisywać na dysku i później korzystać z tych danych w Sparku). Ma też metody pozwalające na dodanie produktów do tych posiadanych przez klienta:

````python
@dataclass
class Customer:
    def add_base_product(self, product: ProductBase, quantity: float = 0.0) -> None:
        prod = Product(**product.to_dict(), quantity=quantity)
        self.add_product(prod)

    def add_product(self, product: Product) -> None:
        self.products.append(product)
````

Dlaczego dwie? W praniu wyszło że przy zakupie dodajemy produkt niejako *tu i teraz* (o aktualnej cenie), ale przy listowaniu tego co wykonał klient w przeszłości (wyciągając dane z bazy) może być tak, że cena produktu mogła być inna niż aktualnie. A nie chcemy zgubić informacji o cenie po której klient zakupił nasz produkt - przecież możemy chcieć kiedyś analizować czy niższa cena przekłada się na większą liczbę kupowanych produktów. Albo po prostu zobaczyć jak wyglądała zmiana cen na przestrzeni czasu (przy obecnej inflacji to modny temat ;-). Czyli nie trzymamy powiązania do *id produktu* a do konkretnego *egzemplarza* tego produktu.

Analizowanie inflacji można spokojnie zrealizować trzymając historię zmian ceny przy produkcie - w prezentowanym rozwiązaniu tego nie robimy.

## Pas transmisyjny

Zanim przygotujemy listę naszych klientów czas na inferface'y komunikacyjne. Do tego użyjemy Kafki (chociaż w repozytorium są skrypty pozwalające na działanie bez Kafki).

Co to jest **Apache Kafka**? W dużym uproszczeniu to taki nasz pas transmisyjny. Pas który może mieć wiele kanałów (tzw. *topików*) do których (każdego z tych topików) może pisać wielu nadawców (*producerów* czy też *producentów*) i z drugiej strony może to czytać wielu odbiorców (*konsumentów* czy *consumerów*). Co więcej - wielu może pisać do jednego topiku, wielu może czytać z jednego topika (i Kafka pilnuje kto ile przeczytał), a wszystko dzieje się niezależnie, każdy w swoim tempie. Dodatkowo Kafka trzyma na topikach komunikaty przez jakiś czas (określony w konfiguracji), jest bardzo szybka i ma jeszcze kilka innych fajnych cech.

W naszym rozwiązaniu Kafkę można zastąpić czymkolwiek. Właściwie gdyby napisać odpowiednio dostosowaną do np. REST API klasę z pliku [streaming/kafka_class.py](https://github.com/prokulski/ClientFlow/blob/main/streaming/kafka_class.py) pozostały kod powinien działać (z dokładnością do importów tej nowej klasy i jej użycia; gimnastyka może być z *consumerem*).

No dobrze, wróćmy do tego interface'u kafkowego. Użyjemy jednego topika i trzech typów komunikatów. Poprawniej byłoby użyć trzech topików (i pilnować czy *lecący* komunikat ma odpowiednie pola), ale dlaczego nie utrudnić sobie zadania? ;-) Tak na prawdę utrudnienie to ułatwienie w kodzie - mamy jednego konsumenta topiku kafkowego, wszystko trzymamy w jednym pliku [tools/kafka_read.py](https://github.com/prokulski/ClientFlow/blob/main/tools/kafka_read.py), a pole *event_type* w komunikacie decyduje co się dzieje dalej:

````python
for msg in kafka_consumer:
    try:
        eh = EventHandler(msg.value, db)
    except Exception as e:
        print(f"Exception: {e}")
        print(msg)
````

Precyzyjniej rzecz biorąc - decyzja odbywa się w klasie *[EventHandler](https://github.com/prokulski/ClientFlow/blob/main/events/events_handler.py)*.

Ale wróćmy do tworzenia naszych klientów. Do wymyślenia danych osobowych użyjemy pakietu Faker, a następnie:

1. wygenerujemy sobie kilku klientów (obiekty klasy *Customer*),
1. każdego przetworzymy na typ *dict*
1. *producer* zamieni (zserializuje) to na JSON
1. i to tym formatem poleci komunikat kafkową rurą jako komunikat o **event_type = "new_customer"**

Niejako *z drugiej strony* (jako *consumer*) kafkowego topika będzie nasłuchiwacz (wspomniany już skrypt [tools/kafka_read.py](https://github.com/prokulski/ClientFlow/blob/main/tools/kafka_read.py)) który odpowiednio zareaguje, czyli:

1. pobierze komunikat z kafkowego topika
1. *consumer* rozkoduje JSONa do *dict*
1. taki obiekt typu *dict* zostanie przetworzony na obiekt klasy **EventHandler**
1. inicjalizacja w ramach klasy *EventHandler* wywoła odpowiednią dla *event_type* metodę
1. powstanie obiekt klasy *Customer*
1. i zostanie zapisany do bazy danych

Ufff... drobiazgowy proces. Po co tworzyć obiekt *Customer*, serializować do JSONa, wysyłać, potem odbierać i z JSONa robić znowu *Customer*-a? Po to, żeby to było niezależne od siebie.

Gdybyśmy od razu zamiast po drodze używać Kafki wysyłali *Customer*-ów do bazy danych, a ta przestałaby działać to byłby kłopot. A tak - Kafka może przyjąć dane i je przytrzymać do póki nie zostaną odczytane. W między czasie bazę można naprawić albo i postawić nową (nawet innego typu!).

W repozytorium jest rozwiązanie pchające dane [do bazy bezpośrednio](https://github.com/prokulski/ClientFlow/blob/main/tools/make_customers_db.py) oraz [przez Kafkę](https://github.com/prokulski/ClientFlow/blob/main/tools/make_customers_kafka.py) - porównaj oba skrypty.

## Produkty

Skoro mamy klientów i sposób przesyłania informacji to możemy zrobić produkty. Podobnie jak poprzednio - mamy odpowiednią data-klasę **Product** dziedziczącą z **ProductBase** (różnica jest prosta: *Product* to coś co klient już kupił - czyli wiadomo kiedy, ile i za ile, *ProductBase* to coś co może kupić - wiadomo co to jest i ile kosztuje w tym momencie):

````python
@dataclass
class ProductBase:
    name: str
    type: str
    price: float
    id: Optional[str] = None

@dataclass
class Product(ProductBase):
    quantity: float = field(default=0.0)
    timestamp: datetime = field(default_factory=datetime.utcnow)
````

Pełny kod oczywiście w repo, [models/product.py](https://github.com/prokulski/ClientFlow/blob/main/models/product.py).

### Stworzenie produktów

Podobnie jak klientów - produkty możemy stworzyć przesyłając je przez Kafkę [tools/make_products_kafka.py](https://github.com/prokulski/ClientFlow/blob/main/tools/make_products_kafka.py) albo bezpośrednio wysyłając je do bazy [tools/make_products_db.py](https://github.com/prokulski/ClientFlow/blob/main/tools/make_products_db.py). Skrypty są dość podobne ale tworzonym produktom nadają inne ID - tak, żeby dało się je łatwo odróżnić (tworzeni klienci też są do rozróżnienia po ID). Proponuję uruchomić oba skrypty, a właściwie to wszystkie cztery (po dwa na tworzenie produktów i klientów).

## Co mamy w bazie?

No właśnie - stworzyliśmy klientów, stworzyliśmy produkty. Ale czy możemy zobaczyć jak wygląda portfel klientów, co kto ma? Oczywiście na to też są gotowe skrypciki:

+ listę klientów możemy podejrzeć przez [tools/list_customers.py](https://github.com/prokulski/ClientFlow/blob/main/tools/list_customers.py) - skrypt ten nie korzysta z Kafki, czyta bezpośrednio z bazy
+ listę dostępnych produktów zobaczymy dzięki [tools/list_products.py](https://github.com/prokulski/ClientFlow/blob/main/tools/list_products.py) - podobnie - skrypt czyta bezpośrednio z bazy danych

Jak się im dobrze przyjrzeć to:

+ sposób czytania danych z bazy i zwracania obiektów typu *Customer* albo *Product* definiuje protokół **DB** zdefiniowany w [db/db.py](https://github.com/prokulski/ClientFlow/blob/main/db/db.py) a do MongoDB dostosowany w [db/mongodb.py](https://github.com/prokulski/ClientFlow/blob/main/db/mongodb.py) - można dostosować te inferfejsy np. do czytania z tabel baz relacyjnych typu PostgreSQL i wykonywania odpowiednich join-ów
+ interface czyta klienta i produkt, a potem dodaje do tego klienta produkt - za to odpowiadają metody w klasie Customer; są więc niezależne od sposobu przechowywania danych w bazie
+ klasy Customer i Product mają zdefiniowane *dunder methods* (konkretnie \_\_repr\_\_) co pozwala na obiektach robić zwykłe *print*

## Testy

Spróbujmy więc od początku - na początek mamy pusto:

````bash
$ python tools/list_customers.py
$ python tools/list_products.py
$
````

Stwórzmy więc kilku klientów od razu w bazie danych:

````bash
$ python tools/make_customers_db.py 
$ python tools/list_customers.py 
Damian Ofiara (customer_db_000) - nie ma produktów.

Roksana Siatka (customer_db_001) - nie ma produktów.

Jakub Fronczyk (customer_db_002) - nie ma produktów.

Ewelina Sobolak (customer_db_003) - nie ma produktów.

Ryszard Pietrek (customer_db_004) - nie ma produktów.

$
````

Dodajmy klientów stworzonych i przesłanych Kafką.

Ważne - w innym oknie konsoli musi być uruchomiony skrypt `tools/kafka_read.py` - inaczej dane z Kafki nie zostaną zebrane!
Ale możesz sprawdzić co się stanie - tworzenie klientów zadziała (skrypt się nie wywali), ale w bazie klientów nie będzie. Włącz później *czytacza* i zobacz czy po chwili w bazie znajdą się nowe osoby?

````bash
$ python tools/make_customers_kafka.py
$ python tools/list_customers.py 
Damian Ofiara (customer_db_000) - nie ma produktów.

Roksana Siatka (customer_db_001) - nie ma produktów.

Jakub Fronczyk (customer_db_002) - nie ma produktów.

Ewelina Sobolak (customer_db_003) - nie ma produktów.

Ryszard Pietrek (customer_db_004) - nie ma produktów.

Alex Kosiak (customer_k_000) - nie ma produktów.

Grzegorz Połom (customer_k_001) - nie ma produktów.

Anna Maria Świgoń (customer_k_002) - nie ma produktów.

Tadeusz Jędral (customer_k_003) - nie ma produktów.

Cyprian Ostapczuk (customer_k_004) - nie ma produktów.

$
````

No to teraz czas na stworzenie produktów - zróbmy je od razu na dwa sposoby:

````bash
$ python tools/make_products_db.py 
$ python tools/make_products_kafka.py 
$ python tools/list_products.py 
Produkt: "Mleko Wypasione" (mleko, cena 0.54 zł, ID mleko_db_1)
Produkt: "Łaciate" (mleko, cena 0.64 zł, ID mleko_db_2)
Produkt: "Cukier w kostkach" (cukier, cena 0.95 zł, ID cukier_db_1)
Produkt: "Cukier drobny" (cukier, cena 0.86 zł, ID cukier_db_2)
Produkt: "Milka Mleczna" (czekolada, cena 0.05 zł, ID czekolada_db_1)
Produkt: "Wedel Gorzka" (czekolada, cena 0.93 zł, ID czekolada_db_2)
Produkt: "Alpengold z orzechami" (czekolada, cena 0.29 zł, ID czekolada_db_3)
Produkt: "Alpengold mleczna" (czekolada, cena 0.47 zł, ID czekolada_db_4)
Produkt: "Chleb staropolski" (chleb, cena 0.56 zł, ID chleb_db_1)
Produkt: "Chleb wiejski" (chleb, cena 0.96 zł, ID chleb_db_2)
Produkt: "Chleb codzienny" (chleb, cena 0.23 zł, ID chleb_db_3)
Produkt: "Masło ekstra" (masło, cena 0.85 zł, ID maslo_db_1)
Produkt: "Masełko maślane" (masło, cena 0.35 zł, ID maslo_db_2)
Produkt: "Mleko Wypasione" (mleko, cena 0.32 zł, ID mleko_k_1)
Produkt: "Łaciate" (mleko, cena 0.16 zł, ID mleko_k_2)
Produkt: "Cukier w kostkach" (cukier, cena 0.92 zł, ID cukier_k_1)
Produkt: "Cukier drobny" (cukier, cena 0.36 zł, ID cukier_k_2)
Produkt: "Milka Mleczna" (czekolada, cena 0.36 zł, ID czekolada_k_1)
Produkt: "Wedel Gorzka" (czekolada, cena 0.29 zł, ID czekolada_k_2)
Produkt: "Alpengold z orzechami" (czekolada, cena 0.15 zł, ID czekolada_k_3)
Produkt: "Alpengold mleczna" (czekolada, cena 0.16 zł, ID czekolada_k_4)
Produkt: "Chleb staropolski" (chleb, cena 0.36 zł, ID chleb_k_1)
Produkt: "Chleb wiejski" (chleb, cena 0.38 zł, ID chleb_k_2)
Produkt: "Chleb codzienny" (chleb, cena 0.37 zł, ID chleb_k_3)
Produkt: "Masło ekstra" (masło, cena 0.87 zł, ID maslo_k_1)
Produkt: "Masełko maślane" (masło, cena 0.56 zł, ID maslo_k_2)
$ 
````

## Klient kupuje produkt

A teraz rzecz najważniejsza - zakupy! Co nasz system zrobi w momencie kupna produktu **P** rzez klienta **C**? Zakładamy, że te elementy istnieją w bazie.

1. z bazy danych pobrany zostaje klient **C** (tworzony jest obiekt Customer)
1. do listy jego produktów zostaje dodany **P** (jako istniejący obiekt ProductBase)
1. w bazie nadpisywany jest nowy stan **C** (można robić update - tutaj robimy jednak prosto: kasujemy i wstawiamy nowy)

Ten scenariusz realizuje skrypt [tools/customers_buys_products_db.py](https://github.com/prokulski/ClientFlow/blob/main/tools/customers_buys_products_db.py).

Jak wygląda to od strony komunikacji i interface'u? Kafką poleci komunikat o IDkach produktu i klienta i liczbie sztuk produktu, które klient kupuje. Zatem *końcówka* po drugiej stronie (czytająca z Kafki) powinna kolejno:

1. z bazy danych pobrać klienta **C** po ID
1. z bazy danych pobrać produkt **P** po jego ID
1. do listy produktów **C** zostaje dodany **P**
1. w bazie nadpisywany jest nowy stan **C**

To z kolei realizuje skrypt [tools/customers_buys_products_kafka.py](https://github.com/prokulski/ClientFlow/blob/main/tools/customers_buys_products_kafka.py). Ponieważ nie znamy pełnej listy ID produktów i klientów znajdujących się w bazie w obu przypadkach na początek wczytujemy z bazy wszystko, a potem sobie coś losujemy.

Nasz kod nie obsługuje błędów, ale patrząc zdroworozsądkowo to w procesie na przykład na front-endzie są wcześniejsze kroki:

+ klient loguje się do sklepu - musi więc istnieć, front-endowi wystarczy pamiętać dalej w sesji ID klienta
+ zakupu dokonuje się na jakieś stronie produktu - produkt więc musi istnieć, znany jest jego ID

Oczywiście to zakłada, że nie ma przerw w realizacji procesu i innych równoległych działań. Ale cały ten wpis i kod do niego to jakieś 3-4 dni roboty, więc jest to taki bardziej **proof of concept** niż coś *produkcyjnego*.

Zobaczmy jak to zadziała - niech będzie w wersji kafkowej:

````bash
$ python tools/customers_buys_products_kafka.py 
$ python tools/list_customers.py 
Grzegorz Połom (customer_k_001) - nie ma produktów.

Anna Maria Świgoń (customer_k_002) - nie ma produktów.

Jakub Fronczyk (customer_db_002) - ma następujące produkty:
 * cukier Cukier drobny (8 za 0.36 zł = 2.88 zł, kupione 2022-04-24 19:41:07)

Alex Kosiak (customer_k_000) - ma następujące produkty:
 * masło Masełko maślane (6 za 0.35 zł = 2.10 zł, kupione 2022-04-24 19:41:11)

Ryszard Pietrek (customer_db_004) - ma następujące produkty:
 * mleko Mleko Wypasione (3 za 0.32 zł = 0.96 zł, kupione 2022-04-24 19:41:15)

Tadeusz Jędral (customer_k_003) - ma następujące produkty:
 * czekolada Wedel Gorzka (2 za 0.93 zł = 1.86 zł, kupione 2022-04-24 19:41:17)

Ewelina Sobolak (customer_db_003) - ma następujące produkty:
 * masło Masło ekstra (3 za 0.85 zł = 2.55 zł, kupione 2022-04-24 19:41:19)

Cyprian Ostapczuk (customer_k_004) - ma następujące produkty:
 * chleb Chleb staropolski (6 za 0.36 zł = 2.16 zł, kupione 2022-04-24 19:41:09)
 * chleb Chleb wiejski (6 za 0.38 zł = 2.28 zł, kupione 2022-04-24 19:41:21)

Damian Ofiara (customer_db_000) - ma następujące produkty:
 * masło Masełko maślane (5 za 0.56 zł = 2.80 zł, kupione 2022-04-24 19:41:23)

Roksana Siatka (customer_db_001) - ma następujące produkty:
 * czekolada Alpengold mleczna (4 za 0.16 zł = 0.64 zł, kupione 2022-04-24 19:41:13)
 * czekolada Wedel Gorzka (9 za 0.93 zł = 8.37 zł, kupione 2022-04-24 19:41:25)

$ 
````

Mamy tych samych klientów co wcześniej, większość z nich została obdzielonych produktami - w różnych ilościach. Jeśli ceny się różnią to są to różne produkty (*Masełko maślane* u Damiana Ofiary to inne *Masełko maślane* niż u Alexa Kosiaka) - nie widać tego na wyciągach, bo poprawiłem to w kodzie już po napisaniu tekstu.

## Po co to wszystko?

Po co tak kombinować? Jakieś Kafki, przesyłanie, miliony skryptów?

A no po to, żeby nie robić *plątaniny kabli* zwanej też *spaghetti*. Załóżmy że jakiś system z boku będzie monitorował ile mamy produktów na stanie. Wystarczy że *podepnie* się pod topik kafkowy o tym co kto kupuje i policzy ile razy kupiono produkt o konkretnym ID (czyli skorzysta z ułamka informacji zawartej w komunikacie w topiku!). Z taką informacją coś można już zrobić, a nikt nie musi jej specjalnie produkować.

Tak samo możemy zebrać dane o adresach naszych klientów. Ktoś się rejestruje i jeśli jest z wybranego miasta to dzieje się jakaś akcja. nie trzeba tego robić batchowo i co jakiś czas zaglądać do bazy klientów i sobie coś weryfikować. Nie trzeba pisać specjalnego kodu że pojawił się klient z jakiegoś miasta. Trzeba przeczytać odpowiednie komunikaty z Kafki i zareagować. Od razu, a nie raz na dobę.

Dane leżą sobie w bazie - czy jest to baza relacyjna (SQL) czy NoSQL nie ma większego znaczenia - do celów raportowych pewnie lepsza byłaby relacyjna (łatwiej pisze się zapytania w SQLu). Ale takie Mongo trzyma obraz całego klienta (bo tak chcieliśmy), odpytując bezpośrednio Mongo dostaniemy na przykład coś takiego:

````json
> db.customers.find({"id":"customer_k_004"})
{
  "_id": ObjectId("6265abea043cefb88e545a15"),
  "first_name": "Cyprian",
  "last_name": "Ostapczuk",
  "address": "plac Średnia 13\n12-612 Dąbrowa Górnicza",
  "id": "customer_k_004",
  "products" :
  [
    {
      "id": "chleb_k_1",
      "type": "chleb",
      "name": "Chleb staropolski",
      "price": 0.36,
      "quantity": 6,
      "timestamp_ms": NumberLong("1650823114225")
    },
    {
      "id": "chleb_k_2",
      "type": "chleb",
      "name": "Chleb wiejski",
      "price": 0.38,
      "quantity": 6,
      "timestamp_ms": NumberLong("1650823114237")
    }
  ]
}
````

Po aktualizacji związanej z zakupami możemy ten obraz przekazać dalej - być może ktoś tego potrzebuje? Na przykład jakiś system scoringowy? Liczy na przykład ile jakich produktów klient kupił w przeciągu ostatniego miesiąca i jeśli więcej niż 25% to chleb to... daje talon na masło?

Interesujące? Trudne? Wcale nie takie trudne. Jeśli jednak masz pytania - śmiało, pisz w komentarzu.
