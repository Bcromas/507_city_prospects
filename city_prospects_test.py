from city_prospects import *
import unittest

class TestData(unittest.TestCase):

    #start testing of class to create ZillowHome instances
    def test_ZillowHome(self):
        x = ZillowHome(streetAddress = "123 Main St.", city = "8" , beds = "3" , sqft = "1200" , price = "1675" , url = "www.zillow.com")
        self.assertEqual(x.streetAddress, "123 Main St.")
        self.assertEqual(x.city, "8")
        self.assertEqual(x.price_sqft, 1.396)
        self.assertEqual(x.url, "www.zillow.com")
        self.assertEqual(str(x), "123 Main St. - Price:1675 - Price/SQFT:1.396")
    #end testing of class to create ZillowHome instances

    #start testing of DB setup, insert, & querying
    def test_DB(self):
        DBNAME = "test.db"
        x = db_setup(DBNAME)
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        city1 = 'Test'
        state1 = 'XY'
        statement1 = "INSERT into Cities VALUES (Null, '{}', '{}')".format(city1,state1)
        cur.execute(statement1)
        conn.commit()
        city2 = 'Check'
        state2 = 'ZZ'
        statement2 = "INSERT into Cities VALUES (Null, '{}', '{}')".format(city2,state2)
        cur.execute(statement2)
        conn.commit()
        statement = "SELECT Id from Cities WHERE Name='{}'".format(city2)
        cur.execute(statement)
        for i in cur:
            result = i[0]
        self.assertEqual(result,2)
    #end testing of DB setup, insert, & querying

class TestDB(unittest.TestCase):

    DBNAME = "city_prospects.db"

    #start testing that avg details populate when queried
    def test_DB_query(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT AVG(Price), AVG(Beds), AVG(Baths), AVG(SQFT) "
        statement += "FROM Apartments "
        cur.execute(statement)
        x = cur.fetchall()
        self.assertGreater(x[0][0],0)
        self.assertGreater(x[0][1],0)
        self.assertGreater(x[0][2],0)
        self.assertGreater(x[0][3],0)
    #end testing that avg details populate when queried

    #start testing that key data for apt summary shown on start up menu populates
    def test_apt_summ(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "SELECT Cities.Name, Cities.State, Count(*) "
        statement += "FROM Apartments "
        statement += "LEFT JOIN Cities on Apartments.City == Cities.Id "
        statement += "GROUP BY City "
        statement += "ORDER BY Cities.Name"
        cur.execute(statement)
        x = cur.fetchall()
        self.assertGreater(len(x[0][0]),0)
        self.assertGreater(len(x[0][1]),0)
        self.assertGreater(x[0][2],0)
    #end testing that key data for apt summary shown on start up menu populates

class TestVisuals(unittest.TestCase):

    DBNAME = "city_prospects.db"

    #query DB for a City ID & use for graph_1
    def test_graph_1(self):
        # pass

        try:
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            statement = "SELECT City "
            statement += "FROM Apartments "
            statement += "LIMIT 1"
            cur.execute(statement)
            x = cur.fetchall()
            city_id = x[0][0]
            graph_1(city_id)
        except:
            self.fail()
    #query DB for a City ID & use for graph_1

    #query DB for a City ID & use for graph_2
    def test_graph_2(self):
        # pass

        try:
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            statement = "SELECT City "
            statement += "FROM Apartments "
            statement += "LIMIT 1"
            cur.execute(statement)
            x = cur.fetchall()
            city_id = x[0][0]
            graph_2(city_id)
        except:
            self.fail()
    #query DB for a City ID & use for graph_2

    #query DB for a City ID & use for graph_3
    def test_graph_3(self):
        # pass

        try:
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            statement = "SELECT City "
            statement += "FROM Apartments "
            statement += "GROUP BY City"
            cur.execute(statement)
            x = cur.fetchall()
            city_idA = x[0][0]
            city_idB = x[1][0]
            graph_3(city_idA, city_idB)
        except:
            self.fail()
    #query DB for a City ID & use for graph_3

    #query DB for a City ID & use for graph_3
    def test_graph_4(self):
        # pass

        try:
            conn = sqlite3.connect(DBNAME)
            cur = conn.cursor()
            statement = "SELECT City "
            statement += "FROM Apartments "
            statement += "GROUP BY City"
            cur.execute(statement)
            x = cur.fetchall()
            city_idA = x[0][0]
            city_idB = x[1][0]
            graph_4(city_idA, city_idB)
        except:
            self.fail()
    #query DB for a City ID & use for graph_4

unittest.main()
