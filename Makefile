.PHONY: flake8
.PHONY: mypy
#.PHONY: test
.PHONY: yapf

flake8:
	flake8 ./financial/ get_raw_data.py --ignore=E501,W504 && \
    echo 'flake8 check done'

# With venv activated, make sure to run `export MYPYPATH=financial/` first
mypy:
	mypy --namespace-packages --explicit-package-bases --no-incremental get_raw_data.py ./financial/ && \
	echo 'mypy check done'

#test:
#	python3.10 -m unittest discover -s tests
#
yapf:
	yapf --style=pep8 -d --recursive ./financial/ get_raw_data.py  && \
	echo 'yapf check done'
