name_bin_file = "showlogsmal.bin"
proj_name = "showlogsmal"

# Генерировать документацию
auto_doc:
	sphinx-autobuild -b html ./docs/source ./docs/build/html

# Создать файл зависимостей для Read The Docs
req_doc:
	poetry export -f requirements.txt --output ./docs/requirements.txt --dev --without-hashes;

# Скомпилировать проект
compile:
	python -m nuitka --follow-imports $(proj_name)/main.py -o $(name_bin_file)

debug:
	python -m nuitka --follow-imports $(proj_name)/main.py -o $(name_bin_file) --remove-output

init:
	pip install poetry && poetry install && mkdir docs && sphinx-quickstart -p "showlogsmal" -a "Denis Kustov <denis-kustov@rambler.ru>" -v "0.0.1" -l "ru"  -r "0.0.1" --sep

