from typing import List, Callable, Union, AnyStr

from urwid import Frame, LineBox, Text, Edit, ListBox, SimpleFocusListWalker, Divider, Pile

from base_template import ShowLogFileBase


class LogObj:
    """
    Структура для хранения информации лог файла
    """
    __slots__ = [
        "index",
        "name",
        "pause",
    ]

    def __init__(self, index: int, name: str):
        """
        :param index: Уникальное индекс
        :param name: Имя, будет заголовком консолей
        """
        self.index = index
        self.name = name
        #: Нужен для установки паузы в вывод в консоль
        self.pause = False


class ConsolesPile(Pile):
    """
    Колоны с консолями
    """

    __slots__ = [
        "root",
        "__index_column",
    ]

    def __init__(self, title_names: tuple[LogObj], root: ShowLogFileBase, focus_item=0, ):
        """
        :param title_names:
        :param root:
        :param focus_item:
        """

        self.root: ShowLogFileBase = root
        #: Обновляем максимум существующий консолей
        ConsoleFrame.new_max_column(len(title_names))
        #: Список консолей
        widget_list = [ConsoleFrame(_console_log) for _console_log in title_names]
        #: Для цикличного перемещения
        self.__index_column = [focus_item, len(title_names) - 1]
        super().__init__(
            widget_list,
            focus_item=focus_item,
        )

    def SendTextInIndex(self, index_: int, text_: Union[str, AnyStr]):
        """
        Вставить текст в консоль по его индексу:
        """
        self.contents[index_][0].body_txt.txt.set_edit_pos(0)
        self.contents[index_][0].body_txt.txt.insert_text(text_)
        self.contents[index_][0].body_txt.txt.set_edit_pos(0)

    def mouse_event(self, size, event, button, col, row, focus):
        """
        Обработка событие мыши
        """
        #: Логика прокрутка консоли с помощью колес мыши
        match button:
            case 5.0:
                self.keypress(size, "down")
            case 4.0:
                self.keypress(size, "up")
        return super().mouse_event(size, event, button, col, row, focus)

    def keypress(self, size, key: str):
        """Горячие клавиши:
        - ``f1`` = Влево
        - ``f3`` = Верх
        - ``f4`` = Вправо
        - ``f5`` = Приостановить/Продолжить консоль на которой сейчас фокус
        - ``f6`` = Показать окно информации
        - ``Tab``= Вправо
        - ``shif + ЛКМ`` = Выделить текст
        - ``shif + ctrl + C`` = Копировать выделенный текст
        - ``shif + ctrl + V`` = Вставить текст
        """

        focus_console: ConsoleFrame = self.contents[self.focus_position][0]

        # Спец клавиши
        match key:
            # В право
            case "tab":
                self.set_focus(self._next_focus())
            case 'f4':
                self.set_focus(self._next_focus())
            # Влево
            case 'f1':
                self.set_focus(self._last_focus())
            # Приостановить/Продолжить вывод в консоль
            case 'f5':
                _cl: ConsoleFrame = focus_console
                if _cl.console_log.pause:
                    _cl.console_log.pause = False
                    _cl.header.base_widget.set_text(_cl.header.base_widget.text.replace("PAUSE: ", ""))
                else:
                    _cl.console_log.pause = True
                    _cl.header.base_widget.set_text(f"PAUSE: {_cl.header.base_widget.text}")
            # Фокус на главное текстовое поле
            case 'f3':
                focus_console.set_focus("body")
            # Показать окно информации
            case 'f6':
                _menu_console: MenuConsole = self.root.gInfoOverlay.top_w
                #: Отобразить подсказки
                _menu_console.root.ExecuteCommand(_menu_console.output_menu, "help")
                #: Окно информации на главном плане
                self.root.loop.widget = self.root.gInfoOverlay

            # case 'f2':
            #     self.contents[self.focus_position][0].set_focus("footer")

        # Если в фокусе текстовое поле для команд, то перенаправляет вывод клавиш в него
        if focus_console.get_focus() == "footer":
            if key not in ("down", "up"):
                return focus_console.footer.base_widget.keypress([size, ], key)
        else:

            # Отправляем кнопки в обработчики текстового поля
            return focus_console.body.keypress(size, key)

    def update_widget(self, loop=None, data=None):
        """
        Пока нет обращений к приложению оно не обновляет состояние, поэтому имитируем
        обращение, для обновления данных.
        """
        self.get_focus()
        loop.set_alarm_in(0.1, self.update_widget)

    def __del_widget_in_index(self, index):
        self.contents.pop(index)

    def __append_widget(self, title):
        self.contents.append([ConsoleFrame(title), self.options()])

    def _next_focus(self) -> int:
        """
        Переместить фокус в правую консоль
        """
        if self.__index_column[0] < self.__index_column[1]:
            self.__index_column[0] += 1
        else:
            self.__index_column[0] = 0
        return self.__index_column[0]

    def _last_focus(self) -> int:
        """
        Переместить фокус в левую консоль
        """
        if self.__index_column[0] > 0:
            self.__index_column[0] -= 1
        else:
            self.__index_column[0] = self.__index_column[1]
        return self.__index_column[0]

    # def UpdateTitle(self, title_names: tuple[str]):
    #     """
    #     Создать новые консоли
    #     """
    #     for _ in range(self.__index_column[1] + 1):
    #         self.__del_widget_in_index(0)
    #
    #     ConsoleFrame.new_max_column(len(title_names))
    #
    #     for name in title_names:
    #         self.__append_widget(name)
    #
    #     self.set_focus(0)
    #     self.__index_column[0] = 0
    #     self.__index_column[1] = len(title_names) - 1


