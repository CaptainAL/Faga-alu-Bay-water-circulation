# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 18:50:51 2014

@author: Alex
"""


import urllib2
import os
import datetime
from BeautifulSoup import BeautifulSoup
from pandas import DataFrame, to_datetime, date_range
import numpy as np

url = "http://ocnlifeguard.shiftplanning.com/app/reports/shifts-confirmed/%2526sdate%253Daug%252016%252C%25202014%2526edate%253Daug%252030%252C%25202014%2526s%253D-1%2526e%253D-1%2526t%253Dundefined%2526ts%253Dundefined%2526skill%253D-1%2526options%253D-1%2526location%253D-1%2526sortby%253Dundefined%2526remote_site%253Dundefined%2526openshiftoption%253Dundefined%2526%2526min15int%253D%2526include_emp_id%253D-1%2526include_emp_eid%253D-1%2526wu%253Dundefined%2526exclude_disabled_emp%253D-1%2526split_overtime_by_rate%253Dundefined/"


page = urllib2.urlopen(url)
soup = BeautifulSoup(page)
soupsplit = str(soup.tagStack).split('\n')