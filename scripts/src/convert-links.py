import os
import re

# Define the list of domains you want to rewrite URLs for
domains_to_rewrite = [
    'www.annarborfsc.org',
    'aafsc.blob.core.windows.net',
    'figureskating.blob.core.windows.net',
    'files.constantcontact.com',
    'imgssl.constantcontact.com',
]

# Compile a regular expression pattern for finding URLs to rewrite
url_pattern = re.compile(
    r'href="(https?)://(' + '|'.join(re.escape(domain) for domain in domains_to_rewrite) + ')(/[^"]*)"'
)

def rewrite_url(match):
    protocol, domain, path = match.groups()
    # Adjust the replacement pattern according to your needs
    return 'href="../' + domain + path + '"'

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace URLs in the content
    updated_content = url_pattern.sub(rewrite_url, content)
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

def main():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.html') or file.endswith('.aspx'):
                file_path = os.path.join(root, file)
                print(f'Processing {file_path}')
                process_file(file_path)

if __name__ == "__main__":
    main()
