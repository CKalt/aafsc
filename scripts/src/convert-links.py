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

# Compile a regular expression pattern for finding URLs to rewrite in various attributes
# This pattern is more inclusive and attempts to capture URLs in common attributes like href, src, srcset, and data-*
url_pattern = re.compile(
    r'(\b(href|src|srcset|action|data-[^=]+)=["\'])(http[s]?)://(' + '|'.join(re.escape(domain) for domain in domains_to_rewrite) + ')(/[^"\']*)["\']',
    re.IGNORECASE
)

def rewrite_url(match):
    prefix, attribute, protocol, domain, path = match.groups()
    # Adjust the replacement pattern according to your needs
    # Now handles multiple attributes by reconstructing the attribute assignment
    return f'{prefix}../{domain}{path}"'

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
                print(f'Processing file: {file_path}')
                process_file(file_path)

if __name__ == "__main__":
    main()
