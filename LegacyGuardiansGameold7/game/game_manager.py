# game/game_manager.py
import pandas as pd
from game import level_one_banking, level_two_stock, level_three_portfolio

class GameManager:
    def __init__(self, data_path='data/'):
        self.sessions = {}
        try:
            self.assets_df = pd.read_csv(f"{data_path}mock_assets.csv")
            self.prices_df = pd.read_csv(f"{data_path}mock_market_prices.csv")
            self.missions_df = pd.read_csv(f"{data_path}missions_catalog.csv")
            print("Game data loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Could not find data files in the '{data_path}' path.")
            self.assets_df = self.prices_df = self.missions_df = None

    def start_new_session(self, session_id):
        """开始或重置一个游戏会话"""
        self.sessions[session_id] = {
            "current_level": 1,
            # Level 1 data
            "principal": 10000.0,
            "interest_earned": 0.0,
            "day": 0, # 在第一关，天数表示存款时长
            # Level 2 & 3 data
            "cash": 10000.0,
            "holdings": {}
        }
        return self.sessions[session_id]

    def get_session(self, session_id):
        """获取一个会话，如果不存在则创建"""
        if session_id not in self.sessions:
            return self.start_new_session(session_id)
        return self.sessions[session_id]

    def get_game_state(self, session_id):
        """根据当前关卡获取对应的游戏状态"""
        session_data = self.get_session(session_id)
        level = session_data.get("current_level", 1)

        state = {"currentLevel": level}

        if level == 1:
            state.update(level_one_banking.get_level_state(session_data))
        elif level == 2:
            state.update(level_two_stock.get_level_state(session_data, self.prices_df, self.assets_df))
        elif level == 3:
            state.update(level_three_portfolio.get_level_state(session_data, self.prices_df, self.assets_df, self.missions_df))

        return state

    def handle_action(self, session_id, action_data):
        """根据当前关卡处理玩家操作"""
        session_data = self.get_session(session_id)
        level = session_data.get("current_level", 1)

        if level == 1:
            return level_one_banking.handle_action(session_data, action_data)
        elif level == 2:
            return level_two_stock.handle_action(session_data, action_data, self.prices_df)
        elif level == 3:
            return level_three_portfolio.handle_action(session_data, action_data, self.prices_df)

        return {"success": False, "message": "Invalid level"}

    def advance_level(self, session_id):
        """晋级到下一关"""
        session_data = self.get_session(session_id)
        current_level = session_data.get("current_level", 1)

        if current_level < 3:
            session_data["current_level"] += 1
            # 初始化下一关的数据
            if session_data["current_level"] == 2:
                # 第二关开始时，重置天数和资产
                session_data['day'] = 0
                session_data['cash'] = session_data.pop('principal', 10000) # 继承第一关的本金
                session_data['holdings'] = {}
            elif session_data["current_level"] == 3:
                # 第三关开始时，继承第二关的资产
                session_data['day'] = session_data.get('day', 0)

            return {"success": True, "newLevel": session_data["current_level"]}

        return {"success": False, "message": "You are already at the highest level!"}

    def handle_chat(self, session_id, user_message):
        """处理聊天请求，只在第三关可用"""
        session_data = self.get_session(session_id)
        if session_data.get("current_level") >= 3:
            answer = level_three_portfolio.get_chat_response(session_data, user_message, self.prices_df, self.assets_df, self.missions_df)
            return {"answer": answer}
        else:
            return {"answer": "Chat coach is only available after Level 3."}