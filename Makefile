-include Makefile.local

generate:
	@echo "RUN GEN"
	@mkdir -p src/gen
	@echo "" > src/gen/__init__.py
	@pyuic5 ./src/ui.ui -o src/gen/UI.py
	@echo "GENERATED SUCCESSFUL"