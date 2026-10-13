"""Cache publisher-deposited bibliographic metadata from Crossref."""
from pathlib import Path
import json, requests, sys
from concurrent.futures import ThreadPoolExecutor

DOIS = ['10.1007/s10877-019-00382-0','10.1080/03091902.2016.1213902',
        '10.3390/s21217246','10.3390/s24051525','10.1109/JSEN.2026.3726629',
        '10.1038/s41597-025-05781-4','10.1371/journal.pone.0138921',
        '10.1093/oxfordjournals.eurheartj.a014868','10.1109/TBME.2015.2475278',
        '10.1109/ACCESS.2019.2911555']
def fetch(doi):
    r=requests.get('https://api.crossref.org/works/'+doi,timeout=45)
    r.raise_for_status()
    m=r.json()['message']
    return doi,{k:m.get(k) for k in ['DOI','title','author','container-title','volume','issue','page','article-number','published','published-print','published-online','URL']}
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    data=dict(ThreadPoolExecutor(max_workers=5).map(fetch,DOIS))
    Path(__file__).with_name('reference_metadata.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    for doi,m in data.items():
        print(doi,m['title'],m['author'][0] if m['author'] else '',m['volume'],m['page'],m['published'])
