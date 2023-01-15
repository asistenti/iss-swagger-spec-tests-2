Za pokretanje testova je neophodno imati instaliran python (pozeljno neku od novijih verzija): https://www.python.org/downloads/

Nakon toga, potrebno je instalirati pip alat koji će vam omogućiti da instalirate eksterne biblioteke
u lokalni virutelni environment: https://pip.pypa.io/en/stable/installation/

Kreiranje lokalnog virtual environment-a je pozeljno da uradite u ovom projektu (pozicionirati se u prevucen projekat). Kreiranje i aktivacija:

Linux i MacOS:

- virtualenv test_env
- source test_env/bin/activate

Windows:

- virtualenv test_env
- test_env\Scripts\activate -> Ako koristite cmd
- source test_env\Scripts\activate -> Ako koristite git bash

Kada ste aktivirali virtual environment, potrebno je instalirati sledece biblioteke:

- pip install requests

Nakon toga, testove pokretati sa sledecim komandama:

- python -m unittest test/test_passenger.py
- python -m unittest test/test_driver.py
- python -m unittest test/test_ride.py
- python -m unittest test/test_review.py
- python -m unittest test/test_panic.py
- python -m unittest test/test_vehicle.py
- python -m unittest test/test_user.py
- python -m unittest test/test_unregistered_user.py

Konfiguracija porta (8080) se nalazi u fajlu test/server_port.py pa ako vam je Spring pokrenut na drugom portu, promeniti vrednost u tom fajlu

Id-evi korisnika (vozača, putnika, admina) su definisani u test/user_data.py

**VRLO BITNE NAPOMENE**

Prvo, pošto ovo nisu klasični integracioni testovi, ne možemo se oslanjati na ROLLBACK (ili DROP i CREATE) baze nakon svakog testa i s obizrom da nemamo definisane endpoint-e koji se tiču brisanja većine entiteta (jer nije definisano specifikacjom), znači da su testovi podešeni tako da se izvršavaju sekvencijalno. U prevodu, nazivi testova su podešeni tako da se izvršavaju u određenom redosledu. Kada budete pokušavali nad svojim projektom, ako neki test padne, može uticati na sledeći test koji sledi. Kada ispitate zašto je test pao, krenite opet sa svežim podacima u bazi, pošto se podaci koji se dobiju kao odgovor koriste na nekim mestima u narednim testovima i plus se može desiti da naredni test zavisi od uspešno izvršenog prethodnog testa.

Preporučujem vam da koristite makar za testiranje spring.jpa.hibernate.ddl-auto=create-drop

Takođe, pošto nemamo uvid u vašu testnu bazu, napravljen je fajl test/user_data.py u kome se nalaze korišćeni ID-evi za korisnike. Slobodno to možete menjati i prilagoditi svojim podacima. Čak možete i dodavati druge vrednosti.

Ako primetite da nešto sa testovima nije kako treba (nešto što nije vezano za vaš tim samo, već za sve), pišite mi na mejl (scolic@uns.ac.rs) pa ću ispraviti.

**Testovi služe da ja i Lazar sebi olakšamo posao. SVAKI test koji bude pao, pogledaćemo zašto je pao. Ako znate zašto je neki test pao i imate validno objašnjenje, naravno da vam neće biti skidani bodovi. Isti slučaj ako postoji i neka naša greška u testovima.**

**Pojedine stvari iz specifikacije nisu testirane zbog neznanja kako izgledaju vaši test podaci ili zbog toga što nismo strikto definisali neke detalje ili isti nisu vidljivi iz specifikacije, tako da će isti biti pogledani na odbrani.**
