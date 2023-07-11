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
    management Class
    """
    def __init__(self):
        self.ingredients_kg_price = []
        self.margherita_dictionary = {
            'flour' : 0.35,
            'east' : 0.003,
            'salt' : 0.007,
            'sugar' : 0.010,
            'tomato sauce': 0.5,
            'cheese' : 0.18,
            'tomatoes' : 0.03,
            'oregano' : 0.003
            }

    def calculate_pizza_cost(self):
        self.ingredients_kg_price = SHEET.worksheet('ingredients kg price').get_all_values()
        ingredients_kg_price_dict = {key: float(value) for key, value in zip (self.ingredients_kg_price[0], self.ingredients_kg_price[1])}
        return ingredients_kg_price_dict
        if 

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