class ConsoleFrame(Frame):
    """
    Объект консоль
    """
    MAX_COLUMN: List[int] = [0, 0]

    __slots__ = [
        "console_log",
        "header",
        "body_txt",
    ]

    def __init__(self, console_log: LogObj):
        self.console_log: LogObj = console_log
        #: Получаем символы для создания рамки консоли
        Ltop_top, Ltop_bot, Rtop_top, Rtop_bot, \
        bod_line, \
        Lbot_top, Lbot_bot, Rbot_top, Rbot_bot, = self.__get_char_pile()

        #: Заголовок
        self.header = LineBox(Text(self.console_log.name, align="center"),
                              tlcorner=Ltop_top,
                              blcorner=Ltop_bot,
                              rline=bod_line,
                              trcorner=Rtop_top,
                              brcorner=Rtop_bot,
                              )

        #: Многострочное текстовое поле
        self.body_txt = EditListBox()

        #: Основное текстовое поле
        body = LineBox(self.body_txt,
                       bline='',
                       tline='',
                       rline=bod_line,
                       )

        #: Однострочное текстовое поле для команд
        # footer = LineBox(EditLine(fun_execute_command=self.ExecuteCommand, output_widget=self.body_txt.txt, ),
        #                  tlcorner=Lbot_top,
        #                  blcorner=Lbot_bot,
        #                  rline=bod_line,
        #                  trcorner=Rbot_top,
        #                  brcorner=Rbot_bot,
        #                  )

        super().__init__(body, self.header, None, focus_part='body')

    # @staticmethod
    # def ExecuteCommand(output_widget: Union[Edit, Text],
    #                    command: Literal["clear", "save"]):
    #     """
    #     Выполнение определённых команд
    #
    #     - `clear` = Отчистить консоль
    #     - `save <name> <path>` = сохранить в файл
    #     """
    #     command = command.split()
    #
    #     # Отчистка консоли выходного виджета
    #     if command[0] == "clear":
    #         output_widget.set_edit_text('')
    #
    #     # Сохранение данных из выходного виджета
    #     elif len(command) == 3 and command[0] == "save":
    #
    #         output_widget.set_edit_pos(0)
    #         try:
    #             path_ = "{}/{}".format(command[2].replace("\\", "/"), command[1])
    #             with open(path_, "w", encoding="utf-8") as f:
    #                 f.write(output_widget.get_edit_text())
    #
    #             output_widget.text_menu.insert_text(f"# Save {command[1]} >> {path_}\n")
    #
    #         except (FileNotFoundError, FileExistsError, PermissionError) as e:
    #             output_widget.insert_text(f"# {e}")
    #
    #         output_widget.set_edit_pos(0)

    @classmethod
    def new_max_column(cls, i: int):
        """Обновить максимум консолей"""
        cls.MAX_COLUMN[0] = 0
        cls.MAX_COLUMN[1] = i

    def __get_char_table(self):
        """Вернуть символы для создания рамки консоли"""
        res = "┌", "├", "┐", "┤", \
              "│", \
              '├', "└", "┤", "┘",

        if self.MAX_COLUMN[1] > 1:
            if self.MAX_COLUMN[0] == 0:
                res = "┌", "├", "─", "─", \
                      " ", \
                      '├', "└", "─", "─",

            elif self.MAX_COLUMN[0] + 1 == self.MAX_COLUMN[1]:
                res = "┬", "┼", "┐", "┤", \
                      "│", \
                      '┼', "┴", "┤", "┘",

            else:
                res = "┬", "┼", "─", "─", \
                      " ", \
                      '┼', "┴", "─", "─",

        self.MAX_COLUMN[0] += 1
        return res

    def __get_char_pile(self):
        """Вернуть символы для создания рамки консоли"""

        res = "┌", "├", "┐", "┤", \
              "│", \
              '├', "└", "┤", "┘",

        self.MAX_COLUMN[0] += 1
        return res


