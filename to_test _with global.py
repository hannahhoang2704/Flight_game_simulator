import psycopg2
from psycopg2 import extensions
from configparser import ConfigParser
import sys
#from geopy.distance import geodesic as GD

"""
Basic Connection Functions
"""


def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def connectDB():
    # global variables to keep connection open and cursor quieries inside functions

    global conn
    global cur
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the game database...')
        try:
            conn = psycopg2.connect(**params)
        except psycopg2.OperationalError as e:
            print(f'Error: {e}')
            sys.exit(1)
        # Test if connection was successful
        if conn.status == extensions.STATUS_READY:
            print("Successfully connected to the game server!\n\n")
        else:
            print("Error connecting to the database. Cannot start the game.")
            sys.exit(1)
        # create a cursor
        cur = conn.cursor()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def closeDBConnection():
    try:
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    # get random airport
def get_random_airports():
    airports_list = []
    while len(airports_list) < 5:
        sql_db_length = f"SELECT city FROM airport WHERE icao = (SELECT icao FROM airport order by random() limit 1);"
        cur.execute(sql_db_length)
        result = cur.fetchall()
        if result[0][0] not in airports_list:
            airports_list.append(result[0][0])
    return airports_list
    generated_5_airports = get_random_airports()
    print(generated_5_airports)




connectDB()
get_random_airports()


closeDBConnection()

## before test
def get_random_airports():
    airports_list = []
    while len(airports_list) < 5:
        sql_db_length = f"SELECT city FROM airport WHERE icao = (SELECT icao FROM airport order by random() limit 1);"
        cur.execute(sql_db_length)
        result = cur.fetchall()
        if result[0][0] not in airports_list:
            airports_list.append(result[0][0])
    return airports_list


generated_5_airports = get_random_airports()
print(generated_5_airports)


#working but getting only coords from the db
#need to find objects by coords
def airports_nearby():
    reachable_airports = []
    # for i in range(airport_table_length):
    nearby = f"SELECT latitude_deg, longitude_deg from airport where city != '{current_city[-1]}';"  # [(52.3086, 4.76389), (59.4133, 24.8328), (48.1103, 16.5697), (44.0203, 12.6117), (47.4298, 19.2611), (49.0128, 2.55), (43.8246, 18.3315), (55.9726, 37.4146), (52.3514, 13.4939), (45.7429, 16.0688), (52.1657, 20.9671), (50.9014, 4.48444), (38.7813, -9.13592), (35.8575, 14.4775), (55.6179, 12.656), (43.7258, 7.41967), (42.3594, 19.2519), (41.8045, 12.252), (41.9616, 21.6214), (60.1939, 11.1004), (53.8881, 28.04), (53.4213, -6.27007), (49.6233, 6.20444), (42.6967, 23.4114), (59.6519, 17.9186), (42.3386, 1.40917), (56.9236, 23.9711), (37.9364, 23.9445), (44.5711, 26.085), (46.9277, 28.931), (64.13, -21.9406), (50.1008, 14.26), (48.1702, 17.2127), (44.8184, 20.3091), (54.6341, 25.2858), (51.5053, 0.055278), (50.345, 30.8947), (41.4147, 19.7206), (46.9141, 7.49715), (46.2237, 14.4576), (40.4719, -3.56264)]
    cur.execute(nearby)
    result = cur.fetchall()
    for coords in result:
        if distance.distance(coords, current_city[2:4]).km < 105:
            reachable_airports.append(coords)
    print(reachable_airports)
    print(len(result))
    print(result)


airports_nearby()


## Fetching not coords, but whole object
def airports_nearby():
    reachable_airports = []
    # for i in range(airport_table_length):
    nearby = f"SELECT * from airport where city != '{current_city[-1]}';"  # [(52.3086, 4.76389), (59.4133, 24.8328), (48.1103, 16.5697), (44.0203, 12.6117), (47.4298, 19.2611), (49.0128, 2.55), (43.8246, 18.3315), (55.9726, 37.4146), (52.3514, 13.4939), (45.7429, 16.0688), (52.1657, 20.9671), (50.9014, 4.48444), (38.7813, -9.13592), (35.8575, 14.4775), (55.6179, 12.656), (43.7258, 7.41967), (42.3594, 19.2519), (41.8045, 12.252), (41.9616, 21.6214), (60.1939, 11.1004), (53.8881, 28.04), (53.4213, -6.27007), (49.6233, 6.20444), (42.6967, 23.4114), (59.6519, 17.9186), (42.3386, 1.40917), (56.9236, 23.9711), (37.9364, 23.9445), (44.5711, 26.085), (46.9277, 28.931), (64.13, -21.9406), (50.1008, 14.26), (48.1702, 17.2127), (44.8184, 20.3091), (54.6341, 25.2858), (51.5053, 0.055278), (50.345, 30.8947), (41.4147, 19.7206), (46.9141, 7.49715), (46.2237, 14.4576), (40.4719, -3.56264)]
    cur.execute(nearby)
    result = cur.fetchall()
    for coords in result:
        if distance.distance(coords[2:4], current_city[2:4]).km < 405:
            reachable_airports.append(coords)
    return reachable_airports


cities_within_range = airports_nearby()
print(cities_within_range)


## returning list of cities where you can reach within give range
def flight_target():
    print("Select destination: ")
    for i in range(len(cities_within_range)):
        print(f"\t{i + 1} - {cities_within_range[i][-1]}")


flight_target()
# Select destination:
# 	1 - Tallinn
# 	2 - Stockholm
# 	3 - Riga