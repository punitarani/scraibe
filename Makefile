# Makefile

# OS specific commands and variables
ifeq ($(OS),Windows_NT)
    SET_ENV = set
else
    SET_ENV = export
endif


format:
	black *.py
	black data/
	black scraibe/
