from pprint import pprint
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('master_pizza')

class Pizza_Management:
    """
    Pizzeria management Class
    """
    def __init__(self):
        self.ingredients_kg_price = []
        # Dictionaries with key ingredients and respective weight in kg
        self.ingredients_constant_dict = {'flour': 0.35, 'east': 0.003, 'salt': 0.007, 'sugar': 0.010, 'tomato sauce': 0.5, 'cheese': 0.18}
        self.margherita_dict = {'tomatoes': 0.03, 'oregano': 0.003}

        self.salami_dict = {'salami': 0.04, 'oregano': 0.003}
            
        self.arugula_dict = {'arugula': 0.01, 'parma ham': 0.025, 'oregano': 0.003}
            
        self.chicken_dict = {'chicken': 0.04, 'champignon': 0.015, 'oregano': 0.003}
            
        self.prosciutto_dict = {'ham': 0.04, 'champignon': 0.015, 'olives': 0.015, 'oregano': 0.003}

        self.caprese_dict = {'tomatoes': 0.03, 'olives': 0.015, 'onion': 0.03, 'oregano': 0.003}

        self.tuna_dict = {'tuna': 0.04, 'onion': 0.03, 'olives': 0.015, 'oregano': 0.003}   

        self.hawaii_dict = {'ham': 0.04, 'pineapple': 0.035}

        self.funghi_dict = {'champignon': 0.015, 'ham': 0.04, 'onion': 0.03, 'oregano': 0.003}
        
        self.meat_lovers_dict = {'meat': 0.04, 'onion': 0.03, 'tomatoes': 0.03, 'oregano': 0.003}
            

    def calculate_pizza_cost(self):
        """
        Calculate pizza cost: (ingredients kg price) * (ingredients)
        """
        self.ingredients_kg_price = SHEET.worksheet('ingredients kg prices').get_all_values()
        # Transform list into dictionary and transform str to float
        ingredients_kg_price_dict = {key: float(value) for key, value in zip (self.ingredients_kg_price[0], self.ingredients_kg_price[1])}
        return ingredients_kg_price_dict
        

    # def calculate_shopping_list_cost(self):

    # def calculate_pizza_price(self):

    # def calculate_day_profit(self):

    # def calculate_ingredients_stock(self)

    # def generate_shopping_list(self):

        

         
test = Pizza_Management()
pprint(test.calculate_pizza_cost())

# pizza_sales = SHEET.worksheet('pizza sales')
# data = pizza_sales.get_all_values()
# print(data)