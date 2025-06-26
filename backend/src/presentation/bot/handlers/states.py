from aiogram.fsm.state import StatesGroup, State

class StatesAdminSettingsWithdrawGift(StatesGroup):
    edit_text = State()

class StatesAdminSettingsWithdrawMoney(StatesGroup):
    edit_text = State()