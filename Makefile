test-quick:
	env SKIP_MIGRATIONS=1 ./manage.py test -s --nologcapture
test:
	./manage.py test -s --nologcapture
flake:
	flake8 --exclude migrations dnsaas/ powerdns/
