#!/usr/bin/env python3

import argparse
import sys
import os
import logging
import ipaddress
import time
import re

import requests
from illumio import *


def ip_in_networks(ip, networks):
    for network in networks:
        logging.debug("IP: %s Network: %s", ip, network)
        if ip in network:
            return True
    return False


def create_workload(pce, ip, simulate):
    logging.debug("Creating workload for IP %s", ip)
    if simulate:
        logging.info("Simulating workload creation for IP %s", ip)
        return None
    logging.info("Creating workload on PCE %s", ip)
    workload = Workload(
        name=f"FlowLink-{ip}",
        interfaces=[
            Interface(name='flowlink0', address=str(ip), link_state='up')
        ]
    )
    workload = pce.workloads.create(workload)
    logging.info("Workload created: %s - %s - %s", workload.href, workload.name, ip)
    return workload


def find_internal_ips(pce, log_file_path, internal_networks, simulate, notail, max_workloads):
    internal_networks = [ipaddress.ip_network(network) for network in internal_networks]
    logging.debug("Internal Networks: %s", internal_networks)

    with open(log_file_path, 'r') as file:
        logging.info("Reading file: %s", log_file_path)
        logging.info("Notail: %s", notail)
        if not notail:
            file.seek(0, 2)  # Move to the end of the file

        while True:
            line = file.readline().rstrip()
            if line == "":
                logging.debug("No new content in file, sleeping 10s.")
                time.sleep(10)
                continue

            if "Following new IP addresses found in flows:" not in line:
                logging.debug("Line does not contain IP addresses")
                continue

            workloads_created = 0
            ip_addresses = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
            for ip_address in ip_addresses:
                try:
                    ip = ipaddress.ip_address(ip_address)
                except ValueError:
                    continue

                logging.debug("IP: %s", ip)
                if not ip_in_networks(ip, internal_networks):
                    logging.debug("IP %s is not in internal networks", ip)
                    continue

                if max_workloads != 0 and workloads_created >= max_workloads:
                    logging.info("Max workloads (%d) created.", max_workloads)
                    break

                logging.debug("Checking if IP is a workload on PCE")
                workload = pce.workloads.get(params={'ip_address': str(ip)})
                workloads_created += 1
                if workload:
                    logging.debug("Workload for IP %s already exists on PCE", ip)
                else:
                    logging.info("Internal IP %s is not a workload on PCE", ip)
                    create_workload(pce, ip, simulate)


def parse_arguments():
    parser = argparse.ArgumentParser(description='FlowLink Unmanaged Workload Maker')
    parser.add_argument('--pce_host', default=os.environ.get('PCE_HOST', 'poc1.illum.io'), help='Hostname of the PCE')
    parser.add_argument('--pce_port', type=int, default=int(os.environ.get('PCE_PORT', 443)), help='TCP port for the PCE connection')
    parser.add_argument('--org_id', type=int, default=int(os.environ.get('PCE_ORG', 1)), help='Organization ID for the PCE')
    parser.add_argument('--api_user', default=os.environ.get('PCE_API_USER'), help='API user or service account')
    parser.add_argument('--api_key', default=os.environ.get('PCE_API_KEY'), help='API key or secret')
    parser.add_argument('--verbose', action='store_true', help='Enable debug-level logging')
    parser.add_argument('--networks', default='192.168.0.0/16,172.16.0.0/12,10.0.0.0/8', help='Company networks listed comma separated')
    parser.add_argument('--log_file', help='Path to the FlowLink log file')
    parser.add_argument('--simulate', action='store_true', help='Simulate the workload creation')
    parser.add_argument('--notail', action='store_true', help='Read log file from the beginning instead of tailing')
    parser.add_argument('--max-workloads', type=int, default=0, help='Maximum number of workloads to create per batch, 0 means unlimited')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not args.pce_host:
        sys.exit("PCE Host (--pce_host or environment variable PCE_HOST) is required")

    if not args.api_user:
        sys.exit("API User (--api_user or environment variable PCE_API_USER) is required")

    if not args.api_key:
        sys.exit("API Key (--api_key or environment variable PCE_API_KEY) is required")

    if not args.log_file:
        sys.exit("Log file (--log_file) is required")

    if not os.path.isfile(args.log_file):
        sys.exit(f"Log file not found: {args.log_file}")

    logging.debug("PCE Host: %s", args.pce_host)
    logging.debug("PCE Port: %s", args.pce_port)
    logging.debug("Organization ID: %s", args.org_id)
    logging.debug("Username: %s", args.api_user)

    pce = PolicyComputeEngine(args.pce_host, port=args.pce_port, org_id=args.org_id)
    pce.set_credentials(args.api_user, args.api_key)
    if pce.check_connection():
        logging.info("Connected to Illumio PCE API on %s:%s", args.pce_host, args.pce_port)
    else:
        logging.error("Connection failed to: %s:%s", args.pce_host, args.pce_port)
        sys.exit(1)

    networks = args.networks.split(',')

    try:
        find_internal_ips(pce, args.log_file, networks, args.simulate, args.notail, args.max_workloads)
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully.")
        sys.exit(0)
