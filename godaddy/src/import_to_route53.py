import boto3
import re
import logging
from dotenv import load_dotenv
import os
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
# Get the hosted zone ID from environment variables
HOSTED_ZONE_ID = os.getenv('HOSTED_ZONE_ID')

# Initialize the Route53 client using default credentials
session = boto3.Session(profile_name='aafsc-admin')
route53_client = session.client('route53')


def parse_zone_file(file_content, zone_name):
    records = []
    lines = file_content.split('\n')
    in_soa_record = False

    for line_number, line in enumerate(lines, 1):
        line = line.strip()
        if 'SOA' in line:
            in_soa_record = True
        if line.startswith(')'):
            in_soa_record = False
            continue
        if line and not line.startswith(';') and not line.startswith('$') and not in_soa_record:
            parts = re.split(r'\s+', line)
            if len(parts) < 5:
                logging.warning(f"Skipping line {line_number}: insufficient parts - {line}")
                continue
            record_type = parts[3]
            record_name = parts[0] if parts[0] != '@' else ''
            # Ensure correct domain concatenation for subdomains
            full_record_name = f"{record_name}.{zone_name}." if record_name else f"{zone_name}."
            records.append({
                'Name': full_record_name,
                'TTL': parts[1],
                'Type': record_type,
                'Value': ' '.join(parts[4:])
            })
    return records

def format_resource_records(record):
    if record['Type'] == 'TXT':
        # Ensure correct quotation of TXT record values
        cleaned_value = record['Value'].replace('"', '')  # Remove existing quotes
        return [{'Value': f'"{cleaned_value}"'}]  # Add quotes around the value
    elif record['Type'] == 'MX':
        return [{'Value': record['Value']}]
    else:
        return [{'Value': record['Value']}]



def submit_changes_to_route53(records):
    changes = []
    for record in records:
        formatted_record = format_resource_records(record)
        print("Formatted record:", formatted_record)  # Logging the formatted record for verification
        changes.append({
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': record['Name'],
                'Type': record['Type'],
                'TTL': int(record['TTL']),
                'ResourceRecords': formatted_record
            }
        })

    try:
        response = route53_client.change_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            ChangeBatch={
                'Comment': 'Automated DNS update from BIND format',
                'Changes': changes
            }
        )
        return response
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return None


def main():
    file_path = 'annarborfsc.org.txt'
    zone_name = 'example-test.com'  # Define the zone name you're working with
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return

    # Pass the zone name as a second argument to parse_zone_file
    parsed_records = parse_zone_file(file_content, zone_name)
    if not parsed_records:
        logging.warning("No records parsed, nothing to update.")
        return

    response = submit_changes_to_route53(parsed_records)
    print(response)



if __name__ == "__main__":
    main()
