import dns.resolver

def perform_dig(record_name, record_type, nameservers):
    resolver = dns.resolver.Resolver()
    
    # Convert nameserver domain names to IP addresses
    ip_nameservers = []
    for nameserver in nameservers:
        try:
            ip_address = dns.resolver.resolve(nameserver, 'A')[0].to_text()
            ip_nameservers.append(ip_address)
        except dns.resolver.NXDOMAIN:
            print(f"Nameserver {nameserver} does not have an A record.")
    
    resolver.nameservers = ip_nameservers
    
    try:
        answers = resolver.resolve(record_name, record_type)
        return [str(rdata) for rdata in answers]
    except dns.resolver.NXDOMAIN:
        return None
    except dns.resolver.NoAnswer:
        return []


def compare_dns_records(zone_file, route53_nameservers, godaddy_nameservers):
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

            route53_results = perform_dig(
                record_name, record_type, route53_nameservers)
            godaddy_results = perform_dig(
                record_name, record_type, godaddy_nameservers)

            print(f"Record: {record_name} ({record_type})")
            print(f"Route53 Results: {route53_results}")
            print(f"GoDaddy Results: {godaddy_results}")

            if route53_results is not None and godaddy_results is not None:
                if sorted(route53_results) == sorted(godaddy_results):
                    print("Results match!")
                else:
                    print("Results do not match!")
            else:
                print("Results do not match!")

            print('---')


route53_nameservers = ['ns-1115.awsdns-11.org',
                       'ns-1819.awsdns-35.co.uk',
                       'ns-78.awsdns-09.com',
                       'ns-671.awsdns-19.net']

godaddy_nameservers = ['ns01.domaincontrol.com', 'ns02.domaincontrol.com']

compare_dns_records('annarborfsc.org.txt',
                    route53_nameservers, godaddy_nameservers)
