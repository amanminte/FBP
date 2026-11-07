import requests
import re
import json

url = 'https://understat.com/league/EPL/2024'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

try:
    r = requests.get(url, headers=headers, timeout=10)
    print('Understat Status code:', r.status_code)
    m = re.search(r"datesData\s*=\s*JSON\.parse\('([^']+)'\)", r.text)
    if m:
        raw_data = m.group(1).encode('utf-8').decode('unicode_escape')
        matches = json.loads(raw_data)
        print('Successfully found matches:', len(matches))
        print('Sample match:', matches[0])
    else:
        print('datesData not found in HTML')
except Exception as e:
    print('Error:', e)
