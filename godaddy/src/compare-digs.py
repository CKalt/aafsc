import argparse
import dns.resolver
import os


def generate_dig_command(record_name, record_type, nameservers):
    nameserver_options = ' '.join([f"@{nameserver}" for nameserver in nameservers])
    return f"dig {record_name} {record_type} {nameserver_options}"

def perform_dig(record_name, record_type, nameservers, timeout=5):
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

            route53_dig_command = generate_dig_command(record_name, record_type, route53_nameservers)
            godaddy_dig_command = generate_dig_command(record_name, record_type, godaddy_nameservers)

            print(f"Record: {record_name} ({record_type})")
            print(f"Route53 Dig Command: {route53_dig_command}")
            print(f"GoDaddy Dig Command: {godaddy_dig_command}")

            if not dry_run:
                print("Route53 Results:")
                os.system(route53_dig_command)
                print("GoDaddy Results:")
                os.system(godaddy_dig_command)

            print('---')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare DNS records between Route53 and GoDaddy')
    parser.add_argument('zone_file', help='Path to the zone file')
    parser.add_argument('--dry-run', action='store_true', help='Print dig commands without executing them')
    args = parser.parse_args()

    route53_nameservers = ['ns-1307.awsdns-35.org', 'ns-1848.awsdns-39.co.uk', 'ns-812.awsdns-37.net', 'ns-282.awsdns-35.com']
    godaddy_nameservers = ['ns01.domaincontrol.com', 'ns02.domaincontrol.com']

    process_zone_file(args.zone_file, route53_nameservers, godaddy_nameservers, args.dry_run)
