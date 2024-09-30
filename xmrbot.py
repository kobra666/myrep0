import requests
import time
import hmac
import hashlib
from datetime import datetime

# MEXC API credentials (replace with your own API key/secret)
api_key = 'mx0vglW3jguUGF9Lp1'
api_secret = 'c7998cd882b64773b8bd92f3061ef9e2'

# Global stats variables
total_trades_today = 0
profit_in_xmr = 0.0
start_date = datetime.now().date()

# Function to generate MEXC signature
def generate_signature(secret, params):
    query_string = '&'.join([f'{key}={value}' for key, value in params.items()])
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

# Function to get current market price for XMR/USDT
def get_market_price(symbol):
    url = f'https://api.mexc.com/api/v3/ticker/price?symbol={symbol}'
    response = requests.get(url).json()
    return float(response['price'])

# Function to place an order and update stats
def place_order(symbol, side, price, quantity):
    global total_trades_today, profit_in_xmr

    url = 'https://api.mexc.com/api/v3/order'
    params = {
        'symbol': symbol,
        'side': side,
        'type': 'LIMIT',
        'price': price,
        'quantity': quantity,
        'recvWindow': 5000,
        'timestamp': int(time.time() * 1000)
    }
    params['signature'] = generate_signature(api_secret, params)
    headers = {'X-MEXC-APIKEY': api_key}
    response = requests.post(url, params=params, headers=headers).json()

    # Update trade stats
    if response.get('status') == 'FILLED':
        total_trades_today += 1
        if side == 'SELL':
            profit_in_xmr -= quantity  # Reduce XMR since we're selling
        elif side == 'BUY':
            profit_in_xmr += quantity  # Increase XMR since we're buying
    return response

# Function to calculate dynamic order size (using a progressive scaling factor)
def calculate_order_size(balance, grid_level, base_order_size, scaling_factor, max_order_size):
    # Progressive scaling: Increase order size by a fixed percentage instead of doubling
    order_size = base_order_size * (scaling_factor ** grid_level)
    # Ensure the order size does not exceed the available balance or max size cap
    return round(min(order_size, max_order_size, balance), 4)

# Function to display daily stats
def display_stats():
    global total_trades_today, profit_in_xmr, start_date
    current_date = datetime.now().date()

    if current_date != start_date:
        # Reset stats for new day
        total_trades_today = 0
        profit_in_xmr = 0.0
        start_date = current_date
    
    print(f"\n--- Daily Stats ---")
    print(f"Total Trades Today: {total_trades_today}")
    print(f"Profit in XMR Today: {profit_in_xmr:.4f} XMR\n")

# Set parameters
symbol = 'XMRUSDT'
balance = 1.3  # Your current XMR balance
base_order_size = 0.02  # Base size in XMR (small starting orders)
grid_interval = 0.002  # 0.2% price intervals
price_range = (120, 180)  # Grid price range
scaling_factor = 1.2  # Progressive growth of 20% per grid level
max_order_size = 0.1  # Maximum order size is capped at 0.1 XMR (or 10% of balance)

# Get current market price
current_price = get_market_price(symbol)
print(f"Current price: {current_price}")

# Loop through and place orders above and below market price
buy_prices = []
sell_prices = []

# Start at grid level 0 (current price)
grid_level = 0

# Set a limit for max grid levels (e.g., 50 levels)
max_grid_levels = 50

for i in range(-max_grid_levels, max_grid_levels + 1):
    # Calculate grid price at each level (0.2% increments)
    grid_price = current_price * (1 + grid_interval * i)

    if grid_price < current_price:
        # For buy orders below the market price
        buy_prices.append(grid_price)
        order_size = calculate_order_size(balance, abs(i), base_order_size, scaling_factor, max_order_size)
        response = place_order(symbol, 'BUY', grid_price, order_size)
        print(f"Placed buy order: {response}")
        
    elif grid_price > current_price:
        # For sell orders above the market price
        sell_prices.append(grid_price)
        order_size = calculate_order_size(balance, i, base_order_size, scaling_factor, max_order_size)
        response = place_order(symbol, 'SELL', grid_price, order_size)
        print(f"Placed sell order: {response}")

# Display daily stats at the end of each round of placing orders
display_stats()

print(f"Buy prices: {buy_prices}")
print(f"Sell prices: {sell_prices}")
