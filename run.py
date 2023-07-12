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
        self.pizza_sales = []
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
        # Daily fixed costs
        self.fixed_costs = 385

        self.pizzas = {
            'margherita': self.margherita_dict,
            'salami': self.salami_dict,
            'arugula': self.arugula_dict,
            'chicken': self.chicken_dict,
            'prosciutto': self.prosciutto_dict,
            'caprese': self.caprese_dict,
            'tuna': self.tuna_dict,
            'hawaii': self.hawaii_dict,
            'funghi': self.funghi_dict,
            'meat_lovers': self.meat_lovers_dict
    }     

    def calculate_pizza_cost(self, pizzas):
        """
        Calculate the cost of multiple pizzas
        """
        self.ingredients_kg_price = SHEET.worksheet('ingredients kg prices').get_all_values()
        # Transform list into dictionary and transform str to float
        ingredients_kg_price_dict = {key: float(value) for key, value in zip (self.ingredients_kg_price[0], self.ingredients_kg_price[1])}
        # Calculate ingredients constant costs using the weight in kg from (ingredients_constant_dict) * (ingredients_kg_price_dict) ingredients kg price
        ingredients_constant_cost = 0
        for ingredient, weight in self.ingredients_constant_dict.items():
            if ingredient in ingredients_kg_price_dict:
                ingredients_constant_cost += ingredients_kg_price_dict[ingredient] * weight

        pizzas_cost = {}
        for pizza_name, pizza_dict in pizzas.items():
            pizza_cost = 0
            for ingredient, weight in pizza_dict.items():
                if ingredient in ingredients_kg_price_dict:
                    pizza_cost += ingredients_kg_price_dict[ingredient] * weight
            pizza_cost += ingredients_constant_cost
            pizzas_cost[pizza_name] = pizza_cost
        return pizzas_cost
        
            
        

    # def calculate_shopping_list_cost(self):

    def calculate_pizza_price(self):
        """
        Calculate the pizza price of each pizza 
        """
        # Get the last six rows of pizza sales spread sheet
        self.pizza_sales = SHEET.worksheet('pizza sales').get_all_values()[-6:]
        # Calculate the daily average sold pizza
        avg_sold_pizzas = sum(sum(int(cell) for cell in row) for row in self.pizza_sales) /6
        # Calculate the fixed cost per pizza
        fixed_cost_per_pizza = self.fixed_costs / avg_sold_pizzas
        # Call the function passing the 'dictionary of dictionaries'(self.pizzas) to calculate the cost of every pizza
        pizzas_cost = self.calculate_pizza_cost(self.pizzas)
        # Add the fixed cost per pizza and a 30% profit to the cost of each pizza and round the price to two decimal places
        pizzas_price = {pizza_name: round(pizza_cost + fixed_cost_per_pizza +(pizza_cost + fixed_cost_per_pizza) * 0.35, 1) for pizza_name, pizza_cost in pizzas_cost.items()}
        return pizzas_price
    
    # This method is reusable, it takes two arguments 'sheet_name' which is the name of the worksheet and 'data_dict' a dictionary containing the data to be written
    def send_dict_to_sheet(self, sheet_name, data_dict):
        """
        Send the values of a dictionary to the specified worksheet
        """
        # Generate the data to be written
        data = [value for key, value in data_dict.items()]
        # Get the worksheet
        worksheet = SHEET.worksheet(sheet_name)
        # Append the data to the next available row
        worksheet.append_row(data)



    # def calculate_day_profit(self):

    # def calculate_ingredients_stock(self)

    # def generate_shopping_list(self):

        

         
test = Pizza_Management()
pizzas_price = test.calculate_pizza_price()
test.send_dict_to_sheet('pizza selling price', pizzas_price)
pprint(test.calculate_pizza_price())

