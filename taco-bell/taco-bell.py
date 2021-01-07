import requests
import json
from time import sleep

TACO_BELL_URL = 'https://www.tacobell.com/'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/39742327938 Firefox/78.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://www.tacobell.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.tacobell.com',
    'TE': 'Trailers'
}

PRODUCTS = {
    'Loaded Nacho Taco': 24537,
    'Chicken Chipotle Melt': 28158,
    'Beef Burrito': 23149,
    'Cheesy Bean and Rice Burrito': 22283,
    'Cheesy Roll Up': 22152,
    'Chips and Nacho Cheese Sauce': 22500,
    'Cinnamon Twists': 22525,
}


class TacoBell():

    def __init__(self, username: str, password: str, config: dict = None):
        """
        Create a connection to your Taco Bell account
        """

        # Create session to save cookies
        self.session = requests.Session()

        # Give option to pass cookie values for testing
        if config:
            self.login_config(config)
        else:
            self.login(username, password)

        pass


    def login(self, username: str, password: str):
        """
        Log into tacobell.com
        """

        # Get the login page to fill standard TB cookies
        response = self.session.get(
            TACO_BELL_URL + 'login',
            headers=HEADERS
        )

        # Pull out inital cookies
        cookies = response.cookies.get_dict()

        # Pull our CSRF for future use
        self.csrf = cookies.get('CSRFToken')

        # Request payload for login
        params = {
            'j_username': username,
            'j_password': password,
            'CSRFToken': self.csrf
        }

        # Make login POST call
        response = self.session.post(
            TACO_BELL_URL + 'j_spring_security_check',
            headers=HEADERS,
            params=params
        )

        # Catch unsuccessful login
        if response.status_code != 200:
            print('unable to login')
        else:
            print('logged in')

        pass


    def login_config(self, config: dict):
        """
        Manually login using cookie values
        """

        # Set CSRF in cookies
        self.csrf = config.get('CSRFToken')

        # Set cookies based on config given
        for cookie in config:
            self.session.cookies.set(cookie, config[cookie])

        # Get the login page to fill other standard TB cookies
        self.session.get(
            TACO_BELL_URL + 'login',
            headers=HEADERS
        )

        pass


    def cart_total(self, retry: bool = True) -> str:
        """
        Get the current total cost of the items in your cart
        """

        # Make call to get cart total
        response = self.session.get(
            TACO_BELL_URL + '/cart/miniCart/SUBTOTAL',
            headers=HEADERS
        )

        # Load response data
        cart_data = json.loads(response.text)

        # Print target data
        return cart_data.get('miniCartPrice', "$0.00")


    def add_to_cart(self, product_name: str, retry: bool = True) -> bool:
        """
        Add an item to your account cart
        """

        # Make sure this is a known product
        if product_name not in PRODUCTS:
            print('unknown product')
            pass

        # Request payload for single, unmodified item
        params = {
            'productCodePost': PRODUCTS[product_name],
            'CSRFToken': self.csrf
        }

        # Make POST call to add item to cart
        response = self.session.post(
            TACO_BELL_URL + '/cart/add',
            headers=HEADERS,
            params=params
        )

        # Catch "The page you requested is no longer active"
        if response.status_code == 403:

            # Retry to avoid lockout
            if retry:
                sleep(4)
                self.add_to_cart(product_name, retry=False)
                pass

            return False
        # Deal with information that was returned
        else:
            return True


    def add_to_cart_customized(self, product_name: str, quantity: int = 1, modify: list = [], sauces: list = [], addons: list = []) -> bool:
        """
        Add an item to your account cart with customizations and quantity
        """

        # Lists of customizations you can make
        modifications = []
        included_changes = []

        # Make sure this is a known product
        if product_name not in PRODUCTS:
            print('unknown product')
            pass

        # Grab current customization options for this product
        customization_options = self.get_customizations(PRODUCTS[product_name])
            
        # Go through every requested modification
        for item in modify:
            
            # Find if requested item comes included
            for included in customization_options.get('includes', []):
                if included['name'] == item[0]:
                    
                    # Find the requested modification
                    for option in included['variantOptions']:
                        if option['modifierType'] == item[1]:
                            included_changes.append({
                                'code': option['code'],
                                'group': 'included',
                                'qty': 1
                            })

        # Sauce
        for sauce in customization_options.get('sauces', []):
            if sauce.get('name') in sauces:
                modifications.append({
                    'code': int(sauce['variantOptions'][0]['code']),
                    'group': 'sauces',
                    'qty': 1
                })

        # Addon
        for addon in customization_options.get('addons', []):
            if addon.get('name') in addons:
                modifications.append({
                    'code': int(addon['variantOptions'][0]['code']),
                    'group': 'addons',
                    'qty': 1
                })

        # Build order data with customization lists
        order = {
            "baseProduct": str(PRODUCTS[product_name]),
            "code": str(PRODUCTS[product_name]),
            "qty": str(quantity),
            "includeProduct": included_changes,
            "modifierProduct": modifications
        }


        # Different headers for this request
        HEADERS['CSRFToken'] = self.csrf
        HEADERS['Content-Type'] = 'application/json'

        # Make POST call with order data
        response = self.session.post(
            TACO_BELL_URL + '/cart/add-composite',
            headers=HEADERS,
            json=order
        )

        # Catch "The page you requested is no longer active"
        if response.status_code == 403:
            return False
        # Print information on what was added to the cart
        else:
            return True


    def get_customizations(self, product_code: str, store_id: int = None, retry: bool = True):
        """
        Get all the options for customizing this item
        """

        # Query options, store code
        options = ''
        if store_id:
            options = f'?store={store_id}'

        # Make GET call for customization options data
        response = self.session.get(
            TACO_BELL_URL + f'p/{product_code}/customizationOverlay{options}',
            headers=HEADERS
        )

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None
