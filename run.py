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


class PizzaManagement:
    """
    Pizzeria management Class
    """

    def __init__(self):
        
        # Dictionaries with key ingredients and respective weight in kg
        
        self.ingredients_constant_dict = { 'flour': 0.35, 'east': 0.003, 'salt': 0.007, 'olive oil': 0.010, 'sugar': 0.010, 'tomato sauce': 0.5, 'cheese': 0.18}

        self.margherita_dict = {'tomatoes': 0.03, 'oregano': 0.003}

        self.salami_dict = {'salami': 0.04, 'oregano': 0.003}

        self.arugula_dict = {'arugula': 0.01, 'parma ham': 0.025, 'oregano': 0.003}

        self.chicken_dict = {'chicken': 0.04, 'mushroom': 0.015, 'oregano': 0.003}

        self.prosciutto_dict = {
            'ham': 0.04, 'mushroom': 0.015, 'olives': 0.015, 'oregano': 0.003}

        self.caprese_dict = {'tomatoes': 0.03, 'olives': 0.015, 'onion': 0.03, 'oregano': 0.003}

        self.tuna_dict = {'tuna': 0.04, 'onion': 0.03, 'olives': 0.015, 'oregano': 0.003}

        self.hawaii_dict = {'ham': 0.04, 'pineapple': 0.035}

        self.funghi_dict = {'mushroom': 0.015,
                            'ham': 0.04, 'onion': 0.03, 'oregano': 0.003}

        self.meat_lovers_dict = {
            'meat': 0.04, 'onion': 0.03, 'tomatoes': 0.03, 'oregano': 0.003}
        # Daily fixed costs
        self.fixed_costs = 385

        self.pizzas = {
            'pizza margherita': self.margherita_dict,
            'pizza salami': self.salami_dict,
            'pizza arugula': self.arugula_dict,
            'pizza chicken': self.chicken_dict,
            'pizza prosciutto': self.prosciutto_dict,
            'pizza caprese': self.caprese_dict,
            'pizza tuna': self.tuna_dict,
            'pizza hawaii': self.hawaii_dict,
            'pizza funghi': self.funghi_dict,
            'pizza meat lovers': self.meat_lovers_dict
        }

    def calculate_pizza_cost(self, pizzas):
        """
        Calculate the cost to manufacture the pizzas
        """
        # Retrieve the ingredient prices per kg from worksheet
        ingredients_kg_price_sheet = SHEET.worksheet('ingredients kg prices').get_all_values()
        # Create a dictionary
        ingredients_kg_price_dict = {key: float(value)for key, value in zip(ingredients_kg_price_sheet[0], ingredients_kg_price_sheet[1])}
        # retrieve the pizza sales data from the worksheet
        pizza_sales_sheet = SHEET.worksheet('pizza sales')
        pizza_sales = pizza_sales_sheet.get_all_values()
        # Convert all numeric sales values to integers
        numeric_sales = [[int(cell) for cell in row if cell.isdigit()]for row in pizza_sales]
        # Calculate the average number of pizzas sold by summing all sales and dividing by the numbers of sales
        avg_sold_pizzas = sum(sum(row) for row in numeric_sales) / len(numeric_sales)
        # Calculate the fixed cost per pizza by diving the total fixed cost by the average number of pizzas sold
        fixed_cost_per_pizza = round(self.fixed_costs / avg_sold_pizzas, 2)
        # calculate the constant cost of ingredients for the pizzas
        ingredients_constant_cost = 0 
        for ingredient, weight in self.ingredients_constant_dict.items():
            if ingredient in ingredients_kg_price_dict:
                ingredients_constant_cost += round(ingredients_kg_price_dict[ingredient] * weight, 2)
        pizzas_cost = {}
        # Iterate over the provided pizzas and their ingredients
        for pizza_name, pizza_dict in pizzas.items():
            pizza_cost = 0
            for ingredient, weight in pizza_dict.items():
                if ingredient in ingredients_kg_price_dict:
                    pizza_cost += round(ingredients_kg_price_dict[ingredient] * weight, 2)
            pizza_cost += ingredients_constant_cost

            pizzas_cost[pizza_name] = round(pizza_cost + fixed_cost_per_pizza, 2)

        self.send_dict_to_sheet('pizza cost', pizzas_cost)

        return pizzas_cost


    def calculate_pizza_price(self):
        """
        Calculate the pizza price of each pizza 
        """
        while True:
            update_pizza_price = input("Do you want to update the selling price of your pizza? Here's how it works: the pizzeria's fixed cost is divided by the number of pizzas sold on the last market day, the cost of the ingredients used in all the sold pizzas is added, then the total cost is calculated, and a 35% profit is added. If you change the ingredient prices or the number of pizzas sold, the recommended pizza price will also change accordingly.(y/n): ")
            if update_pizza_price == 'y':
                print('calculating...')
                # Call the function passing the 'dictionary of dictionaries'(self.pizzas) to calculate the cost of every pizza
                pizzas_cost = self.calculate_pizza_cost(self.pizzas)
                # Add the fixed cost per pizza and a 30% profit to the cost of each pizza and round the price to two decimal places
                pizzas_price = {pizza_name: round(pizza_cost + pizza_cost * 0.35, 2) for pizza_name, pizza_cost in pizzas_cost.items()}
                self.send_dict_to_sheet('pizza selling price', pizzas_price)
                print('The suggested pizza price has been updated')
                return pizzas_price
            elif update_pizza_price == 'n':
                break
            else:
                print('The suggested pizza price has been updated')
                

    # This method is reusable, it takes two arguments 'sheet_name' which is the name of the worksheet and 'data_dict' a dictionary containing the data to be written
    def send_dict_to_sheet(self, sheet_name, data_dict):
        """
        Send the values of a dictionary to the specified worksheet
        """
        worksheet = SHEET.worksheet(sheet_name)
        headers = worksheet.row_values(1)
        data = [data_dict.get(header, '')for header in headers]
        # Append the data to the next available row
        worksheet.append_row(data)
        print('worksheet is updating')

    def calculate_profit(self):
        """
        Calculate profit
        """
        # Get workdheets
        sales_worksheet = SHEET.worksheet('pizza sales')
        cost_worksheet = SHEET.worksheet('pizza cost')
        # Get data from worksheet
        sales_data = sales_worksheet.get_all_values()
        cost_data = cost_worksheet.get_all_values()
        # Get data from the last market day
        sales_last_day = list(map(int, sales_data[-1])) # Convert to integers
        cost_last_day = list(map(float, cost_data[-1])) # Convert to float
        #initialize variables
        total_revenue = 0
        total_cost = 0
        profit_per_pizza = {}

        for pizza_name, quantity, cost in zip(sales_data[0], sales_last_day, cost_last_day):
            if pizza_name in self.pizzas:
                # Calculate revenue, cost and profit
                revenue = quantity * cost
                total_revenue += revenue
                total_cost += cost
                profit_per_pizza[pizza_name] = revenue - cost
        # Calculate overall profit
        total_profit = total_revenue - total_cost
        profit_per_pizza.update({'total profit' : total_profit})
        self.send_dict_to_sheet('profit', profit_per_pizza)
        return profit_per_pizza

    def calculate_ingredients_used(self):
        """
        Calculate the ingredients used to manufacture all sold pizzas.
        """
        # Get the sales data from the 'pizza sales'
        worksheet = SHEET.worksheet('pizza sales')
        sales_data = worksheet.get_all_values()
        # Get the data for the last market day
        last_market_day = sales_data[-1]
        ingredients_used = {}
        # Calculate the quantity of ingredients used for each flavor
        for pizza_name, quantity in zip(sales_data[0], last_market_day):
            if pizza_name in self.pizzas:
                for ingredient, weight in self.pizzas[pizza_name].items():
                    if ingredient in ingredients_used:
                        ingredients_used[ingredient] += round(weight * int(quantity), 2)
                    else:
                        ingredients_used[ingredient] = round(weight * int(quantity), 2)
        # Calculate the quantity of constant ingredients used
        total_pizzas_sold = sum([int(quantity) for quantity in last_market_day])
        for ingredient, weight in self.ingredients_constant_dict.items():
            if ingredient in ingredients_used:
                ingredients_used[ingredient] += round(weight * total_pizzas_sold, 2)
            else:
                ingredients_used[ingredient] = round(weight * total_pizzas_sold, 2)
        self.send_dict_to_sheet('ingredients used', ingredients_used)
        return ingredients_used

    def remaining_ingredient_stock(self):
        """
        Calculate remaining stock: subtract ingredient used from ingredient stock
        """
        ingredients_used = self.calculate_ingredients_used()
        worksheet = SHEET.worksheet('ingredients stock')
        stock_data = worksheet.get_all_values()
        last_row = stock_data[-1]
        headers = stock_data[0]
        current_stock = {headers[i]: float(last_row[i]) for i in range(len(headers))}
        remaining_stock = {ingredient: round(current_stock[ingredient]- ingredients_used.get(ingredient,0), 2) for ingredient in current_stock}
        self.send_dict_to_sheet('ingredients stock', remaining_stock)
        return remaining_stock

    def update_market_sales(self):
        """
        Take last market sales user input and add to the worksheet
        """
        while True:
            market_sales_input = input('Would you like to input the market day sales? (y/n): ').lower()
            if market_sales_input == 'y':
                print(f'Please input in kg, separated by period "." example: 1 or 1.5 \n')
                pizza_flavors = ['pizza margherita', 'pizza salami', 'pizza arugula', 'pizza chicken', 'pizza prosciutto', 'pizza caprese', 'pizza tuna', 'pizza hawaii', 'pizza funghi', 'pizza meat lovers']
                market_sales = {}
                for flavor in pizza_flavors:
                    sales = self.get_valid_input(f'Please input the market sales of {flavor}: ', float)
                    market_sales[flavor] = int(sales)
                self.send_dict_to_sheet('pizza sales', market_sales)
                break
            elif market_sales_input == 'n':
                break
            else:
                print('')
                print(f'Invalid input. Please enter either "y" or "n". \n')

    def update_ingredient_stock(self):
        """
        Ask if the user wants to update the ingredients stock, if yes, it take the ingredient input and adds to the worksheet
        """
        while True:
            update_stock = input('would you like to update the ingredient stock? (y/n): ').lower()
            if update_stock == 'y':
                print('Please input in kg, separated by period "." example: 1 or 1.5')
                ingredients = ['flour',	'east',	'olive oil', 'sugar', 'salt', 'tomato sauce', 'cheese',	'ham', 'salami', 'parma ham', 'mushroom', 'pineapple', 'meat', 'chicken', 'arugula', 'tuna', 'tomatoes', 'onion', 'olives',	'oregano']
                worksheet = SHEET.worksheet('ingredients stock')
                stock_data = worksheet.get_all_values()
                headers = stock_data[0]
                last_row = stock_data[-1]
                current_stock = {headers[i]: float(last_row[i]) for i in range (len(headers))}
                new_stock = {}
                for ingredient in current_stock:
                    stock = self.get_valid_input(f'please input the stock to add to your actual ingredient stock: {ingredient}: ', float)
                    new_stock[ingredient] = current_stock[ingredient] + float(stock)
                self.send_dict_to_sheet('ingredients stock', new_stock)
                break
            elif update_stock == 'n':
                break
            else:
                print('')
                print(f'Invalid input. Please enter either "y" or "n". \n')

    def update_ingredient_prices(self):
        """
        Ask the user if they want to update the ingredient prices and, if yes, take user input for the new prices and update the 'ingredients kg price' worksheet
        """
        while True:
            update_prices = input('Would you like to update the ingredient prices? (y/n): ').lower()
            if update_prices == 'y':
                print('please input in currency per kg, separated by period "." example: 5 or 5.55')
                ingredients = ['flour',	'east',	'olive oil', 'sugar', 'salt', 'tomato sauce', 'cheese',	'ham', 'salami', 'parma ham', 'mushroom', 'pineapple', 'meat', 'chicken', 'arugula', 'tuna', 'tomatoes', 'onion', 'olives',	'oregano']
                new_prices = {}
                for ingredient in ingredients:
                    price = self.get_valid_input(f'Please input the new price for {ingredient}: ', float)
                    new_prices[ingredient] = float(price)
                self.send_dict_to_sheet('ingredients kg prices', new_prices)
                break
            if update_prices == 'n':
                break
            else:
                print('')
                print(f'Invalid input. Please enter either "y" or "n". \n')

    def generate_report(self):
        """
        Generate a report from all worksheets
        """
        while True:
            generate_report_input = input(f'Would you like to generate a report? (y/n):').lower()
            print('')
            if generate_report_input == 'y':
                # Pizza sales report
                worksheet = SHEET.worksheet('pizza sales')
                pizza_sales_data = worksheet.get_all_values()
                headers = pizza_sales_data[0]
                data = pizza_sales_data[-1:]
                
                ingredients = []
                # Iterate over each row of data
                for row in data:
                    # Iterate over each column in the row
                    for header, value in zip(headers, row):
                        # Format the ingredient and its values and add it to a list
                        ingredients.append(f"{header}: {value}")
                        # Join the list ingredients into a single string separated by slash ' / '
                        ingredients_str = ' | '.join(ingredients)
                print('pizza sales:')
                print(f'{ingredients_str}  \n')
                
                # Ingredients stock report
                worksheet = SHEET.worksheet('ingredients stock')
                ingredients_stock_data = worksheet.get_all_values()
                headers = ingredients_stock_data[0]
                data = ingredients_stock_data[-1:]
                
                ingredients = []
                for row in data:
                    for header, value in zip(headers, row):
                        ingredients.append(f"{header}: {value}")
                        ingredients_str = ' | '.join(ingredients)
                print('ingredients stock:')
                print(f'{ingredients_str}  \n')

                # ingredient kg price report
                worksheet = SHEET.worksheet('ingredients kg prices')
                ingredients_kg_price_data = worksheet.get_all_values()
                headers = ingredients_kg_price_data[0]
                data = ingredients_kg_price_data[-1:]

                ingredients = []
                for row in data:
                    for header, value in zip(headers, row):
                        ingredients.append(f"{header}: {value}")
                        ingredients_str = ' | '.join(ingredients)
                print('ingredients kg price:')
                print(f'{ingredients_str}  \n')

                # ingredients used report
                worksheet = SHEET.worksheet('ingredients used')
                ingredients_used_data = worksheet.get_all_values()
                headers = ingredients_used_data[0]
                data = pizza_sales_data[-1:]

                ingredients = []
                for row in data:
                    for header, value in zip(headers, row):
                        ingredients.append(f"{header}: {value}")
                        ingredients_str = ' | '.join(ingredients)
                print('ingredients used:')
                print(f'{ingredients_str}  \n')

                # pizza selling price
                worksheet = SHEET.worksheet('pizza selling price')
                pizza_selling_price_data = worksheet.get_all_values()
                headers = pizza_selling_price_data [0]
                data = pizza_selling_price_data [-1:]

                ingredients = []
                for row in data:
                    for header, value in zip(headers, row):
                        ingredients.append(f"{header}: {value}")
                        ingredients_str = ' | '.join(ingredients)
                print('pizza selling price:')
                print(f'{ingredients_str}  \n')

                # Pizza cost report
                worksheet = SHEET.worksheet('pizza cost')
                pizza_cost_data = worksheet.get_all_values()
                headers = pizza_cost_data[0]
                data = pizza_cost_data[-1:]

                ingredients = []
                for row in data:
                    for header, value in zip(headers, row):
                        ingredients.append(f"{header}: {value}")
                        ingredients_str = ' | '.join(ingredients)
                print('pizza cost:')
                print(f'{ingredients_str}  \n')
                
                # Profit report
                worksheet = SHEET.worksheet('profit')
                profit_data = worksheet.get_all_values()
                headers = profit_data[0]
                data = profit_data[-1:]

                ingredients = []
                for row in data:
                    for header, value in zip(headers, row):
                        ingredients.append(f"{header}: {value}")
                        ingredients_str = ' | '.join(ingredients)
                print('profit:')
                print(f'{ingredients_str}  \n')
                print(f'Thank you for using: Master Pizza Management. \n')
                break
            elif generate_report_input == 'n':
                break
            else:
                print('')
                print('Invalid input. Please enter either "y" or "n". ')

                

    def get_valid_input(self, prompt, valid_type):
        """
        Check for user 'valid', 'invalid' input
        """
        while True:
            try:
                user_input = valid_type(input(prompt))
                return user_input
            except ValueError:
                print(f'Invalid input. Please enter a valid {valid_type.__name__}.')

def main():
    """
    Main function
    """
    pizza_management = PizzaManagement()
    pizza_management.update_market_sales()
    pizza_management.update_ingredient_stock()
    pizza_management.update_ingredient_prices()
    pizza_management.calculate_pizza_price()
    pizza_management.calculate_ingredients_used()
    pizza_management.calculate_profit()
    pizza_management.remaining_ingredient_stock()
    pizza_management.generate_report()

if __name__ == '__main__':
    main()