class EditListBox(ListBox):
    """
    Многострочное поле для ввода текста
    """

    __slots__ = [
        "txt"
    ]

    def __init__(self):
        self.txt = Edit(multiline=True, align="left")
        body = SimpleFocusListWalker([self.txt])
        super().__init__(body)

    def keypress(self, size, key):
        """
        Разрешаем только прокручивать текст, но не редок тировать его
        """
        match key:
            case "down":
                super().keypress(size, "down")
            case "up":
                super().keypress(size, "up")


class TextListBox(ListBox):
    __slots__ = [
        "txt"
    ]

    def __init__(self):
        self.txt = Edit(multiline=True, align="left")
        body = SimpleFocusListWalker([self.txt])
        super().__init__(body)


class EditLine(Edit):
    """
    Однострочное поле для ввода текста
    """

    def __init__(self):
        super().__init__(caption="", edit_text="", multiline=False, align="left")


class CommandLine(EditLine):
    """
    Полк для ввода и выполнения команд
    """

    __slots__ = [
        "output_widget",
        "fun_execute_command",
    ]

    def __init__(self, output_widget: Union[Edit, Text],
                 fun_execute_command: Callable[[Union[Edit, Text], str], None], ):
        """
        :param output_widget: У кого виджета он будет брать текст
        :param fun_execute_command: Какую функцию он будет выполнять при нажатие ``Enter``
        """
        self.output_widget: Union[Edit, Text] = output_widget
        self.fun_execute_command: Callable[[Union[Edit, Text], str], None] = fun_execute_command
        super().__init__()

    def keypress(self, size, key):
        """
        Если нажать``Enter``, то возьмется команда из текстового поля
         и вызовет функцию  self.fun_execute_command()

        Если нажать `F5`, то выполнится  функция с аргументов self.fun_execute_command("close")
        """
        match key:
            #: Выполнить команду из текстового поля
            case "enter":
                self.fun_execute_command(self.output_widget, self.get_edit_text())
                # Отчистить консоль команд
                self.set_edit_text('')
            # Выполнить команду с аргументом подразумевающий отчистку консоли
            case "f6":
                self.fun_execute_command(self.output_widget, "close")
        # Пробросить клавишу дальше по стеку вызова
        super().keypress(size, key)


class MenuConsole(LineBox):
    """
    Меню:
        - Консоль
        - Текстовое поле для вывода
    """

    __slots__ = [
        "root",
        "output_menu",
        "command_menu",
        "list_box_menu",
    ]

    def __init__(self, root: ShowLogFileBase):
        self.root: ShowLogFileBase = root
        self.output_menu = Text("", align="left")
        line_menu = Divider("-")
        self.command_menu = CommandLine(output_widget=self.output_menu, fun_execute_command=self.root.ExecuteCommand, )
        body = SimpleFocusListWalker([self.command_menu, line_menu, self.output_menu])
        self.list_box_menu = ListBox(body)
        super().__init__(
            self.list_box_menu,
            title="",
            title_align="center",
            title_attr=None,
            tlcorner=u'┌',
            tline=u'─',
            lline=u'│',
            trcorner=u'┐',
            blcorner=u'└',
            rline=u'│',
            bline=u'─',
            brcorner=u'┘'
        )
