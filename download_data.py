"""Download the versioned open SensSmartTech WFDB release with SHA256 validation."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests, re, hashlib, json, time, threading

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'data' / 'senssmarttech'
BASE = 'https://physionet-open.s3.amazonaws.com/senssmarttech/1.0.0/'
LOCAL = threading.local()

def fetch(name):
    if not hasattr(LOCAL, 'session'): LOCAL.session = requests.Session()
    path = DEST / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        for attempt in range(5):
            try:
                r = LOCAL.session.get(BASE + name, timeout=120)
                r.raise_for_status()
                path.write_bytes(r.content)
                break
            except requests.RequestException:
                if attempt == 4: raise
                time.sleep(2 ** attempt)
    return name, hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for name in ['Demographics.csv', 'LICENSE.txt', 'README.txt', 'RECORDS', 'SHA256SUMS.txt']:
        fetch(name)
    hashes = {}
    for line in (DEST / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        hashes[name.strip().lstrip('*').removeprefix('./')] = digest
    names = sorted(n.removeprefix('WFDB/') for n in hashes if n.startswith('WFDB/') and n.endswith(('.hea','.dat')))
    manifest = []
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(fetch, 'WFDB/' + n) for n in names]
        for i, f in enumerate(as_completed(futures), 1):
            name, digest, size = f.result()
            expected = hashes.get(name)
            if expected is None or digest != expected:
                raise RuntimeError('Missing or mismatched upstream checksum: ' + name)
            manifest.append(dict(file=name, sha256=digest, bytes=size, verified=True))
            if i % 100 == 0: print(f'{i}/{len(names)} files verified', flush=True)
    (DEST / 'manifest.json').write_text(json.dumps(sorted(manifest, key=lambda x:x['file']), indent=2))
    print(f'COMPLETE: {len(manifest)} verified files; {sum(x["bytes"] for x in manifest)/1e6:.1f} MB', flush=True)

if __name__ == '__main__': main()
