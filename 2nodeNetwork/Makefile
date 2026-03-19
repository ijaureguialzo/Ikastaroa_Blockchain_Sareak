#!make

help: _header
	${info }
	@echo Opciones:
	@echo -----------------------
	@echo test-conectividad
	@echo despliegue
	@echo -----------------------

_header:
	@echo -----------------------
	@echo Blockchain 2nodeNetwork
	@echo -----------------------

test-conectividad:
	@ansible -i inventory.yml -m ping all --ask-pass

despliegue:
	@ansible-playbook -i inventory.yml hedapena-AnsiblePlaybook.yml --ask-become-pass
