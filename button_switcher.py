import logging
from typing import List, Optional


from loader import max_inline_buttons



class ButtonSwitcher():
    """class calculates values in Advertisement buttons"""
    def __init__(self, buttons_count: int) -> None:
        self.buttons = self._check_buttons_count(buttons_count)
        self.current = 1


    def _check_buttons_count(self, buttons_count: int):
        if buttons_count < 1:
            raise ValueError("invalid parameter buttons_count")
        
        return [str(i) for i in range(1, buttons_count + 1)]
    

    def get_buttons(self, pressed_button: str = None) -> List[str]:
        buttons = []
        if not pressed_button:
            pressed_button = self.buttons[0]

        if pressed_button in self.buttons[0:2]:
            buttons = [button for button in self.buttons[:max_inline_buttons - 1]]
            buttons.append(self.buttons[-1])
            # self.__edit_buttons_starting_view(buttons)

        elif pressed_button in self.buttons[-2:]:
            buttons.append(self.buttons[0])
            buttons.extend([button for button in self.buttons[-max_inline_buttons + 1:]])
            # self.__edit_buttons_ending_view(buttons)
        else:
            buttons.append(self.buttons[0])
            buttons.extend([button for button in self.buttons[int(pressed_button) - 2: int(pressed_button) + 1]])
            buttons.append(self.buttons[-1])
            # self.__edit_buttons_middle_view(buttons, pressed_button)
        
        return buttons


    def __edit_buttons_starting_view(self, buttons: List[str]) -> None:
        # buttons[0] = "«{0:s}".format(buttons[0])
        buttons[0] = "•{0:s}•".format(buttons[0])
        buttons[-1] = "{0:s}»".format(buttons[-1])


    def __edit_buttons_ending_view(self, buttons: List[str]) -> None:
        buttons[0] = "«{0:s}".format(buttons[0])
        buttons[-1] = "•{0:s}•".format(buttons[0])
        # buttons[-1] = "{0:s}»".format(buttons[-1])


    def __edit_buttons_middle_view(self, buttons: List[str], pressed_button) -> None:
        buttons[0] = "«{0:s}".format(buttons[0])
        pressed_index = buttons.index(pressed_button)
        buttons[pressed_index] = "•{0:s}•".format(buttons[pressed_index])
        buttons[-1] = "{0:s}»".format(buttons[-1])