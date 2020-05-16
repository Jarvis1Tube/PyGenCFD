-include Makefile.local

generate:
	@echo "RUN GEN"
	@mkdir -p gen
	@echo "" > gen/__init__.py
	@pyuic5 ui.ui -o gen/UI.py
	@echo "GENERATED SUCCESSFUL"