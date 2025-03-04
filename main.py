import psycopg2
from psycopg2 import extensions
from configparser import ConfigParser
import sys
from geopy import distance
import colorama
from colorama import Fore, Back, Style

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
        raise Exception(f'Section {0} not found in the {1} file'.format(section, filename))
    return db


def connect_db():
    # global variables to keep connection open and cursor quieries inside functions
    global conn
    global cur
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print(f'{Fore.LIGHTBLUE_EX}Connecting to the game database...')
        try:
            conn = psycopg2.connect(**params)
        except psycopg2.OperationalError as e:
            print(f'{Fore.RED}Error: {e}')
            sys.exit(1)
        # Test if connection was successful
        if conn.status == extensions.STATUS_READY:
            print(f"{Fore.LIGHTGREEN_EX}Successfully connected to the game server!\n\n")
        else:
            print("Error connecting to the database. Cannot start the game.")
            sys.exit(1)
        # create a cursor
        cur = conn.cursor()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_random_airports():
    airports_list = []
    while len(airports_list) < 5:
        sql_db_length = f"SELECT city, country FROM airport WHERE icao = (SELECT icao FROM airport order by random() limit 1);"
        cur.execute(sql_db_length)
        result = cur.fetchall()
        # Generate X number of random airports. Make sure it's not a repeated and different than the starting location
        if result[0] not in airports_list and result[0][0] != current_location[-1]:
            airports_tuple = (result[0][0], result[0][1])
        else:
            continue
        airports_list.append(airports_tuple)
    return airports_list


# Iterate and print the list of airports the user must travel to.
# This outputs in a nicer format the contents of get_random_airports()

def print_airports(airport_list: list):
    airports_str = ""
    for index, tup in enumerate(airport_list):
        airports_str += f"{Fore.RED}{tup[0]}, {tup[1]} || "
    print(airports_str[0:-3])


# Find airports nearby


def airports_nearby():
    reachable_airports = []
    nearby = f"SELECT * from airport where city != '{current_location[-1]}';"
    cur.execute(nearby)
    result = cur.fetchall()
    for coords in result:
        if distance.distance(coords[2:4], current_location[2:4]).km < flight_range:
            reachable_airports.append(coords)
    return reachable_airports


# add debug if number out of the list. Later on


def flight_target(airports: list):
    print("")
    print("Select your next destination: ")
    for i in range(len(airports)):
        print(f"\t{i + 1} - {airports[i][-1]}, {airports[i][-2]}")
    while True:
        try:
            user_choice = int(input("> "))
        except ValueError:
            print("Invalid input. Input a airport number from the list above.")
            continue
        else:
            if user_choice <= 0 or user_choice > len(airports):
                print("The selected airport is not valid!")
                continue
        break
    target_city = airports[user_choice - 1]
    return target_city


def update_curr_location():
    current = f"UPDATE player SET curr_location = '{current_city_country}' WHERE username = '{username}';"
    cur.execute(current)
    insert_game_turn_query = f"INSERT INTO GAME(game_id, player_id, city_visited) VALUES ({game_id}, {player_id}, '{current_city_country}')"
    cur.execute(insert_game_turn_query)
    all_places_visited.append(current_city_country)
    get_info = f"SELECT * from player WHERE username = '{username}';"
    cur.execute(get_info)
    conn.commit()
    res = cur.fetchall()
    return res


def total_travel_distance(airport_from, airport_to):
    dist = distance.distance(airport_from, airport_to).km
    return dist


def co2_calculator(target_cities_list: list):
    co2_packages_left = {
        1: 8.24,
        2: 16.62,
        3: 25,
        4: 33.24,
        5: 41.62
    }
    list_length = len(target_cities_list)
    if list_length in co2_packages_left:
        co2_per_journey = co2_packages_left[list_length] * total_travel_distance(travel_from, travel_to)
    return co2_per_journey


def co2_per_trip(target_cities_list: list):
    co2_packages_left = {
        1: 8.24,
        2: 16.62,
        3: 25,
        4: 33.24,
        5: 41.62
    }
    list_length = len(target_cities_list)
    return co2_packages_left.get(list_length)


