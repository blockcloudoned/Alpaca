# alpaca_cli.py
import os
import sys
import argparse
import json
from alpaca_trade_api.rest import REST, APIError
from alpaca_trade_api.common import URL
from dotenv import load_dotenv

load_dotenv()

# --- Core Logic Functions (Return Data) ---

def setup_api_client():
    """
    Sets up and authenticates the Alpaca API client using environment variables.
    Exits gracefully if keys are not found.
    """
    try:
        api_key = os.environ['APCA_API_KEY_ID']
        secret_key = os.environ['APCA_API_SECRET_KEY']
        base_url = os.environ.get('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')
    except KeyError as e:
        print(f"🔴 Critical Error: Environment variable {e} not set.")
        sys.exit(1)
        
    return REST(key_id=api_key, secret_key=secret_key, base_url=URL(base_url))

def get_account_status_data(api):
    """Returns account status and key metrics as a dictionary."""
    try:
        account = api.get_account()
        return {
            "id": account.id,
            "status": account.status,
            "currency": account.currency,
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "equity": float(account.equity),
            "pattern_day_trader": account.pattern_day_trader,
        }
    except APIError as e:
        return {"error": str(e)}

def list_positions_data(api):
    """Returns all open positions as a list of dictionaries."""
    try:
        positions = api.list_positions()
        return [
            {
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "market_value": float(pos.market_value),
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
            }
            for pos in positions
        ]
    except APIError as e:
        return {"error": str(e)}

# --- Original CLI Functions (Now Use Core Logic) ---

def get_account_status(api, args):
    """Fetches and displays the account status and key metrics."""
    data = get_account_status_data(api)
    if "error" in data:
        print(f"🔴 API Error fetching account: {data['error']}")
    else:
        print("\n---\n📋 Fetching Account Status...\n---")
        status = "ACTIVE" if data['status'] == 'ACTIVE' else "RESTRICTED"
        print(f"Account Status:       {status} ({data['id']})")
        print(f"Currency:             {data['currency']}")
        print(f"Portfolio Value:      ${data['portfolio_value']:, .2f}")
        print(f"Buying Power:         ${data['buying_power']:, .2f}")
        print(f"Daytrade Count:       {data['daytrade_count']}")
        print(f"Pattern Day Trader:   {'Yes' if data['pattern_day_trader'] else 'No'}")

def list_positions(api, args):
    """Fetches and displays all open positions."""
    data = list_positions_data(api)
    if "error" in data:
        print(f"🔴 API Error listing positions: {data['error']}")
    elif not data:
        print("No open positions found.")
    else:
        print("\n---\n📊 Fetching Open Positions...\n---")
        print(f"{'Symbol':<10} {'Qty':<10} {'Avg Entry Price':<18} {'Current Price':<15} {'P/L ($)':<15} {'P/L (%)':<15}")
        print("-" * 90)
        for pos in data:
            pl_usd = f"{pos['unrealized_pl']:, .2f}"
            pl_pct = f"{pos['unrealized_plpc'] * 100:,.2f}%"
            print(f"{pos['symbol']:<10} {pos['qty']:<10} ${pos['avg_entry_price']:<17,.2f} ${pos['current_price']:<14,.2f} {pl_usd:<15} {pl_pct:<15}")

def place_order(api, args):
    """Places a new order with the specified parameters."""
    print(f"\n---\n🛒 Placing Order for {args.qty} {args.symbol}...\n---")
    try:
        order = api.submit_order(
            symbol=args.symbol,
            qty=args.qty,
            side=args.side,
            type=args.type,
            time_in_force=args.time_in_force
        )
        print(f"✅ Order submitted successfully!")
        print(f"    ID:           {order.id}")
        print(f"    Symbol:       {order.symbol}")
        print(f"    Qty:          {order.qty}")
        print(f"    Side:         {order.side}")
        print(f"    Type:         {order.type}")
        print(f"    Status:       {order.status}")
    except APIError as e:
        print(f"🔴 API Error placing order: {e}")

def list_orders(api, args):
    """Lists existing orders, filtered by status."""
    print(f"\n---\n📄 Fetching Orders (Status: {args.status})...\n---")
    try:
        orders = api.list_orders(status=args.status, limit=args.limit)
        if not orders:
            print(f"No orders found with status '{args.status}'.")
            return
            
        print(f"{'ID':<30} {'Symbol':<10} {'Qty':<8} {'Side':<8} {'Type':<10} {'Status':<12}")
        print("-" * 80)
        for order in orders:
           print(f"{(order.id or 'N/A'):<30} {(order.symbol or 'N/A'):<10} {(order.qty or 'N/A'):<8} {(order.side or 'N/A'):<8} {(order.type or 'N/A'):<10} {(order.status or 'N/A'):<12}")

    except APIError as e:
        print(f"🔴 API Error listing orders: {e}")


def main():
    """The main function to parse commands and execute them."""
    parser = argparse.ArgumentParser(description="A robust CLI for the Alpaca Trading API.", prog="robust_alpaca_cli")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # 'account' command
    parser_account = subparsers.add_parser('account', help='Get account status and details.')
    parser_account.set_defaults(func=get_account_status)

    # 'positions' command
    parser_positions = subparsers.add_parser('positions', help='List all open positions.')
    parser_positions.set_defaults(func=list_positions)

    # 'orders' command group
    parser_orders = subparsers.add_parser('orders', help='Manage orders (list, place).')
    orders_subparsers = parser_orders.add_subparsers(dest="orders_command", help="Order actions")
    orders_subparsers.required = True
    
    # 'orders list' command
    parser_orders_list = orders_subparsers.add_parser('list', help='List existing orders.')
    parser_orders_list.add_argument('--status', type=str, default='open', choices=['open', 'closed', 'all'], help='Filter orders by status.')
    parser_orders_list.add_argument('--limit', type=int, default=50, help='Max number of orders to return.')
    parser_orders_list.set_defaults(func=list_orders)
    
    # 'orders place' command
    parser_orders_place = orders_subparsers.add_parser('place', help='Place a new order.')
    parser_orders_place.add_argument('--symbol', type=str, required=True, help='The stock symbol to trade.')
    parser_orders_place.add_argument('--qty', type=int, required=True, help='Number of shares to trade.')
    parser_orders_place.add_argument('--side', type=str, required=True, choices=['buy', 'sell'], help='Order side.')
    parser_orders_place.add_argument('--type', type=str, default='market', choices=['market', 'limit'], help='Order type.')
    parser_orders_place.add_argument('--time_in_force', type=str, default='gtc', choices=['day', 'gtc', 'opg'], help='Time in force.')
    parser_orders_place.set_defaults(func=place_order)

    args = parser.parse_args()
    
    # Setup the API client once
    api = setup_api_client()
    
    # Call the function associated with the parsed command
    args.func(api, args)


if __name__ == "__main__":
    main()