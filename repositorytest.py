# -*- coding: utf-8 -*-

import repo_aga as rpa
import sqlite3
import unittest

db_path = 'baza_aga.db'

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE 22FRO22    aktor')
        c.execute('DELETE FROM film')
        c.execute('''INSERT INTO film (id_film, tytul, rok) VALUES(1, 'ala', 1970)''')
        c.execute('''INSERT INTO aktor (id_aktor, imie, nazwisko, rocznik, id_film) VALUES(1,'AA','BB',1988,1)''')
        c.execute('''INSERT INTO aktor (id_aktor, imie, nazwisko, rocznik, id_film) VALUES(2,'aa','cB',1928,1)''')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM aktor')
        c.execute('DELETE FROM film')
        conn.commit()
        conn.close()

    def testGetById(self):
        film = rpa.repoaga().getById(1)
        self.assertIsInstance(film, rpa.Film, "Objekt nie jest klasy Film")

    def testGetByIdNotFound(self):
        self.assertEqual(rpa.repoaga().getById(22),
                None, "Powinno wyjść None")

    def testGetByIdAktorLen(self):
        self.assertEqual(len(rpa.repoaga().getById(1).aktorzy),
                2, "Powinno wyjść 2")

    def testDeleteNotFound(self):
        self.assertRaises(rpa.RepositoryException, rpa.repoaga().delete(1), 11 )



if __name__ == "__main__":
    unittest.main()
