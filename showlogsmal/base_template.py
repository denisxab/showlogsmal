from typing import Union

from urwid import Edit, Text, set_encoding


class ShowLogFileBase:
    set_encoding('utf8')
    palette = [
        ('label_text1', 'light cyan', 'black',),
    ]

    __slots__ = [
        "arr_console_log",
        "time_update",
        "console_columns",
        "menu",
        "gInfoOverlay",
        "loop",
    ]

    def ExecuteCommand(self, output_widget: Union[Edit, Text], command: str): ...
