# CPU Cache Benchmark Lab — Deney Sonuçları

## 1. Deneyin Amacı

Bu deneyde, aynı sayısal dizinin elemanlarına **sıralı (sequential)** ve **rastgele sıralanmış indeksler üzerinden (random)** erişildiğinde geçen süreler karşılaştırılmıştır. Amaç, bellek erişim düzeninin performansla ilişkisini gözlemlemek ve olası CPU cache etkilerini tartışmaktır.

> **Önemli:** Bu çalışma doğrudan cache hit/cache miss sayısını ölçmez. Süre farkları yalnızca CPU cache'e bağlanamaz; Python yorumlayıcısı ve indeksleme işlemleri de sonuçları etkiler.

## 2. Test Ortamı

| Özellik                | Bilgi                                                              |
| ---------------------- | ------------------------------------------------------------------ |
| İşletim sistemi        | Windows (Git Bash terminali)                                       |
| Python                 | 3.12                                                               |
| Çalıştırma komutu      | `py main.py`                                                       |
| İşlemci (CPU)          | Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz                          |
| RAM kapasitesi         | 17.041.707.008 bayt (≈ 15,87 GiB; yaklaşık 16 GB)                  |
| CPU cache kapasiteleri | L1 Data: 32 KB/çekirdek; L2: 256 KB/çekirdek; L3: 12 MB paylaşımlı |

### 2.1. İşlemci ve cache boyutlarının yorumu

Intel'in resmî ürün sayfasına göre i7-10750H, **6 çekirdek / 12 thread**, **2,60 GHz temel frekans**, **5,00 GHz'e kadar turbo** ve **12 MB Intel Smart Cache** özelliklerine sahiptir. L1/L2 dağılımı için bağımsız işlemci özellik kaynakları da kullanılmıştır.

- **100.000 eleman → ≈ 0,8 MB:** Dizinin verisi L3 cache kapasitesinden küçüktür; bunun tüm verinin sürekli cache'te kalacağı anlamına gelmediğini unutmak gerekir.
- **1.000.000 eleman → ≈ 8 MB:** Dizinin verisi 12 MB L3 kapasitesinden küçüktür; ancak Python'un indeks listesi ve diğer çalışma verileri toplam bellek ayak izini büyütür.
- **5.000.000 eleman → ≈ 40 MB:** Yalnızca dizinin verisi bile 12 MB L3 cache kapasitesini aşar.

