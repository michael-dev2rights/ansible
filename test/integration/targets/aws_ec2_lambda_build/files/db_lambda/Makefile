SHELL := /bin/bash

package:
	rm -f db_lambda.zip
	rm -rf lambda_venv
	mkdir -p build
	cp db_lambda.py build
	chmod 755 build/db_lambda.py
	python3 -m venv lambda_venv
	set -vx  ; \
		source lambda_venv/bin/activate ; \
		python lambda_venv/bin/pip install --upgrade pip ; \
		python lambda_venv/bin/pip install --requirement lambda-requirements.txt
	set -vx  ; \
		cd lambda_venv/lib/python3.*/site-packages ; \
		zip -q -r9 ../../../../db_lambda.zip *
	set -vx ;\
		cd build ;\
		zip -q -r9 ../db_lambda.zip *
	ls -l db_lambda.zip
	unzip -l db_lambda.zip

.PHONY: package
