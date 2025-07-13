from aiogram.fsm.state import StatesGroup, State

class StatesAdminSearchGift(StatesGroup):
    gift_id = State()

class StatesAdminSearchGiftEdit(StatesGroup):
    gift_price = State()

class StatesAdminSettingsEditGiftPrices(StatesGroup):
    edit_price = State()

class StatesAdminSettingsWithdrawGift(StatesGroup):
    edit_text = State()

class StatesAdminSettingsWithdrawMoney(StatesGroup):
    edit_text = State()