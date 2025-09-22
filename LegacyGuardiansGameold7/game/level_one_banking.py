# game/level_one_banking.py
import math

LEVEL_GOAL = 10400  # 目标：本金达到 10500

def get_level_state(session_data):
    """返回第一关前端渲染所需的数据"""
    principal = session_data.get('principal', 10000)
    interest_earned = session_data.get('interest_earned', 0)
    is_goal_met = bool(principal >= LEVEL_GOAL)
    
    return {
        "principal": principal,
        "interestEarned": interest_earned,
        "goal": LEVEL_GOAL,
        "isGoalMet": is_goal_met,
        "availableRates": [
            {"period": 10, "rate": 0.015}, # 10天 年化 1.5%
            {"period": 30, "rate": 0.025}, # 30天 年化 2.5%
            {"period": 60, "rate": 0.04},  # 60天 年化 4.0%
        ]
    }

def handle_action(session_data, action_data):
    """处理第一关的操作：存款"""
    action = action_data.get('action')
    if action == 'deposit':
        try:
            period = int(action_data.get('period'))
            rate = float(action_data.get('rate'))
            principal = session_data.get('principal', 10000)

            # 利息计算公式: 本金 * 年化利率 * (存款天数 / 365)
            interest = principal * rate * (period / 365.0)
            
            session_data['principal'] += interest
            session_data['interest_earned'] = session_data.get('interest_earned', 0) + interest
            session_data['day'] = session_data.get('day', 0) + period # 时间流逝
            

            return {"success": True, "message": f"Successfully deposited for {period} days and earned ${interest:.2f} in interest!"}
        except (ValueError, TypeError):
            return {"success": False, "message": "Invalid deposit parameters"}

    return {"success": False, "message": "Unknown action"}
