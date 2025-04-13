# Retkeilyvarusteet
Tässä sovelluksesssa käyttäjät voivat luoda retkeilyvarustelistoja eri käyttötarkoituksiin. Käyttäjät näkevät toistensa retkeilyvarustelistat ja voivat antaa niistä palautetta kommenttien muodossa. Täten käyttäjät voivat auttaa toisiansa varusteisiin liittyen ja jakaa uusille retkeilijöille tietämystä varusteista.

## Toiminnot
* Sovelluksessa käyttäjät pystyvät jakamaan retkeilyvarustelistoja.
* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan retkeilyvarustelistoja.
* Käyttäjä pystyy lisäämään kuvia retkeilyvarusteista retkeilyvarustelistaan.
* Käyttäjä pystyy valitsemaan retkeilyvarustelistoille luokittelun vuodenajan ja retken keston mukaan.
* Käyttäjä näkee sovellukseen lisätyt retkeilyvarustelistat.
* Käyttäjä pystyy antamaan retkeilyvarustelistoille kommentin ja poistamaan omia kommenttejaan.
* Retkeilyvarustelistoille näytetään sen saamat kommentit.
* Käyttäjä pystyy etsimään retkeilyvarustelistoja nimen tai kuvauksen perusteella.
* Käyttäjäsivu näyttää montako retkeilyvarustelistaa käyttäjä on lisännyt ja montako kommentia käyttäjä on jättänyt.
* Käyttäjäsivu näyttää listan käyttäjän lisäämistä retkeilyvarustelistoista.
* Käyttäjä voi poistaa käyttäjätunnuksensa.

## Sovelluksen asennus
1.Lataa repositorio.
\
\
2. Asenna `flask` -kirjasto:
```
pip instal flask
```
\
3. Luo tietokannan taulut ja lisää alkutiedot:
```
sqlite3 database.db < schema.sql
sqlite3 database.db < init.sql
```
\
4. Käynnistä ohjelma:
```
flask run
```
