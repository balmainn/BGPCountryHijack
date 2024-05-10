#!/bin/bash
peer-stats-single-file http://archive.routeviews.org/route-views.sg/bgpdata/2022.02/RIBS/rib.20220205.1800.bz2|python3 test-read-js.py
