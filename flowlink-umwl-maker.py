#!/usr/bin/env python3

import argparse
import sys
import os
import json
import argparse
import uuid
import logging
import requests
import json
import socket
import sys
import ipaddress
import time
import select

from illumio import *

# include regular expression module
import re

def ip_in_networks(ip, networks):
    for network in networks:
        print("IP: " + str(ip) + " Network: " + str(network))
        if ip in network:
            return True
    return False

def create_workload(pce, ip, simulate):
    logging.debug(f"Creating workload for IP {ip}")
    if not simulate:
        logging.info(f"Creating workload on PCE {ip}")
        workload = Workload(
            name=f"FlowLink-{str(ip)}", 
            interfaces=[ 
                Interface( name='flowlink0', address=str(ip), link_state='up')
            ]
        )
        workload = pce.workloads.create(workload)
        logging.info(f"Workload created: {workload.href} - {workload.name} - {ip}")
        return workload
    else:
        logging.info(f"Simulating workload creation for IP {ip}")
        return None

def find_internal_ips(log_file_path, internal_networks):
    internal_networks = [ipaddress.ip_network(network) for network in internal_networks]
    logging.debug("Internal Networks: " + str(internal_networks))

    # keep log file open and wait for new lines to appear
    with open(log_file_path, 'r') as file:
        logging.info("Reading file: {}".format(log_file_path))
        logging.info("Notail: {}".format(notail))
        if notail == False:
            file.seek(0, 2)  # Move to the end of the file

        while True:
            # be sure that the line matches : 
            # 2024-03-30T19:29:18.027820424Z 2024-03-30T19:29:18.027524+00:00 ***** Following new IP addresses found in flows: [170.72.41.92 184.185.103.69 23.218.217.180 82.64.102.158 217.20.50.39 193.122.61.43] 

            line = file.readline().rstrip() 
            if line == "":
                logging.debug("No new content in file, sleeping 10s.")
                time.sleep(10)
                continue

            if "Following new IP addresses found in flows:" in line:
                workloads_created = 0
                ip_addresses = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
                for ip_address in ip_addresses:
                    try:
                        ip = ipaddress.ip_address(ip_address)
                        logging.debug("IP: " + str(ip))
                        if ip_in_networks(ip, internal_networks):
                            # exit loop when workloads_created is equal to max_workloads
                            if max_workloads != 0 and workloads_created >= max_workloads:
                                logging.info(f"Max workloads ({max_workloads}) created.")
                                break
                            # check if this is a workload on PCE
                            logging.debug("Checking if IP is a workload on PCE")
                            workload = pce.workloads.get(params={'ip_address': str(ip)})
                            workloads_created += 1
                            if not workload:
                                logging.info(f"Internal IP {ip} is not a workload on PCE")
                                # create workload on PCE with a flowlink related name
                                workload = create_workload(pce, ip, simulate)
                            else:
                                logging.debug(f"Workload for IP {ip} already exists on PCE")   
                        else:
                            logging.debug("IP {} is not in internal networks".format(str(ip)))
                    except ValueError:
                        # Ignore IP addresses that are not valid
                        continue
            else:
                logging.debug("Line does not contain IP addresses")

def parse_arguments():
    parser = argparse.ArgumentParser(description='PCE Demo Host Credentials')
    parser.add_argument('--pce_host', default=os.environ.get('PCE_HOST', 'poc1.illum.io'), help='Integer for the PCE demo host')
    parser.add_argument('--pce_port', default=os.environ.get('PCE_PORT', 443), help='TCP port for the PCE connection')
    parser.add_argument('--org_id', default=os.environ.get('PCE_ORG', 1), help='Organization ID for the PCE')
    parser.add_argument('--api_user', default=os.environ.get('PCE_API_USER'), help='Optional username (default: demo@illumio.com)')
    parser.add_argument('--api_key', default=os.environ.get('PCE_API_KEY'), help='Optional password (default: password)')
    parser.add_argument('--verbose', help='Be more verbose (logging)')
    parser.add_argument('--networks', default='192.168.0.0/16,172.16.0.0/12,10.0.0.0/8', help = 'Company networks listed comma separated')
    parser.add_argument('--log_file', help = 'Path to the log file')
    parser.add_argument('--simulate', action='store_true', help = 'Simulate the workload creation', default=False)
    parser.add_argument('--notail', action='store_true', help = 'Do not tail the log file')
    parser.add_argument('--max-workloads', help = 'Maximum number of workloads to create per run, 0 means unlimited', default=0)
    return parser.parse_args()


if __name__ == "__main__":
    # Parsing the arguments
    args = parse_arguments()

    # Accessing the values
    pce_host = args.pce_host
    pce_port = args.pce_port
    org_id = args.org_id
    username = args.api_user
    password = args.api_key
    verbose = args.verbose
    networks_string = args.networks
    simulate = args.simulate
    notail = args.notail
    max_workloads = args.max_workloads

    if not pce_host:
        exit("PCE Host (--pce_host or environemnt variable PCE_HOST) is required")

    if not username:
        exit("API User (--api_user or environment variable PCE_API_USER) is required")

    if not password:
        exit("API Key (--api_key or environment variable PCE_API_KEY) is required")

    if verbose:
        print("Verbose logging enabled")
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


    # Printing the values
    logging.debug(f"PCE Host: {pce_host}")
    logging.debug(f"PCE Port: {pce_port}")
    logging.debug(f"Organization ID: {org_id}")
    logging.debug(f"Username: {username}")
    pce = PolicyComputeEngine(pce_host, port=pce_port, org_id=org_id)
    pce.set_credentials(username, password)
    if pce.check_connection():
        logging.info("Connected to Illumio PCE API on {}:{}".format(pce_host, pce_port))
    else:
        logging.info("Connection failed to: {}:{}".format(pce_host, pce_port))
        exit(1)

    # split networks in a array
    networks = networks_string.split(',')

    # watch a file on disk and check for a comma separated list of IP addresses
    logging.debug("calling find_internal_ips")
    find_internal_ips(args.log_file, networks)  # args.log_file is the path to the log file
