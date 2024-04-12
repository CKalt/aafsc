import boto3
import re
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
HOSTED_ZONE_ID = 'xxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your actual Route 53 hosted zone ID

# Initialize the Route53 client using default credentials
route53_client = boto3.client('route53')

def parse_zone_file(file_content):
    records = []
    lines = file_content.split('\n')
    for line_number, line in enumerate(lines, 1):  # Added line number for better debugging
        line = line.strip()
        if line and not line.startswith(';') and not line.startswith('$'):
            parts = re.split(r'\s+', line)
            if len(parts) < 5:  # Check if parts have less than the expected number of elements
                logging.warning(f"Skipping line {line_number}: insufficient parts - {line}")
                continue
            record_type = parts[3]
            name = f"{parts[0]}annarborfsc.org." if parts[0] == '@' else parts[0]
            records.append({
                'Name': name,
                'TTL': parts[1],
                'Type': record_type,
                'Value': ' '.join(parts[4:])
            })
    return records

def format_resource_records(record):
    if record['Type'] in ['A', 'NS', 'CNAME', 'SOA']:
        return [{'Value': record['Value']}]
    elif record['Type'] == 'MX':
        priority, value = record['Value'].split(' ')
        return [{'Value': f"{priority} {value}"}]
    elif record['Type'] == 'TXT':
        return [{'Value': record['Value']}]

def submit_changes_to_route53(records):
    changes = []
    for record in records:
        changes.append({
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': record['Name'],
                'Type': record['Type'],
                'TTL': int(record['TTL']),
                'ResourceRecords': format_resource_records(record)
            }
        })

    response = route53_client.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch={
            'Comment': 'Automated DNS update from BIND format',
            'Changes': changes
        }
    )
    return response

def main():
    file_path = 'annarborfsc.org.txt'  # Ensure this is the correct path
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return

    parsed_records = parse_zone_file(file_content)
    if not parsed_records:
        logging.warning("No records parsed, nothing to update.")
        return

    response = submit_changes_to_route53(parsed_records)
    print(response)

if __name__ == "__main__":
    main()
