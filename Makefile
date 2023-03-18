.PHONY: flake8
.PHONY: mypy
.PHONY: test
.PHONY: yapf
.PHONY: pycodestyle

flake8:
	flake8 ./financial/ get_raw_data.py --ignore=E501,W504 && \
    echo 'flake8 check done'

mypy:
	mypy --explicit-package-bases --no-incremental get_raw_data.py ./financial/ && \
	echo 'mypy check done'

test:
	python3.10 -m unittest discover -s tests

yapf:
	yapf --style=pep8 -d --recursive ./financial/ get_raw_data.py  && \
	echo 'yapf check done'

pycodestyle:
	pycodestyle ./financial/ get_raw_data.py
	echo 'pycodestyle check done'