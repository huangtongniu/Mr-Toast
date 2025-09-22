# game/level_three_portfolio.py
import pandas as pd
import openai

def get_level_state(session_data, prices_df, assets_df, missions_df):
    """返回第三关前端渲染所需的数据"""
    day = session_data.get('day', 0)
    cash = session_data.get('cash', 10000)
    holdings = session_data.get('holdings', {})
    holdings_with_cash = {"_cash": cash, **holdings}

    total_assets = calculate_portfolio_value(holdings_with_cash, day, prices_df)
    current_prices = prices_df.iloc[day].to_dict()
    todays_missions = missions_df[missions_df["effect_days"].apply(lambda s: str(day) in str(s))]

    assets_info = [{
        "ticker": asset['ticker'], "name": asset['name'], "sector": asset['sector'],
        "price": round(current_prices.get(asset['ticker'], 0), 2),
        "holding": holdings.get(asset['ticker'], 0)
    } for _, asset in assets_df.iterrows()]

    return {
        "day": day + 1,
        "date": current_prices.get("date", ""),
        "cash": round(cash, 2),
        "totalAssets": round(total_assets, 2),
        "assets": assets_info,
        "missions": todays_missions.to_dict('records'),
        "portfolioHistory": get_history_for_chart(holdings_with_cash, day, prices_df),
        "aiCoachInitialTips": get_ai_coach_advice(holdings_with_cash, day, assets_df, prices_df)
    }

def handle_action(session_data, action_data, prices_df):
    """处理第三关的操作"""
    action = action_data.get('action')
    day = session_data.get('day', 0)

    if action == 'next_day':
        if day < len(prices_df) - 1:
            session_data['day'] += 1
        return {"success": True}

    if action in ('buy', 'sell'):
        ticker = action_data.get("ticker")
        try: quantity = int(action_data.get("quantity", 1)); assert quantity > 0
        except: return {"success": False, "message": "Invalid quantity"}

        price = prices_df.iloc[day].get(ticker)
        if price is None: return {"success": False, "message": "Invalid ticker number"}

        if action == 'buy':
            cost = price * quantity
            if session_data["cash"] < cost: return {"success": False, "message": "Insufficient cash"}
            session_data["cash"] -= cost
            session_data["holdings"][ticker] = session_data["holdings"].get(ticker, 0) + quantity
        else: # sell
            if session_data["holdings"].get(ticker, 0) < quantity: return {"success": False, "message": "Insufficient holdings"}
            session_data["holdings"][ticker] -= quantity
            session_data["cash"] += price * quantity
        return {"success": True}

    return {"success": False, "message": "Unknown action"}

def get_chat_response(session_data, user_message, prices_df, assets_df, missions_df):
    """与ChatGPT交互"""
    if not openai.api_key:
        return "抱歉，AI聊天功能当前不可用，因为未配置API密钥。"

    day = session_data['day']
    holdings_str = ", ".join([f"{t}: {q}股" for t, q in session_data['holdings'].items() if q > 0]) or "无"
    cash_str = f"${session_data['cash']:.2f}"
    current_prices = prices_df.iloc[day].to_dict()
    prices_str = ", ".join([f"{t}: ${current_prices.get(t, 0):.2f}" for t in assets_df['ticker']])
    missions = missions_df[missions_df["effect_days"].apply(lambda s: str(day) in str(s))]
    mission_str = "; ".join([f"{m['title']}({m['hint']})" for _, m in missions.iterrows()]) or "无"

    def get_chat_response(session_data, user_message, prices_df, assets_df, missions_df):
        """与ChatGPT交互"""
        if not openai.api_key:
            return "Sorry, the AI chat feature is currently unavailable because the API key is not configured."

    day = session_data['day']
    # Note: Translated "股" to "shares" and "无" to "None"
    holdings_str = ", ".join([f"{t}: {q} shares" for t, q in session_data['holdings'].items() if q > 0]) or "None"
    cash_str = f"${session_data['cash']:.2f}"
    current_prices = prices_df.iloc[day].to_dict()
    prices_str = ", ".join([f"{t}: ${current_prices.get(t, 0):.2f}" for t in assets_df['ticker']])
    missions = missions_df[missions_df["effect_days"].apply(lambda s: str(day) in str(s))]
    mission_str = "; ".join([f"{m['title']}({m['hint']})" for _, m in missions.iterrows()]) or "None"

    system_prompt = (
        "You are a patient and skilled investment coach guiding a teenage player in an investment simulation game called 'Legacy Guardian'."
        "Your answers must be professional, friendly, easy to understand, and always in English."
        "Provide advice based on the game state provided below, in conjunction with the player's questions. Do not give real-world investment advice outside of the game."
    )
    context_prompt = (
        f"--- Game Status ---\nToday is Day {day + 1}.\nPlayer Cash: {cash_str}\nPlayer Holdings: {holdings_str}\n"
        f"Today's Market Prices: {prices_str}\nToday's Special Events: {mission_str}\n--- Player's Question ---"
    )
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300, temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return "Sorry, my brain seems to have short-circuited. I can't answer right now. Please try again later."

# --- 通用辅助函数 ---
def calculate_portfolio_value(holdings, day_idx, prices_df):
    price_map = prices_df.iloc[day_idx].to_dict()
    pv = holdings.get("_cash", 0.0)
    for ticker, quantity in holdings.items():
        if ticker != "_cash":
            pv += quantity * price_map.get(ticker, 0)
    return pv

def get_history_for_chart(holdings, to_day, prices_df):
    history = []
    step = max(1, to_day // 30) if to_day > 0 else 1
    for i in range(0, to_day + 1, step):
        value = calculate_portfolio_value(holdings, i, prices_df)
        history.append({"date": prices_df.iloc[i]["date"], "value": round(value, 2)})
    if to_day > 0 and to_day % step != 0:
        value = calculate_portfolio_value(holdings, to_day, prices_df)
        history.append({"date": prices_df.iloc[to_day]["date"], "value": round(value, 2)})
    return history

def get_ai_coach_advice(holdings, day, assets_df, prices_df):
    """生成AI教练的初始建议"""
    price_map = prices_df.iloc[day].to_dict()
    tickers = [t for t in holdings if t != "_cash"]
    values, sectors = [], []
    for t in tickers:
        val = holdings.get(t, 0) * price_map.get(t, 0.0)
        values.append(val)
        sector_info = assets_df[assets_df["ticker"] == t]
        if not sector_info.empty: sectors.append(sector_info["sector"].values[0])

    total_invested = sum(values)
    cash = holdings.get("_cash", 0.0)
    total = total_invested + cash
    if total == 0: total = 1

    tips = []
    if total <= 10000 and total_invested < 1:
        return ["Welcome to the portfolio level! You can start by buying some assets, or ask me any questions about investing."]
    if cash / total > 0.5:
        tips.append("Your cash ratio is quite high. Consider buying in batches to try and secure profits.")
    if total_invested > 0:
        by_sector = {s: 0 for s in assets_df['sector'].unique()}
        for v, s in zip(values, sectors):
            by_sector[s] += v
        if by_sector and max(by_sector.values()) / total_invested > 0.6:
            tips.append("Your portfolio is too concentrated in a single sector. It's advisable to diversify your investments.")
    if not tips:
        tips.append("Your strategy looks solid. Feel free to ask me for specific advice about today's market or your holdings.")

    return tips