def starting_location():
    global current_location
    start_city_query = f"SELECT * FROM airport WHERE icao = 'EFHK';"
    cur.execute(start_city_query)
    result = cur.fetchall()
    current_location = result[0]
    return current_location

def get_game_id():
    game_id_query = f"SELECT MAX(game_id) from game;"
    cur.execute(game_id_query)
    game_id = cur.fetchone()
    if game_id[0] is None: # If there's no records on the table
        game_id = 1
    else:
        game_id = game_id[0] + 1
    return game_id

def get_player_id():
    player_id_query = f"SELECT id from player where username ='{username}'"
    cur.execute(player_id_query)
    player_id = cur.fetchone()
    return player_id[0]

def close_db_connection():
    try:
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


""" Game Functions """

def search_username():
    try:
        select_id_from_username_query = f"SELECT id FROM player WHERE username = '{username}'"
        cur.execute(select_id_from_username_query)
        username_row = cur.fetchall()
        return len(username_row) # returns how many results the query returned
    except (Exception, psycopg2.DatabaseError) as error:
        print(error) 


def add_username(username: str):
    try:
        add_new_user = f"INSERT INTO player(username) VALUES ('{username}')"
        cur.execute(add_new_user)
        conn.commit()
        #print(f"{username} has been added to the database!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"{Fore.RED}{error}")


def login_screen():
    print("\t\t-- Flight Game --")
    print("\t\t[1] Create new game")
    print("\t\t[2] Exit")


def welcome_ascii():
    user = username + (" " * (20 - len(username)))
    print(f"""\
        {Fore.BLUE}
        .----.                                                   .'.
        |  /   '                                                 |  '
        |  |    '                                                '  :
        |  |     '             .-~~~-.               .-~-.        \ |
        |  |      '          .\\   .//'._+_________.'.'  /_________\|
        |  |___ ...'.__..--~~ .\\__//_.-     . . .' .'  /      :  |  `.
        |.-"  .'  /  {Fore.GREEN}Welcome Pilot{Fore.BLUE}           . .' .'   /.      :_.|__.'
       <    .'___/    {Fore.YELLOW}{user}{Fore.BLUE}   .' .'    /|.      : .'|\\
        ~~--..                             .' .'     /_|.      : | | \\
          /_.' ~~--..__             .----.'_.'      /. . . . . . | |  |
                      ~~--.._______'.__.'  .'      /____________.' :  /
                               .'   .''.._'______.'                '-'
                               '---'
                               """)


def landing_ascii():
    print(f"""{Fore.LIGHTCYAN_EX}
          */ | \*
          / -+- \\
      ---o--(_)--o---
        /  0 " 0  \\
      */     |     \*
      /      |      \\
""")


