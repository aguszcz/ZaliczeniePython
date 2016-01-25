# -*- coding: utf-8 -*-

import sqlite3


db_path = 'aga_baza.db'

# utworzenie połączenia z bazą
conn = sqlite3.connect(db_path)

# dostęp do kolumn przez indeksy i przez nazwy
conn.row_factory = sqlite3.Row

# utworzenie obiektu kursora
c = conn.cursor()
#
# Tabele
#


c.execute('''
          CREATE TABLE IF NOT EXISTS film
          ( id_film INTEGER,
            tytul VARCHAR(100),
            rok DATE NOT NULL,
           PRIMARY KEY (id_film))
          ''')
c.execute('''
          CREATE TABLE IF NOT EXISTS aktor
          ( id_aktor INTEGER PRIMARY KEY,
            imie VARCHAR(20) NOT NULL,
            nazwisko VARCHAR(40) NOT NULL,
            wynagrodzenie integer not null,
            id_film integer not null,
           FOREIGN KEY(id_film) REFERENCES film(id_filmm)
          )
          ''')
