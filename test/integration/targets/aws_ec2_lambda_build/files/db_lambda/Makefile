SHELL := /bin/bash

# package is designed to be run on an EC2 instance with software
# corresponding to the lambda environment and will build the full
# lambda package

package:
	rm -f db_lambda.zip
	rm -rf lambda_venv
	mkdir -p build
	cp db_lambda.py build
	chmod 755 build/db_lambda.py
	python3 -m virtualenv lambda_venv
	set -vx  ; \
		source lambda_venv/bin/activate ; \
		python lambda_venv/bin/pip install --upgrade pip ; \
		python lambda_venv/bin/pip install --requirement lambda-requirements.txt
	set -vx  ; \
		cd lambda_venv/lib/python3.*/site-packages ; \
		zip -q -r9 ../../../../db_lambda.zip *
		cd lambda_venv/lib64/python3.*/site-packages ; \
		zip -q -r9 ../../../../db_lambda.zip *
	set -vx ; \
		cd build ;\
		zip -q -r9 ../db_lambda.zip *
	ls -l db_lambda.zip
	unzip -l db_lambda.zip

# shortcut just updates
shortcut:
	zip -f db_lambda.zip db_lambda.py


.PHONY: package