Kaynaklar: [Intel i7-10750H resmî özellikleri](https://www.intel.com/content/www/us/en/products/sku/201837/intel-core-i710750h-processor-12m-cache-up-to-5-00-ghz/specifications.html), [PassMark cache seviye bilgileri](https://www.cpubenchmark.net/cpu.php?cpu=i7-10750H).

## 3. Ölçüm Yöntemi

- Veri, Python standart kütüphanesindeki `array("q")` ile oluşturuldu. Bu tür, her elemanı 8 baytlık işaretli tamsayı olarak saklar.
- Sıralı erişimde indeksler `0`'dan `SIZE - 1`'e doğru ziyaret edildi.
- Rastgele erişimde `0` ile `SIZE - 1` arasındaki indeksler önceden oluşturulup `random.shuffle()` ile karıştırıldı; böylece her eleman bir turda **tam bir kez** ziyaret edildi.
- Dizi oluşturma ve indeksleri karıştırma süresi erişim ölçümüne dahil edilmedi.
- Her dizi büyüklüğü için iki yöntem **5'er kez** ölçüldü; zaman ölçümünde `time.perf_counter()` kullanıldı.
- İki erişim yönteminin aynı elemanları işlediği, biriktirilen toplamların eşitliğiyle kontrol edildi.
- Nihai karşılaştırmada beş ölçümün **medyanı** kullanıldı.

## 4. Ham Ölçümler

Sürelerin tamamı **saniye** cinsindendir. Bu bölümde yalnızca en son gerçekleştirilen deneylerin çıktıları kullanılmıştır.

### 4.1. 100.000 Eleman

Yaklaşık dizi veri boyutu: **0,8 MB** (indeks listesinin ek bellek maliyeti hariç).

|     Tekrar | Sequential (s) | Random (s) |
| ---------: | -------------: | ---------: |
|          1 |         0.0201 |     0.0232 |
|          2 |         0.0193 |     0.0296 |
|          3 |         0.0201 |     0.0222 |
|          4 |         0.0203 |     0.0329 |
|          5 |         0.0208 |     0.0266 |
| **Medyan** |     **0.0201** | **0.0266** |

**Random / Sequential:** **1,32×**.

### 4.2. 1.000.000 Eleman

Yaklaşık dizi veri boyutu: **8 MB** (indeks listesinin ek bellek maliyeti hariç).

|     Tekrar | Sequential (s) | Random (s) |
| ---------: | -------------: | ---------: |
|          1 |         0.1602 |     0.3430 |
|          2 |         0.1546 |     0.2964 |
|          3 |         0.1287 |     0.2921 |
|          4 |         0.1642 |     0.3214 |
|          5 |         0.1405 |     0.2601 |
| **Medyan** |     **0.1546** | **0.2964** |

**Random / Sequential:** **1,92×**.

### 4.3. 5.000.000 Eleman

Yaklaşık dizi veri boyutu: **40 MB** (indeks listesinin ek bellek maliyeti hariç).

|     Tekrar | Sequential (s) | Random (s) |
| ---------: | -------------: | ---------: |
|          1 |         0.9551 |     1.7908 |
|          2 |         0.7124 |     1.4854 |
|          3 |         0.6110 |     1.6420 |
|          4 |         0.6245 |     1.3260 |
|          5 |         0.5895 |     1.2964 |
| **Medyan** |     **0.6245** | **1.4854** |

**Random / Sequential:** **2,38×**.

## 5. Sonuçların Karşılaştırılması

| Eleman sayısı | Dizi veri boyutu | Sequential medyan (s) | Random medyan (s) | Random / Sequential |
| ------------: | ---------------: | --------------------: | ----------------: | ------------------: |
|       100.000 |         ≈ 0,8 MB |                0.0201 |            0.0266 |               1,32× |
|     1.000.000 |           ≈ 8 MB |                0.1546 |            0.2964 |               1,92× |
|     5.000.000 |          ≈ 40 MB |                0.6245 |            1.4854 |               2,38× |

Oran şu şekilde hesaplandı:

`Random / Sequential = random_median / sequential_median`

Bu deneylerde rastgele erişim, üç veri boyutunun tamamında sıralı erişimden daha uzun sürdü. Ölçülen süre oranı, veri boyutu büyüdükçe **1,32× → 1,92× → 2,38×** olarak arttı. Bu eğilim yalnızca gerçekleştirilen ölçümler için geçerlidir; başka bilgisayarlarda veya dizi boyutlarında mutlaka aynı sonucu vereceği garanti değildir.

## 6. Teknik Yorum

Sıralı erişim, bellekte yakın konumdaki elemanların art arda okunmasını sağlar. Bu erişim deseni **mekânsal yerellik (spatial locality)** ve işlemcinin **önceden getirme (prefetching)** mekanizmalarından yararlanabilir. Rastgele erişimde ise bir sonraki elemanın bulunduğu konum daha az öngörülebilirdir; daha çok cache miss oluşması olasıdır.

Bununla birlikte deney, cache miss sayısını doğrudan toplamadığı için gözlenen farkın ne kadarının cache'ten kaynaklandığını belirleyemez. Rastgele indeks listesinin okunması, Python döngüsü ve indeksleme davranışları da performansı etkiler. Özellikle karıştırılan Python indeks listesi, sayısal diziden farklı bir veri yerleşimine ve ek bellek erişimlerine yol açar.

## 7. Deneyin Sınırlılıkları

1. **Doğrudan cache sayacı yok:** L1/L2/L3 cache miss ve hit sayıları ölçülmedi.
2. **Python maliyeti:** Yorumlayıcı, döngü ve indeksleme işlemleri toplam süreye dahildir.
3. **Erişim kodları tamamen eşdeğer değil:** Sequential bölümde `range(SIZE)`, random bölümde önceden hazırlanmış `indices` listesi dolaşılıyor; bu, cache dışındaki ek bir farktır.
4. **Ek bellek tüketimi:** Random erişim için kullanılan Python `list` indeksleri ayrıca RAM tüketir; yukarıdaki 0,8/8/40 MB değerleri sadece `array("q")` verisine aittir.
5. **Çalıştırma sırası sabit:** Her tekrarda önce sequential, sonra random çalıştırıldı. Isınma ve cache durumu sonucu etkileyebilir.
6. **Tek karıştırma sırası:** Her dizi boyutunda bir karışık indeks dizisi hazırlanıp beş tekrarda kullanıldı.
7. **Ölçüm oynaklığı:** İşletim sistemi etkinlikleri, CPU frekansı ve arka plan süreçleri süreleri değiştirebilir.

## 8. Sonuç

Bu laboratuvar çalışmasında üç farklı veri boyutunda yapılan tekrarlı ölçümlerin tamamında, **medyan rastgele erişim süresi medyan sıralı erişim süresinden daha yüksek** bulundu. En büyük veri kümesinde rastgele erişim yaklaşık **2,38 kat** daha fazla süre aldı.

Bulgular, erişim düzeninin performansı etkileyebildiğini ve CPU cache yerelliğinin önemli bir açıklama olabileceğini gösteriyor. Ancak mevcut Python benchmark'ı, farkın yalnızca cache miss'lerden kaynaklandığını **kanıtlamaz**. Daha ileri bir çalışma için eşdeğer indeks döngüleriyle kontrollü test veya daha düşük seviyeli bir dil ve donanım performans sayaçları kullanılabilir.
