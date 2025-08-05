from aiogram.fsm.state import State, StatesGroup

class ConversionStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_choice = State()