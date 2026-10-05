PREFIX ?= /usr

.PHONY: all html test serve clean

all html:
	python3 build.py build/html

test:
	python3 tests/check.py

serve: html
	python3 -m http.server --directory build/html 8080

clean:
	rm -rf build
