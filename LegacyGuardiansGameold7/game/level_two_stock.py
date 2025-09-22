# game/level_two_stock.py
import pandas as pd

LEVEL_GOAL = 10800 # 目标：总资产达到 11000
STOCK_TICKER = "TECH_A" # 本关只允许交易这支股票

# In game/level_two_stock.py

def get_level_state(session_data, prices_df, assets_df):
    """返回第二关前端渲染所需的数据"""
    day = session_data.get('day', 0)
    cash = session_data.get('cash', 10000)
    holdings = session_data.get('holdings', {})
    
    stock_info = assets_df[assets_df['ticker'] == STOCK_TICKER].iloc[0]
    current_price = prices_df.iloc[day][STOCK_TICKER]
    stock_holding = holdings.get(STOCK_TICKER, 0)
    
    total_value = cash + stock_holding * current_price
    
    # --- FIX ---
    # Convert the result to a standard Python bool
    is_goal_met = bool(total_value >= LEVEL_GOAL)

    price_history = []
    for i in range(day + 1):
        price_history.append({
            "date": prices_df.iloc[i]['date'],
            "price": prices_df.iloc[i][STOCK_TICKER]
        })

    return {
        "cash": cash,
        "stock": {
            "ticker": STOCK_TICKER,
            "name": stock_info['name'],
            "price": current_price,
            "holding": stock_holding
        },
        "totalValue": total_value,
        "goal": LEVEL_GOAL,
        "isGoalMet": is_goal_met, # Now this is a safe type
        "priceHistory": price_history,
        "day": day,
        "date": prices_df.iloc[day]['date']
    }

# 在 game/level_two_stock.py 文件中

def handle_action(session_data, action_data, prices_df):
    """处理第二关的操作：买卖股票 或 等待一天"""
    action = action_data.get('action')

    # --- 新增的逻辑 ---
    if action == 'next_day':
        day = session_data.get('day', 0)
        if day < len(prices_df) - 1:
            session_data['day'] += 1
        return {"success": True, "message": "Proceeded to the next day."}
    # --- 新增结束 ---

    try:
        quantity = int(action_data.get('quantity'))
        if quantity <= 0: raise ValueError
    except (ValueError, TypeError):
        return {"success": False, "message": "must provide a valid positive integer quantity"}

    day = session_data.get('day', 0)
    price = prices_df.iloc[day][STOCK_TICKER]

    if action == 'buy':
        cost = price * quantity
        if session_data['cash'] < cost:
            return {"success": False, "message": "Insufficient cash"}
            
        session_data['cash'] -= cost
        session_data['holdings'][STOCK_TICKER] = session_data['holdings'].get(STOCK_TICKER, 0) + quantity
    elif action == 'sell':
        if session_data['holdings'].get(STOCK_TICKER, 0) < quantity:
            return {"success": False, "message": "Insufficient holdings"}
        session_data['holdings'][STOCK_TICKER] -= quantity
        session_data['cash'] += price * quantity
    else:
        return {"success": False, "message": "Unknown action"}

    # 买卖后也自动进入下一天
    if session_data['day'] < len(prices_df) - 1:
        session_data['day'] += 1
        
    return {"success": True, "message": f"Your operation was successful!"}