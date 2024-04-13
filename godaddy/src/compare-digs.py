import argparse
import dns.resolver
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def resolve_nameservers(nameservers):
    resolved_nameservers = []
    for nameserver in nameservers:
        try:
            answers = dns.resolver.resolve(nameserver, 'A')
            ip_address = str(answers[0])
            resolved_nameservers.append(ip_address)
        except dns.resolver.NoAnswer:
            print(f"Warning: Could not resolve IP address for nameserver {nameserver}")
    return resolved_nameservers

def generate_dig_command(record_name, record_type, nameservers, zone_name):
    if not record_name.endswith('.'):
        if record_name == '@':
            record_name = zone_name
        else:
            record_name = f"{record_name}.{zone_name}"
    nameserver_options = ' '.join([f"@{nameserver}" for nameserver in nameservers])
    return f"dig {record_name} {record_type} {nameserver_options}"

def perform_dig(record_name, record_type, nameservers, zone_name, timeout=5):
    if not record_name.endswith('.'):
        if record_name == '@':
            record_name = zone_name
        else:
            record_name = f"{record_name}.{zone_name}"
    resolver = dns.resolver.Resolver()
    resolver.nameservers = nameservers
    try:
        answers = resolver.resolve(record_name, record_type, lifetime=timeout)
        return [str(rdata) for rdata in answers]
    except dns.resolver.NXDOMAIN:
        return None
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.LifetimeTimeout:
        print(f"Record {record_name} ({record_type}) resolution timed out.")
        return []

def process_zone_file(zone_file, route53_nameservers, godaddy_nameservers, dry_run):
    zone_name = os.path.splitext(os.path.basename(zone_file))[0]
    with open(zone_file, 'r') as file:
        lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line.startswith(';') or line.startswith('$') or line == '':
            continue
        parts = line.split()
        if len(parts) >= 4:
            record_name = parts[0]
            record_type = parts[3]
            if not dry_run:
                route53_ip_nameservers = resolve_nameservers(route53_nameservers)
                route53_results = perform_dig(record_name, record_type, route53_ip_nameservers, zone_name)
                godaddy_ip_nameservers = resolve_nameservers(godaddy_nameservers)
                godaddy_results = perform_dig(record_name, record_type, godaddy_ip_nameservers, zone_name)
                if route53_results == godaddy_results:
                    print(f"{record_name} ({record_type}): COMPARE GOOD")
                else:
                    if record_type == 'MX' and set(route53_results) == set(godaddy_results):
                        print(f"{record_name} ({record_type}): MX records compare but different order")
                    else:
                        print(f"{record_name} ({record_type}): DIFFERENCES FOUND")
                        print(f"  Route53 Results: {route53_results}")
                        print(f"  GoDaddy Results: {godaddy_results}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare DNS records between Route53 and GoDaddy')
    parser.add_argument('zone_file', help='Path to the zone file')
    parser.add_argument('--dry-run', action='store_true', help='Print dig commands without executing them')
    args = parser.parse_args()

    route53_nameservers = os.getenv('ROUTE53_NAMESERVERS', '').split(',')
    godaddy_nameservers = os.getenv('GODADDY_NAMESERVERS', '').split(',')

    process_zone_file(args.zone_file, route53_nameservers, godaddy_nameservers, args.dry_run)