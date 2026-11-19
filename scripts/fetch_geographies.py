"""Download actual Census boundaries; never infer a Northern California polygon.

Run from the package root: python scripts/fetch_geographies.py
Uses only Python standard library. Leaves existing output untouched on failure.
"""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://tigerweb.geo.census.gov/arcgis/rest/services/Generalized_ACS2024/State_County/MapServer'
STATES = {'02': 'US-AK', '06': 'US-CA', '16': 'US-ID', '30': 'US-MT', '41': 'US-OR', '53': 'US-WA', '56': 'US-WY'}
BAY = {'06001', '06013', '06041', '06055', '06075', '06081', '06085', '06095', '06097'}

def get(layer, where):
    query = urllib.parse.urlencode(dict(where=where, outFields='GEOID,STATE,NAME',
        returnGeometry='true', outSR=4326, geometryPrecision=5, f='geojson'))
    url = f'{BASE}/{layer}/query?{query}'
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'K-Seattle research prototype/1.0', 'Accept': 'application/geo+json,application/json'})
            with urllib.request.urlopen(req, timeout=40) as response:
                raw = response.read(30_000_000)
            payload = json.loads(raw)
            if payload.get('error') or payload.get('type') != 'FeatureCollection':
                raise ValueError('Census returned an error or non-GeoJSON payload')
            if payload.get('exceededTransferLimit'):
                raise ValueError('Census result is truncated')
            return url, raw, payload['features']
        except Exception as exc:
            error = exc
            if attempt < 2:
                time.sleep(1 + attempt)
    raise RuntimeError(f'Census boundary fetch failed: {error}')

def main():
    state_sql = 'STATE IN (' + ','.join("'"+s+"'" for s in STATES) + ')'
    county_sql = 'GEOID IN (' + ','.join("'"+s+"'" for s in sorted(BAY)) + ')'
    state_url, state_raw, states = get(9, state_sql)
    county_url, county_raw, counties = get(13, county_sql)
    if {str(f['properties']['STATE']).zfill(2) for f in states} != set(STATES):
        raise ValueError('Expected exactly seven state boundaries')
    if {str(f['properties']['GEOID']).zfill(5) for f in counties} != BAY:
        raise ValueError('Expected exactly nine Bay Area county boundaries')
    if any(not f.get('geometry') for f in states + counties):
        raise ValueError('Missing geometry in source response')
    features = []
    for feature in states + counties:
        props = feature['properties']
        geoid = str(props['GEOID'])
        rid = STATES[str(props['STATE']).zfill(2)] if feature in states else 'US-CA-' + geoid.zfill(5)
        features.append({'type':'Feature','id':rid,'properties':{'feature_id':rid,
            'region_id':rid,'name':props['NAME'],'source_ref':'SRC-GEO-002',
            'boundary_version':'2024-01-01','crs':'EPSG:4326',
            'geometry_basis':'Census generalized 1:20,000,000 boundary'},'geometry':feature['geometry']})
    # This is an exact collection of constituent county polygons, not a fabricated hull.
    features.append({'type':'Feature','id':'US-CA-BAY9','properties':{
        'feature_id':'US-CA-BAY9','region_id':'US-CA-BAY9','name':'Bay Area 9 counties',
        'source_ref':'SRC-GEO-002','membership_source_ref':'SRC-GEO-003','boundary_version':'2024-01-01',
        'crs':'EPSG:4326','geometry_basis':'GeometryCollection of nine constituent counties; not dissolved'},
        'geometry':{'type':'GeometryCollection','geometries':[f['geometry'] for f in counties]}})
    target=ROOT/'source_documents/geography'
    target.mkdir(parents=True,exist_ok=True)
    (target/'census_states_2024.geojson').write_bytes(state_raw)
    (target/'census_bay_counties_2024.geojson').write_bytes(county_raw)
    manifest={'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_id':'SRC-GEO-002','version':'2024-01-01','downloads':[
        {'url':state_url,'file':'census_states_2024.geojson','sha256':hashlib.sha256(state_raw).hexdigest()},
        {'url':county_url,'file':'census_bay_counties_2024.geojson','sha256':hashlib.sha256(county_raw).hexdigest()}]}
    (target/'boundary_download_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    output={'type':'FeatureCollection','features':features,'metadata':{'source_id':'SRC-GEO-002',
        'boundary_version':'2024-01-01','coordinate_system':'EPSG:4326','status':'downloaded',
        'note':'US-CA-NORTH has no polygon because its membership is not defined. Bay9 and CA are distinct comparison areas.'}}
    temp=ROOT/'geographies.geojson.tmp'
    temp.write_text(json.dumps(output,ensure_ascii=False),encoding='utf-8')
    temp.replace(ROOT/'geographies.geojson')
    print(f'Saved {len(features)} geographic features to geographies.geojson')

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print(str(exc),file=sys.stderr)
        sys.exit(1)