if __name__ == "__main__":
    # Vars initialization
    total_turns = 0
    total_co2_wasted = 0.0
    all_places_visited = []
    flight_range = 800
    total_dist = 0.0
    colorama.init(autoreset=True)
    # Colorama video tutorial : https://youtu.be/u51Zjlnui4Y?t=475
    # Colorama colors list : https://stackoverflow.com/q/61686780

    # Call login screen at the start of the game
    login_screen()
    # Main Menu Selection
    option = input("Type your choice: ")
    while True:
        if option == "1":
            # Ask user to type a username
            while True:
                username = input("Type your username: ").capitalize()
                if len(username) == 0:
                    print("Username cannot be empty!")
                    continue
                if len(username) > 20:
                    print(f"Your username is too long! Please use at most 20 characters for your username.")
                    continue
                break
            break
        elif option == "2":
            print("Thank you for playing!")
            sys.exit(1)
        else:
            option = input("Invalid choice. Please type your choice again: ")

    # Connect to the DB after the user selects the nickname
    connect_db()

    # Add new user to the DB if it doesn't exist
    if search_username() == 0:
        add_username(username)
    #print(f"Welcome, {username}!")

    # Grab current player ID and assign a new game_id for this session so we can log the player's movements
    game_id = get_game_id()
    player_id = get_player_id()
    welcome_ascii()

    # Populate the current_location - Currently will always be Helsinki
    current_location = starting_location()
    current_city_country = f"{current_location[-1]}, {current_location[-2]}"
    print(f"{Fore.CYAN}You are a new pilot of FedEx.\n"
          f"Your mission is to deliver packages to the following airports.\n"
          f"You are flying Boeing 737-400 with the fuel limited to {flight_range} km flight range.\n"
          f"If you can't reach your target destination directly, you have to fly by cities that are on the way,"
          f" and refill the fuel tank.\n"
          f"Try using most efficient roots in order to generate less carbon footprint & save company's operational costs.\n"
          f"{Fore.RED}{Style.BRIGHT}HINT: The fewer packages you carry, the less CO2 emission you generate!\n"
          f"{Fore.CYAN}You starting position is {current_city_country}. Good luck & have fun!\n")
    print(f"Reach these airports in any order:")
    # Grab the 5 closest airports to the current location
    generated_5_airports = get_random_airports()
    print_airports(generated_5_airports)
    print("")

    print(f"From {Fore.LIGHTGREEN_EX}{current_city_country}{Fore.LIGHTGREEN_EX} can travel to any of these cities:")

    while len(generated_5_airports) > 0:
        nearby_airports = airports_nearby()
        travel_from = [current_location[2], current_location[3]]
        destination = flight_target(nearby_airports)
        travel_to = [destination[2], destination[3]]
        current_city_country = f"{destination[-1]}, {destination[-2]}"
        current_location = destination
        update_curr_location()
        co2_calculator(generated_5_airports)
        total_co2_wasted += co2_calculator(generated_5_airports)
        total_dist += total_travel_distance(travel_from, travel_to)
        total_turns += 1
        landing_ascii()
        print(f"You're now in {Fore.LIGHTGREEN_EX}{current_city_country}{Fore.LIGHTGREEN_EX}.\n")
        for city_from_gen_list in generated_5_airports:
            if (current_location[-1], current_location[-2]) in generated_5_airports:
                generated_5_airports.remove((current_location[-1], current_location[-2]))
                if len(generated_5_airports) == 0:
                    break
                print(f"Nicely done!\n"
                      f"You have delivered a package to {current_location[-1]} - one of your target destinations.\n"
                f"Now you dropped some cargo so your co2 emission decreased to {co2_per_trip(generated_5_airports)} "
                      f"kg per km.")
                print(f"You have the following destinations left:")
                print_airports(generated_5_airports)
                print("")
                break
            elif destination[-1] != city_from_gen_list[0]:
                print(f"You need to deliver your package to the following airport(s) in: \n")
                print_airports(generated_5_airports)
                break
        # Uncomment when debugging if needed - Remove later
        # print(generated_5_airports)
    print(f"Congratulations!!!\n You have reached your final destination and finished the game!")
    print(f" You have visited: {', '.join(all_places_visited)}")  # FIX to make it fancy
    print(f"It took you {total_turns} turns to deliver all the packages.\n"
          f"The total travelled distance is {total_dist:.2f} km.\n"
          f"The total carbon emission is {total_co2_wasted:.2f} kg CO2\n"
          f"GGWP")

    # Remove comments below when understand how co2 emission calculated

    # CO2 emissions from aviation fuel are 3.15 grams per gram of fuel [38],
    # which gives CO2 emissions from a Boeing 737-400 of 115 g per passenger per km.
    # At a cruising speed of 780 km per hour [Wikipedia, 28.2. 08],
    # this is equivalent to 90 kg CO2 per passenger per hour.

    # co2 full plane 4203.8 * 101km
    # 41,62kg per 1km
    # cargo max 23000 == 288pas*80kg
    # https://www.icao.int/environmental-protection/Carbonoffset/Pages/default.aspx
    # 41.62 kg CO2 per 1 km - 5 packages
    # 33.24 kg CO2 per 1 km - 4 packages
    # 25.00 kg CO2 per 1 km - 3 packages
    # 16.62 kg CO2 per 1 km - 2 packages
    # 8.24 kg CO2 per 1 km - 1 package

    # forcefully closing this to be 100% sure no connection gets stuck
    close_db_connection()
