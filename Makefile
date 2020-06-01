-include Makefile.local

generate:
	@echo "RUN GEN"
	@mkdir -p src/generated
	@echo "" > src/generated/__init__.py
	@pyuic5 ./src/ui.ui -o src/generated/UI.py
	@echo "GENERATED SUCCESSFUL"

run:
	@make generate
	python3 ./src/start_ui.py