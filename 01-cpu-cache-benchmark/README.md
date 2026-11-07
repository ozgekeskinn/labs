# CPU Cache Benchmark Lab

**Sıralı ve rastgele bellek erişiminin performans karşılaştırması**

Bu laboratuvar çalışmasında, aynı sayısal dizinin elemanlarını iki farklı sırayla okuyarak bellek erişim düzeninin çalışma süresine etkisini inceledim. Python ile gerçekleştirdiğim deneyde **sequential access** (sıralı erişim) ve **random access** (rastgele erişim) yöntemlerini üç farklı veri boyutunda, beşer tekrarla ölçtüm. Elde edilen sonuçları CPU cache, mekânsal yerellik ve bellek erişim maliyetleri açısından yorumladım.

> **Önemli ayrım:** Çalışma, doğrudan CPU cache hit/miss sayılarını değil, Python programının geçen süresini ölçer. Bu nedenle gözlenen farkın tamamının cache miss nedeniyle oluştuğunu iddia etmem.

## İçindekiler

1. [Projenin Amacı](#1-projenin-amacı)
2. [Teorik Arka Plan: CPU, RAM ve Cache](#2-teorik-arka-plan-cpu-ram-ve-cache)
3. [Sequential ve Random Access Arasındaki Fark](#3-sequential-ve-random-access-arasındaki-fark)
4. [Deney Tasarımı ve Kullanılan Araçlar](#4-deney-tasarımı-ve-kullanılan-araçlar)
5. [Proje Yapısı ve Çalıştırma](#5-proje-yapısı-ve-çalıştırma)
6. [Test Ortamı](#6-test-ortamı)
7. [Benchmark Sonuçları](#7-benchmark-sonuçları)
8. [Sonuçların Teknik Analizi](#8-sonuçların-teknik-analizi)
9. [Deneyin Sınırlılıkları](#9-deneyin-sınırlılıkları)
10. [Kazanımlar ve Sonuç](#10-kazanımlar-ve-sonuç)
11. [Kaynaklar](#11-kaynaklar)

---

## 1. Projenin Amacı

Modern işlemciler ana bellekteki (RAM) verilere doğrudan erişmek yerine mümkün olduğunca cache seviyelerinden yararlanmaya çalışır. Bu nedenle **bir verinin bellekte nerede bulunduğu kadar, o veriye hangi sırayla erişildiği de** performansı etkileyebilir.

Bu çalışmada yanıt aradığım sorular:

- Aynı dizideki bütün elemanları sıralı ve rastgele sırayla okuduğumda süreler nasıl değişiyor?
- Dizi boyutu büyüdükçe iki erişim yöntemi arasındaki fark nasıl değişiyor?
- Bu farkı CPU cache, bellek yerelliği ve prefetching kavramlarıyla nasıl açıklayabilirim?
- Python ile yapılan bir zaman ölçümünden hangi sonuçları çıkarabilirim, hangilerini çıkaramam?

**Hipotez:** Sıralı erişimin, komşu bellek adreslerini düzenli olarak ziyaret etmesi nedeniyle çoğu durumda daha avantajlı olması beklenir. Veri kümesi büyüdükçe rastgele erişimin göreli maliyeti artabilir; ancak bu eğilim her koşulda garanti değildir.

## 2. Teorik Arka Plan: CPU, RAM ve Cache

### 2.1. CPU ve RAM neden farklı hızlarda çalışır?

**CPU (Central Processing Unit)** programdaki talimatları yürütür ve veriler üzerinde işlem yapar. **RAM (Random Access Memory)**, çalışan programların veri ve kodlarını barındıran ana bellektir.

İşlemci çok hızlı çalışmasına rağmen verinin RAM'den gelmesini beklemek zorunda kaldığında yürütme gecikebilir. Bu hız farkının etkisini azaltmak için işlemciye yakın, daha küçük ve daha hızlı **cache bellekleri** kullanılır.

### 2.2. CPU cache seviyeleri

Genel olarak aşağıdaki bellek hiyerarşisi söz konusudur:

```text
CPU çekirdeği
    |
    v
L1 Cache  -> küçük, çok hızlı
    |
    v
L2 Cache  -> L1'e göre daha büyük
    |
    v
L3 Cache  -> genellikle çekirdekler arasında paylaşımlı
    |
    v
RAM       -> kapasitesi yüksek, erişim gecikmesi daha fazla
```

Bu şema kavramsaldır; gerçekte veri akışı ve cache seviyelerinin organizasyonu mimariye göre daha karmaşıktır.

**Cache hit:** İstenen veri hedef cache seviyesinde bulunur; bir sonraki bellek seviyesine gitmeye gerek kalmayabilir.

**Cache miss:** İstenen veri o cache seviyesinde bulunmaz; daha alt bir cache seviyesine veya RAM'e başvurmak gerekebilir. Bu da erişim gecikmesini artırabilir.

### 2.3. Cache line nedir?

Cache, çoğunlukla verileri tek tek sayılar hâlinde değil, **cache line** denen bloklarla taşır. Modern x86 işlemcilerde yaygın cache line boyutu **64 byte**'tır.

Bu deneyde kullanılan `array("q")` elemanları 8 byte olduğundan, örnek olarak 64 byte'lık bir cache line içinde **8 ardışık sayı** bulunabilir (uygun hizalama varsayımıyla).

```text
64 byte'lık örnek cache line
+----+----+----+----+----+----+----+----+
| 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  |
+----+----+----+----+----+----+----+----+
   8 byte x 8 eleman = 64 byte
```

Dizinin ilk elemanı okunurken aynı cache line içindeki komşu elemanlar da getirilebildiği için sonraki sıralı erişimler bundan yararlanabilir.

### 2.4. Spatial ve temporal locality

**Spatial locality (mekânsal yerellik):** Bir bellek adresine erişildikten sonra yakın adreslere de erişilme eğilimidir. Dizi elemanlarının art arda okunması buna örnektir.

**Temporal locality (zamansal yerellik):** Yakın zamanda erişilen bir veriye tekrar erişilme eğilimidir. Aynı değişkenin veya veri kümesinin sık kullanılması buna örnektir.

**Hardware prefetching:** İşlemcinin düzenli erişim desenlerini algılayıp sonraki verileri ihtiyaç duyulmadan önce getirmeye çalışmasıdır. Sıralı erişim, bu mekanizmadan genellikle daha iyi yararlanabilir.

## 3. Sequential ve Random Access Arasındaki Fark

**Sequential access:** Dizinin indeksleri `0, 1, 2, 3, ...` sırasıyla dolaşılır.

**Random access:** Aynı indeksler, önceden karıştırılmış bir sırayla dolaşılır; örneğin `3, 0, 5, 1, 4, 2`.

```text
Sequential:  [0] -> [1] -> [2] -> [3] -> [4] -> [5]
Random:      [3] -> [0] -> [5] -> [1] -> [4] -> [2]
```

Her iki yöntemde de **aynı elemanlar, aynı sayıda** okunur; değişen şey erişim sırasıdır. Sıralı erişimde komşu adreslerden yararlanma olasılığı yüksektir. Rastgele erişimde ise veriler farklı cache line'lara dağılabildiğinden daha fazla cache miss oluşması **mümkündür**.

Ancak **random access = her zaman cache miss** demek doğru değildir. Verinin cache'e sığıp sığmaması, erişim örüntüsü, önceki işlemler ve işlemci mimarisi sonucu etkiler.

## 4. Deney Tasarımı ve Kullanılan Araçlar

### 4.1. Neden Python `array` kullandım?

Python'un standart `list` yapısı sayısal nesnelere referanslar tutar. `array` ise aynı türdeki temel sayısal değerleri daha kompakt ve ardışık bir veri bölgesinde saklar.

Bu projede `array("q")` kullandım: `q`, 8 byte'lık işaretli tamsayı türüdür. Dizi boyutu `SIZE` ile belirlenir.

Bu seçim, sayısal verinin yerleşimini daha anlaşılır hâle getirir; ancak Python yorumlayıcısının çalışma maliyetini ortadan kaldırmaz.

### 4.2. Erişim akışı

1. Belirlenen boyutta sayısal dizi oluşturulur.
2. `0` ile `SIZE - 1` arasındaki indeksler oluşturulur ve `random.shuffle()` ile **ölçüm başlamadan** karıştırılır.
3. Sequential erişimde tüm elemanlar artan indeks sırasıyla okunur ve toplamda biriktirilir.
4. Random erişimde aynı elemanlar karıştırılmış indeks sırasıyla okunur ve toplamda biriktirilir.
5. İki yöntemin toplamları `assert` ile karşılaştırılarak bütün elemanların doğru ziyaret edildiği kontrol edilir.
6. Her yöntem aynı veri büyüklüğünde **5 kez** ölçülür.
7. Beş ölçümün **medyanı** alınır ve `random_median / sequential_median` oranı hesaplanır.

> Karıştırma işlemini süre ölçümüne dahil etmedim. Ölçmek istediğim şey karıştırmanın kendisi değil, belirlenen sırada elemanlara erişimin maliyetidir.

### 4.3. Zaman ölçümü

Kısa süreli işlemleri ölçmek için Python'un `time.perf_counter()` fonksiyonunu kullandım. Başlangıç ve bitiş noktalarındaki sayaç değerlerinin farkı, geçen süreyi saniye cinsinden verir.

Beş ayrı ölçümden **medyan** elde etmek, tek bir yüksek/düşük ölçümün etkisini azaltır. Bununla birlikte medyan, ölçümdeki sistematik yanlılıkları otomatik olarak gidermez.

## 5. Proje Yapısı ve Çalıştırma

```text
01-cpu-cache-benchmark/
├── main.py       # Benchmark uygulaması
├── results.md    # Ham ölçümler ve teknik analiz
└── README.md     # Deneyin kapsamı ve açıklamaları
```

**Gereksinim:** Python 3.x. Kullanılan `array`, `random`, `statistics` ve `time` modülleri standart kütüphanededir; üçüncü taraf paket kurulumu gerekmez.

Proje klasöründe çalıştırma:

```bash
py main.py
```

Dizi boyutu `main.py` içindeki `SIZE` değişkeniyle değiştirilerek her bir büyüklük için program yeniden çalıştırılır. Bu çalışmada `100_000`, `1_000_000` ve `5_000_000` eleman kullanıldı.

## 6. Test Ortamı

| Bileşen           | Bilgi                                                                     |
| ----------------- | ------------------------------------------------------------------------- |
| İşletim sistemi   | Windows (Git Bash terminalinden çalıştırıldı; sürüm bilgisi kaydedilmedi) |
| Python            | 3.12                                                                      |
| İşlemci           | Intel Core i7-10750H                                                      |
| Çekirdek / Thread | 6 çekirdek / 12 thread                                                    |
| Temel frekans     | 2.60 GHz                                                                  |
| L1 Data Cache     | 32 KB / çekirdek                                                          |
| L2 Cache          | 256 KB / çekirdek                                                         |
| L3 Cache          | 12 MB (paylaşımlı, Intel Smart Cache)                                     |
| RAM kapasitesi    | 17.041.707.008 bayt (≈ 15,87 GiB; yaklaşık 16 GB)                         |
| Tekrar sayısı     | Her veri boyutu için 5                                                    |

Cache kapasiteleri işlemci özellik kaynaklarından alınmıştır; deney sırasında donanım cache sayaçları ölçülmemiştir.

## 7. Benchmark Sonuçları

Aşağıdaki sayılar **son paylaşılan ölçüm serisine** aittir. Süreler, her yöntemin beş tekrarından elde edilen medyan değerlerdir.

| Dizi boyutu | Dizi verisi | Sequential medyan | Random medyan | Süre oranı |
| ----------: | ----------: | ----------------: | ------------: | ---------: |
|     100.000 |    ≈ 0,8 MB |          0.0201 s |      0.0266 s |  **1.32×** |
|   1.000.000 |      ≈ 8 MB |          0.1546 s |      0.2964 s |  **1.92×** |
|   5.000.000 |     ≈ 40 MB |          0.6245 s |      1.4854 s |  **2.38×** |

**Süre oranı**, random medyan süresinin sequential medyan süresine bölünmesiyle hesaplanır. Örneğin 5 milyon elemanda `1.4854 / 0.6245 ≈ 2.38` bulunur. Bu, rastgele erişimin ilgili ölçüm serisinde **yaklaşık 2,38 kat daha uzun sürdüğü** anlamına gelir.

5 milyon eleman için programın ürettiği sonuç bölümü:

```text
===== BENCHMARK RESULTS =====
Sequential median: 0.6245s
Random median: 1.4854s
Random / Sequential: 2.38x
Random access is slower, potentially due to cache misses and memory access overhead.
```

**Bütün ham ölçümler ve ayrıntılı analiz:** [results.md](./results.md)

## 8. Sonuçların Teknik Analizi

### 8.1. Küçük dizide fark neden daha az olabilir?

100.000 elemanlık dizinin yalnızca sayısal verisi yaklaşık **0,8 MB** yer kaplar. Bu miktar, işlemcinin 12 MB paylaşımlı L3 cache kapasitesinden küçüktür. Küçük bir veri kümesinde cache'den yararlanmak daha kolay olabileceğinden rastgele erişimin göreli dezavantajı sınırlı kalabilir.

Ancak dizi boyutunun L3'ten küçük olması, verinin tamamının kesinlikle cache'te tutulacağı anlamına gelmez. Diğer çalışan veriler, indeks listesi ve sistemin cache kullanımı da önemlidir.

### 8.2. Büyük dizide fark neden artmış olabilir?

5 milyon `q` elemanının ham veri boyutu yaklaşık **40 MB**'tır ve işlemcinin 12 MB L3 cache kapasitesini aşar. Böyle bir veri kümesinde tüm verinin aynı anda L3 içerisinde tutulması mümkün değildir.

Sıralı erişim komşu elemanlardan ve düzenli erişim öngörüsünden yararlanabilirken rastgele erişim daha fazla farklı bellek bölgesine dağılabilir. Daha fazla cache miss ve RAM erişimi yaşanması olasıdır. **Bu, gözlenen fark için makul bir açıklamadır; tek ve kanıtlanmış neden değildir.**

### 8.3. Ölçümlerden hangi sonucu çıkardım?

Üç veri boyutunun hepsinde rastgele erişimin **medyan süresi** daha uzun çıktı. Oranlar sırasıyla **1,32×**, **1,92×** ve **2,38×** oldu. Ölçümler, bu uygulamada veri boyutu arttıkça rastgele erişimin göreli maliyetinin de arttığını gösteriyor.

Bu eğilim, bellek yerelliğinin performansa etkisiyle **uyumludur**. Fakat sadece süreye bakarak "yavaşlamanın yüzde kaçı cache miss nedeniyle oldu?" sorusu cevaplanamaz.

## 9. Deneyin Sınırlılıkları

Bu benchmark gerçek bir performans karşılaştırmasıdır; ancak kontrollü bir **donanım cache miss ölçümü** değildir.

1. **Python yorumlayıcı maliyeti:** Döngü ve indeksleme işlemleri de ölçülen süreye dahildir.
2. **Erişim yolları tam eşdeğer değil:** Sıralı erişimde `range(SIZE)` dolaşılırken rastgele erişimde ayrı bir Python indeks listesi dolaşılıyor. Bu durum cache dışındaki farkları da etkiler.
3. **Rastgele indeks listesinin ek maliyeti:** Özellikle büyük boyutta indeks listesinin kendisi önemli RAM tüketir ve Python tamsayı nesneleriyle ilişkili ilave erişimler oluşturur. Tablodaki 0,8/8/40 MB değerleri yalnızca sayısal dizinin ham verisidir.
4. **Cache hit/miss sayaçları kullanılmadı:** Hangi seviyede kaç miss gerçekleştiği doğrudan bilinmiyor.
5. **Çalıştırma sırası sabit:** Her tekrarda önce sequential, ardından random test edildi. Isınma ve önceki testin cache üzerindeki etkileri sonuçları değiştirebilir.
6. **Sistem koşulları sabit değil:** Arka plan uygulamaları, güç modu, işlemci frekansı ve işletim sistemi zamanlaması ölçümleri etkileyebilir.
7. **Tek karıştırılmış sıra:** Her boyutta oluşturulan rastgele indeks sırası beş tekrar boyunca aynı tutuldu; farklı karıştırma sıraları ayrıca test edilmedi.

### Daha ileri geliştirmeler

- Her boyutta birden fazla rastgele indeks sırası oluşturmak ve deneyler arasında erişim sırasını dönüşümlü kullanmak.
- Sequential ve random yöntemlerini aynı indeks dolaşma mekanizmasıyla tasarlayarak karşılaştırılabilirliği artırmak.
- Isınma (warm-up), daha fazla tekrar ve sonuç dağılımı gibi benchmark uygulamalarını eklemek.
- Cache davranışını daha doğrudan incelemek için C/C++ gibi daha düşük seviyeli bir dil ve uygun donanım performans sayaçlarıyla ayrı bir deney yapmak.

## 10. Kazanımlar ve Sonuç

Bu laboratuvar çalışmasında:

- CPU, RAM ve cache hiyerarşisinin neden önemli olduğunu araştırdım.
- Cache hit/miss, cache line, spatial locality ve prefetching kavramlarını erişim düzenleriyle ilişkilendirdim.
- Python'da kompakt sayısal dizi oluşturmayı ve sıralı/rastgele indeks erişimini uyguladım.
- `time.perf_counter()` ile süre ölçtüm; beş tekrarlı ölçümlerin medyanını kullandım.
- Üç veri büyüklüğünün karşılaştırmasını yaptım ve yöntemin sınırlarını değerlendirdim.

**Sonuç:** Bu bilgisayarda yapılan ölçümlerde sıralı erişim, test edilen üç boyutun tamamında rastgele erişimden daha kısa medyan süreye sahipti. En büyük veri boyutunda rastgele erişim yaklaşık **2,38 kat daha uzun** sürdü. Sonuçlar CPU cache ve erişim yerelliğinin olası önemini gösterse de Python'daki ek indeksleme ve veri yapısı maliyetleri nedeniyle farkı **yalnızca cache miss'e bağlamak doğru değildir**.

## 11. Kaynaklar

- [Intel — Core i7-10750H teknik özellikleri](https://www.intel.com/content/www/us/en/products/sku/201837/intel-core-i710750h-processor-12m-cache-up-to-5-00-ghz/specifications.html)
- [PassMark — Intel Core i7-10750H cache seviye bilgileri](https://www.cpubenchmark.net/cpu.php?cpu=i7-10750H)
- [Python 3.12 — `array` dokümantasyonu](https://docs.python.org/3.12/library/array.html)
- [Python 3.12 — `time.perf_counter()` dokümantasyonu](https://docs.python.org/3.12/library/time.html#time.perf_counter)
- [Python 3.12 — `statistics.median()` dokümantasyonu](https://docs.python.org/3.12/library/statistics.html#statistics.median)
