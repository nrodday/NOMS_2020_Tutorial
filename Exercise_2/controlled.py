#!/usr/bin/env python3
from datetime import datetime, timedelta
from bgpReader_util import bgp
from calendar import timegm
from collections import defaultdict
import json


def add_missing_routes(vp_routes):
    for vp in vp_routes:
        p_a = '147.28.240.0/24' 
        p_e = '147.28.241.0/24'

        for timestamp in vp_routes[vp][p_a]:
            if timestamp not in vp_routes[vp][p_e]:
                vp_routes[vp][p_e][timestamp] = 'missing'
    return vp_routes


def get_bgp_data_from_file(filename):   
    vp_routes = defaultdict(lambda: defaultdict(dict))
    all_experiment_prefixes = set()

    all_experiment_prefixes.add('147.28.240.0/24')
    all_experiment_prefixes.add('147.28.241.0/24')

    with open(filename, 'r') as f:
        for line in f:
            if not bgp.is_relevant_line(line, ['\n', '/', '#']): #Filter non BGP-Elements
                continue
            bgp_fields = bgp.get_bgp_fields(line, 'v2') #Parse BGP fields
            if not bgp.is_valid_bgp_entry(bgp_fields): #Filter corrupted BGP-Elements
                continue

            bgp_fields = bgp.get_bgp_fields(line, 'v2')
            peer_asn = bgp_fields.get('peer_asn')
            peer_address = bgp_fields.get('peer_ip')
            vp = (peer_asn, peer_address)
            prefix = bgp_fields.get('prefix')
            as_path = bgp_fields.get('as_path')
            as_path = bgp.remove_prepending_from_as_path(as_path)
            timestamp = int(bgp_fields.get('time'))
            timestamp = timestamp - (timestamp % 3600)

            if prefix in all_experiment_prefixes:
                vp_routes[vp][prefix][timestamp] = as_path

    return vp_routes
