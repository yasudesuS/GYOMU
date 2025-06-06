#!/home/xs332906/anaconda3/bin/python
# encoding: utf-8

import sys, os

sys.path.append("/home/xs332906/xs332906.xsrv.jp/public_html/flow/")

os.environ['DJANGO_SETTINGS_MODULE'] = "flow.settings"

from wsgiref.handlers import CGIHandler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
CGIHandler().run(application)