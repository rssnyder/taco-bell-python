# Taco Bell Python

A python sdk for Taco Bell.

## Goal

To be able to order my favorite taco bell items (rip potatoes) via code.

## What Works

1. Logging into Taco Bell account with username/password

2. Adding a single, uncustomized item to your cart

3. Adding a customized item to your cart, either adding extras or modifying what comes by default

4. Getting your cart total cost

## Usage

Sign into your Taco Bell account with your username (email) and password:
```
from tacobell import TacoBell
tbell = TacoBell('rileysndr@gmail.com', '<super secure password>')
```

Add an item to your cart:
```
tbell.add_to_cart('Cheesy Bean and Rice Burrito')
```

Add a customized item to your cart:
```
tbell.add_to_cart_customized(
    'Cheesy Bean and Rice Burrito',
    sauces=[
        'Red Sauce',
        'Avocado Ranch'
    ],
    addons=[
        '3 Cheese Blend'
    ]
)
```

```
tbell.add_to_cart_customized(
    'Cheesy Bean and Rice Burrito',
    modify=[
        ('Creamy Jalapeño Sauce', 'EXTRA')
    ]
)
```

Get your cart total:
```
tbell.cart_total()
```

## Current problems/issues

I am accomplishing this by exporling the network calls made on the Taco Bell site. I will publish the API endpoints I have found and how to use them.

It seems like logging in and doing actions is hit or miss. I am unsure if this is some sort of anti-robot protections taco bell has or they are just blocking my IP every once and a while.

There is no great way to list items, so for now I am building a relationship of item names -> product codes. Hopefull this can be replaced by a search function later.

## Known API Endpoints

### Root URL: `https://www.tacobell.com`

### Login: POST `/j_spring_security_check`
Data:
```
{
    'j_username': <username>,
    'j_password': <password>,
    'CSRFToken': <CSRF Token>
}
```

### Cart Total: GET `/cart/miniCart/SUBTOTAL`
Always returns 200 status code

### Add uncustomized item to cart: POST `/cart/add`
Data:
```
{
    'productCodePost': <product code>,
    'CSRFToken': <CSRF Token>
}
```

### Get options for item customization: GET `/p/<product code>/customizationOverlay?store=<store id (optional)>`
Example return data in `tests/customizations.json`

### Add customized item to cart: POST `/cart/add-composite`
Data:
```
{
    "baseProduct": <product code>,
    "code": <product code>,
    "qty": <quantity>,
    "includeProduct": [
        {
            'code': <modifier code>,
            'group': 'included',
            'qty': 1
        }
    ],
    "modifierProduct": [
        {
            'code': <modifier code>,
            'group': <modifier type>,
            'qty': 1
        }
    ]
}
```

For these, you can change the items that come on the product normall with the `includeProduct` list. You can then add extra items with the `modifierProduct` list.

Get modification options: `p/<product_code>/customizationOverlay?store=<store_id>`
The return data here is a huge JSON with all your options, the meat of the code is taking your modification input and finding the correct modifier code for what you want.


## Contributing

Contributions are obviously welcome. Exporing the backend Taco Bell API is most of the work. Until we can get a good source for product codes I will be putting them in the code by hand.

Things on the ToDo list:

1. Query for list of products and codes

2. Select/Find store to send order to

3. Select payment method

4. Checkout/Submit order
