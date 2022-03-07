from os import system
from select import poll
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep
from typing import Union

from urwid import MainLoop, Overlay, Edit, Text

from base_template import ShowLogFileBase
from widget import ConsolesPile, LogObj, MenuConsole


class ShowLogFile(ShowLogFileBase):
    """
    Класс для отображения лог файлов в реальном времянки
    """

    def __init__(self, arr_path_file: tuple[str], time_update: float = 0.1):
        """
        :param arr_path_file: Список файлов
        """
        #: Через сколько обновлять данные ищ файла
        self.time_update = time_update
        #: Список объектов для консолей
        self.arr_console_log: tuple[LogObj] = tuple(LogObj(_index, _path)
                                                    for _index, _path in enumerate(arr_path_file))

        #: Инициализируем все консоли
        self.console_columns: ConsolesPile = ConsolesPile(
            title_names=self.arr_console_log,
            root=self
        )
        #: Скрывающееся меню для команд и информации
        self.menu = MenuConsole(root=self)
        #: Инициализируем всплывающие окно с информацией
        self.gInfoOverlay: Overlay = Overlay(
            self.menu,
            self.console_columns,
            align="center",
            valign="middle",
            width=("relative", 60),
            height=("relative", 60),
        )
        #: Инициализируем главный цикл
        self.loop = MainLoop(
            self.console_columns,
            palette=self.palette
        )
        # Обновляем отрисовку консоли
        self.loop.set_alarm_in(0.1, self.console_columns.update_widget)
        #: Запускаем циклы события
        self.run()

    def run(self):
        """
        Запустить циклы события
        """
        try:
            super().__init__()
            self.loop_thread_tail_file()
            self.loop.run()
        except KeyboardInterrupt:
            print("Exit")
            system("clear")
            exit()

    def ExecuteCommand(self, output_widget: Union[Edit, Text], command: str):
        """
        Глобальная консоль ввода:
        - `close` = Скрыть меню
        - `help` = Подсказка
        """
        match command.split()[0]:
            case 'close':
                self.loop.widget = self.console_columns
            case "help":
                output_widget.set_text(f"{ConsolesPile.keypress.__doc__}\n{self.ExecuteCommand.__doc__}")

    def loop_thread_tail_file(self):
        """
        Запускам tail для всех файлов в отдельных потоках
        """

        def _tail(console_log: LogObj):
            """
            Получаем данные из конца файла

            :param console_log:
            """

            f = Popen(['tail', '-F', console_log.name], stdout=PIPE, stderr=PIPE)
            p = poll()
            p.register(f.stdout)

            while True:
                if p.poll(1) and console_log.pause is not True:
                    self.console_columns.SendTextInIndex(console_log.index, f.stdout.readline())
                sleep(self.time_update)
                # TEST SEND KYE PRESS
                # self.console_columns.keypress(1, 1)

        for _console in self.arr_console_log:
            Thread(target=_tail, args=(_console,), daemon=True).start()


if __name__ == '__main__':
    ShowLogFile(arr_path_file=tuple(['/home/denis/prog/data_test/test.log',
                                     '/home/denis/prog/data_test/test1.log',
                                     '/home/denis/prog/data_test/test2.log',
                                     '/home/denis/prog/data_test/test3.log']))
