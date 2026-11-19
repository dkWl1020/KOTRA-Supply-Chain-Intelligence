"""USGS public event feed adapter. No fabricated business-impact links."""
import datetime as dt,json,time,urllib.request
from api.store import *
from api.services import snapshot
USGS_URL='https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojson'
def fetch_json(url,attempts=3):
    last=None
    for attempt in range(attempts):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'KSeattleResearchPrototype/1.0','Accept':'application/geo+json,application/json'})
            with urllib.request.urlopen(req,timeout=25) as r:
                body=r.read(20_000_001)
                if len(body)>20_000_000:raise ValueError('수집 응답 크기 제한 초과')
                return json.loads(body)
        except Exception as exc:
            last=exc
            if attempt+1<attempts:time.sleep(2**attempt)
    raise RuntimeError('USGS 수집 실패: '+type(last).__name__)
def iso_ms(value):return dt.datetime.fromtimestamp(value/1000,dt.timezone.utc).isoformat(timespec='seconds') if value is not None else None
def collect_usgs(db,fetcher=fetch_json):
    cid='COL-LIVE-USGS'
    put(db,'collection_sources',{'collection_source_id':cid,'publisher':'USGS','access_method':'HTTPS GET JSON','endpoint_or_url':USGS_URL,'adapter_key':'usgs_geojson','refresh_policy':'manual or external scheduler','enabled':1,'availability_note':'M2.5+ last seven days; regional bounding boxes are screening only'})
    run={'run_id':uid('ING'),'collection_source_id':cid,'started_at':now(),'status':'running','new_count':0,'updated_count':0,'rejected_count':0};put(db,'ingestion_runs',run);db.commit()
    try:
        feed=fetcher(USGS_URL)
        if feed.get('type')!='FeatureCollection' or not isinstance(feed.get('features'),list):raise ValueError('USGS 응답 형식 오류')
        snapshot_dir=ROOT/'runtime'/'source_documents';snapshot_dir.mkdir(parents=True,exist_ok=True)
        path=snapshot_dir/(run['run_id']+'.json');raw=dumps(feed);path.write_text(raw,encoding='utf-8')
        sid='SRC-'+run['run_id'];put(db,'sources',{'source_id':sid,'publisher':'USGS','original_publisher':'USGS','title':'USGS M2.5+ past seven days feed','source_type':'government_api','url':USGS_URL,'local_document_ref':str(path.relative_to(ROOT)),'retrieved_at':now(),'version':run['run_id'],'collection_source_id':cid,'content_hash':digest(raw),'access_status':'retrieved','license_note':'USGS public-domain data; review third-party exclusions','local_snapshot_ref':str(path.relative_to(ROOT))})
        for f in feed['features']:
            db.execute('SAVEPOINT feature')
            try:
                coord=f['geometry']['coordinates']; lon,lat=coord[:2]
                # Includes Alaska and bounding box containing seven project regions.
                if not ((-180<=lon<=-129 and 50<=lat<=72) or (-125<=lon<=-104 and 36<=lat<=49.1)):
                    db.execute('RELEASE feature');continue
                p=f['properties'];eid='EV-USGS-'+f['id'];old=one(db,'events','event_id',eid)
                row={'event_id':eid,'event_type':'earthquake','title':p.get('title') or 'USGS earthquake','description':'USGS 지진 관측. 좌표 범위로 수집한 사건이며 기업 피해·시설 중단을 뜻하지 않음.','occurred_at':iso_ms(p.get('time')),'announced_at':iso_ms(p.get('updated')),'event_status':'observed','external_event_key':f['id'],'last_seen_at':now(),'expires_at':(dt.datetime.now(dt.timezone.utc)+dt.timedelta(days=7)).isoformat(timespec='seconds'),'severity_basis':dumps({'magnitude':p.get('mag'),'magnitude_type':p.get('magType'),'longitude':lon,'latitude':lat,'depth_km':coord[2] if len(coord)>2 else None}),'is_replay':0}
                put(db,'events',row);snapshot(db,'events',row)
                put(db,'evidence',{'evidence_id':'EVD-'+run['run_id']+'-'+f['id'],'record_type':'events','record_id':eid,'field_name':'occurred_at;severity_basis','source_id':sid,'locator':'features[id='+f['id']+']','excerpt':f"USGS event {f['id']}: magnitude {p.get('mag')}; location {lon}, {lat}; time {row['occurred_at']}",'support_type':'reported_observation','extraction_method':'usgs_geojson_adapter','source_version_id':run['run_id']})
                run['updated_count' if old else 'new_count']+=1
                db.execute('RELEASE feature')
            except (KeyError,TypeError,ValueError):
                db.execute('ROLLBACK TO feature');db.execute('RELEASE feature');run['rejected_count']+=1
        run.update(status='success',finished_at=now());put(db,'ingestion_runs',run);db.commit();build_index(db);return run
    except Exception as exc:
        db.rollback();run.update(status='failed',finished_at=now(),new_count=0,updated_count=0,error_ref=str(exc));put(db,'ingestion_runs',run);db.commit();return run
