**CI/CD Test Selection Tool**

**Opis Projekta**
 
CI/CD Test Selection Tool je alat koji optimizuje proces testiranja unutar CI/CD pipeline-a. Projekat se sastoji od tri glavna direktorijuma: cppcheck, selection_tool, i coverage_tool.
 
- cppcheck: Ovaj direktorijum sadrzi open source projekat Cppcheck, koji se koristi za demonstraciju znacaja i efikasnosti Selection Tool alata. Cppcheck je alat za staticku analizu C/C++ koda koji pomaze u otkrivanju razlicitih vrsta gresaka u kodu.
- selection_tool: Direktorijum koji sadrži implementaciju Selection Tool alata. Alat analizira Pull Request-ove i na osnovu pokrivenosti koda odabira testove koji trebaju biti pokrenuti na osnovu promena u kodu.
- coverage_tool: Ovde se nalazi implementacija alata za praćenje pokrivenosti koda. Alat prati koje delove koda pokrivaju pojedinacni testovi i generiše izveštaje u JSON formatu.
 
**Opis alata**
 
CI/CD Test Selection Tool je alat dizajniran za optimizaciju procesa testiranja u CI/CD pipeline-u.
Alat integrise pracenje pokrivenosti koda tokom kompajliranja i izvrsavanja testova, omogucavajuci detaljno pracenje koriscenih fajlova i funkcija za svaki pojedinacni test.
Rezultati se zatim koriste za inteligentno odabiranje testova koji trebaju biti pokrenuti za svaki Pull Request, zasnovano na promenama u kodu.


**Kako radi**
 
1. Kompajliranje sa praćenjem pokrivenosti: Projekat se kompajlira sa ukljucenom opcijom za pracenje pokrivenosti koda.
2. Izvraavanje testova: Testovi se pokrecu pojedinacno, omogucavajuci precizno pracenje koriscenja koda.
3. Parsiranje rezultata: Rezultati pokrivenosti se parsiraju i transformišu u JSON datoteke koje sadrze mape test-funkcija.
4. Arhiviranje snapshot-ova: Mape se arhiviraju kao snapshot-ovi pod jedinstvenim identifikatorom poslednjeg commit-a.

**Selekcija testova**
 
Alat dodaje dodatni stage u Jenkins CI/CD tok koji analizira Pull Request i identifikuje promenjene funkcije. Selekcija testova se vrsi na osnovu:
 
  - Analize Pull Request-a: Prepoznavanje promenjenih funkcija na osnovu razlika izmedju novih commit-ova i baznog stanja koda.
  - Odabir snapshot-a: Biranje odgovarajuceg snapshot-a iz arhive na osnovu vremenske blizine baznoj liniji spajanja.

**Sigurnosna provera**
 
Ukoliko odgovarajuci snapshot nije dostupan ili je stariji od definisanog vremenskog limita, sistem prelazi na izvrsavanje svih testova kako bi se osigurala pouzdanost procesa.
 
