from click import argument, command, option

from logic import ShowLogFile


@command(help='Следить за указанными файлами')
@argument("arr_path", nargs=-1)
@option('time_update', '-t', '--time-update', type=float, default=0.1,
        help="Количество секунд через которое снова будет проверен файл")
def show(arr_path: tuple[str], time_update: float):
    ShowLogFile(arr_path_file=arr_path, time_update=time_update)


if __name__ == '__main__':
    show()
