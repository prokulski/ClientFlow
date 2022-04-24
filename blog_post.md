# Sklep rozproszony

Od kilku lat zajmuję się przede wszystkim wymyślaniem *jak coś ma działać*, opisywaniem tego i oddawaniem do zespołu developerskiego. Głównie są to rzeczy związane z real-time'owym działaniem systemów wszelakich. I dzisiaj przykład takiego działania. Dodatkowo - próbowałem napisać kod tak, żeby był łatwy do rozbudowy.

## O co chodzi?

Zbudujemy coś na kształt prostego sklepu internetowego. Całość oparta będzie zbudowana w nowoczesny (a przynajmniej tak się mówi na konferencjach, a jest to właściwie *jedyny słuszny* sposób) sposób, komponenty będą od siebie nie zależne, a kod w zamyśle ma wspierać taką niezależność.

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

Dlaczego dwie? W praniu wyszło że przy zakupie dodajemy produkt niejako *tu i teraz* (o aktualnej cenie), ale przy listowaniu tego co wykonał klient w przeszłości (wyciągając dane z bazy) może być tak, że cena produktu mogła być inna niż aktualnie. A nie chcemy zgubić informacji o cenie po której klient zakupił nasz produkt - przecież możemy chcieć kiedyś analizować czy niższa cena przekłada się na większą liczbę kupowanych produktów. Albo po prostu zobaczyć jak wyglądała zmiana cen na przestrzeni czasu (przy obecnej inflacji to modny temat ;-).

Ten drugi element można spokojnie zrealizować trzymając historię zmian ceny przy produkcie - w prezentowanym rozwiązaniu tego nie robimy.

## Pas transmisyjny

Zanim przygotujemy listę naszych klientów czas na inferface'y komunikacyjne. Do tego użyjemy Kafki (chociaż w repozytorium są skrypty pozwalające na działanie bez Kafki).

Co to jest **Apache Kafka**? W dużym uproszczeniu to taki nasz pas transmisyjny. Pas który może mieć wiele kanałów (tzw. *topików*) do których (każdego z tych topików) może pisać wielu nadawców (*producerów* czy też *producentów*) i z drugiej strony może to czytać wielu odbiorców (*konsumentów* czy *consumerów*). Co więcej - wielu może pisać do jednego topiku, wielu może czytać z jednego topika (i Kafka pilnuje kto ile przeczytał), a wszystko dzieje się niezależnie, każdy w swoim tempie. Dodatkowo Kafka trzyma na topikach komunikaty przez jakiś czas (określony w konfiguracji), jest bardzo szybka i ma jeszcze kilka innych fajnych cech.

W naszym rozwiązaniu Kafkę można zastąpić czymkolwiek. Właściwie gdyby napisać odpowiednio dostosowaną do np. REST API klasę z pliku [streaming/kafka_class.py](https://github.com/prokulski/ClientFlow/blob/main/streaming/kafka_class.py) pozostały kod powinien działać.

No dobrze, wróćmy do tego interface'u kafkowego. Użyjemy jednego topika
