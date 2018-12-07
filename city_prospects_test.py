from city_prospects import *
import unittest

class TestData(unittest.TestCase):

    #start testing of class to create ZillowHome instances
    def test_ZillowHome(self):
        x = ZillowHome(streetAddress = "123 Main St.", city = "8" , beds = "3" , sqft = "1200" , price = "1675" , url = "www.zillow.com")
        self.assertEqual(x.streetAddress, "123 Main St.")
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


unittest.main()
