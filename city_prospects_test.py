from city_prospects import *
import unittest

class TestData(unittest.TestCase):

    #start testing of class to create ZillowHome instances
    def test_ZillowHome(self):
        x = ZillowHome(streetAddress = "123 Main St.", city = "Boston" , beds = "3" , rooms = "6" , sqft = "2,700" , price = "$379,000" , price_sqft = "$140" , est_mortgage = "2,101" , url = "www.zillow.com")
        self.assertEqual(x.streetAddress, "123 Main St.")
        self.assertEqual(x.city, "Boston")
        self.assertEqual(x.url, "www.zillow.com")
        self.assertEqual(str(x), "123 Main St. - Price:$379,000 - Price/SQFT:$140")
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
        # conn = sqlite3.connect(DBNAME)
        # cur = conn.cursor()
        statement = "SELECT Id from Cities WHERE Name='{}'".format(city2)
        cur.execute(statement)
        for i in cur:
            result = i[0]
        self.assertEqual(result,2)
    #end testing of DB setup, insert, & querying


unittest.main()
