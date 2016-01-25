# coding=utf-8

# -*- coding: utf-8 -*-


import sqlite3

import math
from datetime import datetime

#
# Scieżka połączenia z bazą danych
#
db_path = 'aga_baza.db'

#
# Wyjątek używany w repozytorium
#
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors

#
# Model danych
#
class Film():
    """Model pojedynczego film
    """
    def __init__(self, id_film, tytul, rok, aktorzy=[]):
        self.id_film = id_film
        self.tytul = tytul
        self.rok=rok
        self.aktorzy=aktorzy


    def __repr__(self):
        return "<FILM tytul %s, rok=%s, (id=%s), aktorzy = %s)>" % (self.tytul, str(self.rok), self.id_film, self.aktorzy)

class Aktor():
    """Model aktorów występujących w danym filmie
    """
    def __init__(self, id_film, imie, nazwisko, wynagrodzenie):
        self.id_film=id_film
        self.imie=imie
        self.nazwisko=nazwisko
        self.wynagrodzenie=wynagrodzenie

    def __repr__(self):
        return "<Aktor %s %s, wynagrodzenie %s (id_filmu=%s)>" %(self.imie, self.nazwisko, self.wynagrodzenie, self.id_film)


class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

#
# repozytorium obiektow typu Invoice
#
class repoaga(Repository):

    def add(self, film):
        """Metoda dodaje pojedynczą fakturę do bazy danych,
        wraz ze wszystkimi jej pozycjami.
        """
        try:
            c = self.conn.cursor()
            c.execute('INSERT INTO film (id_film, tytul, rok) VALUES(?, ?, ?)',
                        (film.id_film, film.tytul, film.rok)
                    )
            # zapisz aktorow
            if film.aktorzy:
                for aktorzy in film.aktorzy:
                    try:
                        c.execute('INSERT INTO aktor (imie, nazwisko, wynagrodzenie,id_film) VALUES(?,?,?,?)',
                                        (aktorzy.imie, aktorzy.nazwisko, aktorzy.wynagrodzenie, film.id_film)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding: %s, to komunikat bledu: %s' %
                                                    (str(film), e)
                                                )
        except Exception as e:
            #print "invoice add error:", e
            raise RepositoryException('error adding %s' % str(e))

    def delete(self, id_film):
        """Metoda usuwa pojedynczy film wraz z przypisanymi aktorami
        """
        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM film WHERE id_film=?', (id_film,))
            # usuń aktorow
            c.execute('DELETE FROM aktor WHERE id_film=?', (id_film,))

        except Exception as e:
            #print "delete :", e
            raise RepositoryException('error deleting  %s' % str(e))


    def getById(self, id):
        """Get film by id
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM film WHERE id_film=?", (id,))
            row = c.fetchone()
#            film = Film(id_film=id)
            a=[]
            if row == None:
                film=None
            else:
                film=Film(id_film=id, tytul= row[1], rok=row[2],aktorzy=[])
                c.execute("SELECT * FROM aktor WHERE id_film=? order by imie", (id,))
                aktor_rows = c.fetchall()
                for i_rows in aktor_rows:
                    a = Aktor(id_film=id, imie=i_rows[1], nazwisko=i_rows[2], wynagrodzenie=i_rows[3])
                    film.aktorzy.append(a)
        except Exception as e:
            #print "invoice getById error:", e
            raise RepositoryException('error getting by id film: %s' % str(e))
        return film



    def getMaxAktor(self, id):  #id jest id filmu
        """Get max wiek aktorow wystepujacych w danym filmie
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT max(wynagrodzenie) FROM aktor WHERE id_film=?", (id,))
            row = c.fetchone()
            if row == None:
                wynagrodzenie_max=None
            else:
                wynagrodzenie_max=row[0]
        except Exception as e:
            #print "aktor getMax error:", e
            raise RepositoryException('error getting max: %s' % str(e))
        return wynagrodzenie_max

    def getMinAktor(self, id):  #id jest id filmu
        """Get min wiek aktorow wystepujacych w danym filmie
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT min(wynagrodzenie) FROM aktor WHERE id_film=?", (id,))
            row = c.fetchone()
            if row == None:
                wynagrodzenie_min=None
            else:
                wynagrodzenie_min=row[0]
        except Exception as e:
            #print "aktor getMax error:", e
            raise RepositoryException('error getting min: %s' % str(e))
        return wynagrodzenie_min

    def getSrednieAktor(self):  #id jest id filmu
        """Get srednie wynagrodzenie aktorow wystepujacych we wszystkich filmach
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT avg(wynagrodzenie) FROM aktor")
            row = c.fetchone()
            if row == None:
                wynagrodzenie_srednie=None
            else:
                wynagrodzenie_srednie=row[0]
        except Exception as e:
            #print "aktor getMax error:", e
            raise RepositoryException('error getting min: %s' % str(e))
        return wynagrodzenie_srednie

    def update(self, film):
        """Metoda uaktualnia pojedynczy film wraz z przypisanymi aktorami.
        """
        try:
            # pobierz z bazy fakturę
            F_oryg = self.getById(film.id_film)
            if F_oryg != None:
                # faktura jest w bazie: usuń ją
                self.delete(film.id_film)
            self.add(film)

        except Exception as e:
            #print "film update error:", e
            raise RepositoryException('error updating film %s' % str(e))





if __name__ == '__main__':
    try:
        with repoaga() as rpa:
            rpa.delete(1)
            rpa.delete(2)
            rpa.complete()
            rpa.add(
               Film(1, "Zjawa" , 2015 ,
                        aktorzy = [
                            Aktor(1, "Leonardo", "DiCaprio", 1000000),
                            Aktor(1, "Tom", "Hardy", 500000),
                            Aktor(1, "Domhnall", "Gleeson", 400000),
                            Aktor(1, "Will", "Poulter", 250000),
                        ]
                    ))
            rpa.add(
               Film(2, "Dwunastu gniewnych ludzi" , 1957 ,
                        aktorzy = [
                            Aktor(2, "Henry", "Fonda", 4500000),
                            Aktor(2, "Martin", "Balsam", 550000),
                            Aktor(2, "Jack", "Klugman", 400000),
                            Aktor(2, "Edward", "Binns", 250000),
                        ]
                    ))
            rpa.complete()
            #print("***Zastapienie filmu o podanym numerze id innym filmem wraz z aktorami ***")
            #rpa.update(Film(1,"JAWA",2000,[Aktor(1,"dd","sss",1000)]))
            print("***Film o podanym id wraz z aktorami: ***")
            print(rpa.getById(id=1))
            print("*******************")
            print("*** Maksymalne wynagrodzenie aktora dla filmu o danym id ***")
            print(rpa.getMaxAktor(id=1))
            print("*******************")
            print("*** Minimalne wynagrodzenie aktora dla filmu o danym id ***")
            print(rpa.getMinAktor(id=2))
            print("*******************")
            print("*** Srednie wynagrodzenie wszystkich aktorow ***")
            print(rpa.getSrednieAktor())
            print("*******************")
    except RepositoryException as e:
       print(e)





#a1=Aktor(1,'A','B',22)
#a2=Aktor(1,"Jan","Kowalski",1998)
#FA= Film(1,'sdklfjsl',2014, [a1,a2])

#print(FA)
#print(a1)
#print(a2)
