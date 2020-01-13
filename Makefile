.PHONY: clean build

clean:
	rm -rf build
	rm -rf dist

build:
	pyinstaller -F -n "do" --hidden-import=do.utils entrypoint.py
	cp examples/basic.py dist/tasks.py
