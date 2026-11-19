"""SQLite storage, typed CSV import and reproducible text indexing (stdlib only)."""
from __future__ import annotations
import csv, datetime as dt, hashlib, json, math, os, sqlite3, uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def now(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
def uid(prefix): return prefix+'-'+uuid.uuid4().hex[:16]
def dumps(v): return json.dumps(v,ensure_ascii=False,sort_keys=True)
def digest(v): return hashlib.sha256((v if isinstance(v,str) else dumps(v)).encode()).hexdigest()
def db_path(): return Path((os.environ.get('KOTRA_DB') or str(ROOT/'runtime'/'kotra.sqlite')))
def connect(path=None):
    p=Path(path or db_path()); p.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(p,timeout=30); db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON'); db.execute('PRAGMA busy_timeout=30000')
    return db

def tables(db): return [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'") if not r[0].startswith('search_')]
def columns(db,table):
    if table not in tables(db): raise ValueError('존재하지 않는 데이터셋')
    return {r['name']:dict(r) for r in db.execute(f'PRAGMA table_info("{table}")')}
def pk(db,table): return [k for k,v in sorted(columns(db,table).items(),key=lambda i:i[1]['pk']) if v['pk']]
def rows(db,table):
    columns(db,table)
    return [dict(x) for x in db.execute(f'SELECT * FROM "{table}"')]
def one(db,table,key,value):
    if key not in columns(db,table): raise ValueError('존재하지 않는 열')
    r=db.execute(f'SELECT * FROM "{table}" WHERE "{key}"=?',(value,)).fetchone()
    return dict(r) if r else None

def put(db,table,row):
    cols=columns(db,table); extra=set(row)-set(cols)
    if extra: raise ValueError(f'{table}: 알 수 없는 열 {sorted(extra)}')
    keys=list(row); keycols=pk(db,table)
    if not keys: raise ValueError('빈 기록')
    q=','.join('"'+k+'"' for k in keys); vals=[dumps(row[k]) if isinstance(row[k],(list,dict)) else row[k] for k in keys]
    updates=','.join(f'"{k}"=excluded."{k}"' for k in keys if k not in keycols)
    conflict=' ON CONFLICT('+','.join('"'+k+'"' for k in keycols)+') DO '+('UPDATE SET '+updates if updates else 'NOTHING') if keycols else ''
    db.execute(f'INSERT INTO "{table}" ({q}) VALUES ({",".join("?" for _ in keys)})'+conflict,vals)

def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS _app_migrations (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)')
    for p in sorted((ROOT/'db'/'migrations').glob('*.sql')):
        if not db.execute('SELECT 1 FROM _app_migrations WHERE name=?',(p.name,)).fetchone():
            db.executescript(p.read_text(encoding='utf-8'))
            db.execute('INSERT INTO _app_migrations VALUES (?,?)',(p.name,now()))
            db.commit()
    db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS search_chunks USING fts5(chunk_id UNINDEXED,source_id UNINDEXED,locator UNINDEXED,text)')
    db.commit()

def typed(value,col):
    if value=='': return None
    t=col['type'].upper()
    if t=='INTEGER':
        if str(value).lower() in ('true','false'): return int(str(value).lower()=='true')
        n=float(value)
        if not math.isfinite(n) or n != int(n): raise ValueError('정수 형식 오류')
        return int(n)
    if t in ('REAL','FLOAT','DOUBLE','NUMERIC'):
        n=float(value)
        if not math.isfinite(n): raise ValueError('유한한 수치만 허용')
        return n
    return value

POLY={'company':'companies','companies':'companies','facility':'facilities','facilities':'facilities','region':'regions','regions':'regions','industry':'industries','industries':'industries','product':'products','products':'products','route':'routes','routes':'routes','route_segment':'route_segments','segment':'route_segments','route_segments':'route_segments','relationship':'relationships','relationships':'relationships','event':'events','events':'events','regulation':'regulations','regulations':'regulations','statistic':'statistics','statistics':'statistics','observation':'statistics','project':'projects','projects':'projects','activity':'activities','activities':'activities','risk_profile':'risk_profiles','risk_profiles':'risk_profiles','response_option':'response_options','response_options':'response_options','region_industries':'region_industries','metric_definition':'metric_definitions','metric_definitions':'metric_definitions','collection_sources':'collection_sources','sources':'sources'}
def resolve_table(kind): return POLY.get(kind,kind)
def record_exists(db,kind,id):
    table=resolve_table(kind)
    if table not in tables(db): return False
    keys=pk(db,table)
    if len(keys)!=1:
        try:
            values=json.loads(id) if str(id).startswith('[') else str(id).split('|')
            if not isinstance(values,list) or len(values)!=len(keys): return False
            where=' AND '.join('"'+k+'"=?' for k in keys)
            return db.execute(f'SELECT 1 FROM "{table}" WHERE {where}',values).fetchone() is not None
        except (ValueError,TypeError):return False
    return one(db,table,keys[0],id) is not None

def validate(db):
    errors=[]
    for r in db.execute('PRAGMA foreign_key_check'): errors.append({'table':r[0],'row':r[1],'error':'foreign_key','target':r[2]})
    for table,typecol,idcol in [('evidence','record_type','record_id'),('risk_profiles','target_type','target_id'),('event_impacts','target_type','target_id'),('watchlists','target_type','target_id'),('classification_mappings','target_type','target_id')]:
        if table not in tables(db): continue
        for row in rows(db,table):
            if row.get(idcol) and not record_exists(db,row.get(typecol),row[idcol]): errors.append({'table':table,'id':row[idcol],'error':'unresolved_reference','kind':row.get(typecol)})
    spec=json.loads((ROOT/'schemas'/'datasets.json').read_text(encoding='utf-8'))
    for table,ds in spec['datasets'].items():
        if table not in tables(db):continue
        jsoncols=[c['name'] for c in ds['columns'] if c.get('format')=='json']
        for row in rows(db,table):
            for col in jsoncols:
                if row.get(col) is not None:
                    try: json.loads(row[col])
                    except (ValueError,TypeError):errors.append({'table':table,'column':col,'error':'invalid_json'})
    if 'statistics' in tables(db):
        for r in rows(db,'statistics'):
            m=one(db,'metric_definitions','metric_id',r['metric_id'])
            if m and m.get('default_unit') and r.get('unit')!=m['default_unit']: errors.append({'table':'statistics','id':r['observation_id'],'error':'unit_mismatch'})
            if r.get('value') is None and r.get('value_status') in ('observed','available'): errors.append({'table':'statistics','id':r['observation_id'],'error':'missing_value'})
    return errors

def import_csv(db,directory=None):
    """All-or-nothing import; reject logs are retained outside the transaction."""
    directory=Path(directory or ROOT/'data'); report={'started_at':now(),'new_count':0,'updated_count':0,'unchanged_count':0,'errors':[]}
    run_id=uid('CSV-ING')
    put(db,'ingestion_runs',{'run_id':run_id,'started_at':report['started_at'],'status':'running','new_count':0,'updated_count':0,'rejected_count':0});db.commit()
    try:
        db.execute('BEGIN'); db.execute('PRAGMA defer_foreign_keys=ON')
        for path in sorted(directory.glob('*.csv')):
            table=path.stem
            if table not in tables(db): continue
            cols=columns(db,table); keycols=pk(db,table)
            with path.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f)
                extra=set(reader.fieldnames or [])-set(cols)
                if extra: raise ValueError(f'{path.name}: 알 수 없는 열 {sorted(extra)}')
                for line,r in enumerate(reader,2):
                    try:
                        row={k:typed(v,cols[k]) for k,v in r.items()}
                        where=' AND '.join('"'+k+'"=?' for k in keycols)
                        old=db.execute(f'SELECT * FROM "{table}" WHERE {where}',[row[k] for k in keycols]).fetchone() if keycols else None
                        if old and all(old[k]==v for k,v in row.items()): report['unchanged_count']+=1; continue
                        put(db,table,row)
                        if table not in ('record_versions','review_history','ingestion_runs'):
                            from .services import snapshot
                            snapshot(db,table,row)
                        report['updated_count' if old else 'new_count']+=1
                    except Exception as e: raise ValueError(f'{path.name}:{line}: {e}') from e
        issues=validate(db)
        if issues: raise ValueError(dumps(issues[:25]))
        db.commit(); report['status']='success'
    except Exception as e:
        db.rollback(); report.update(status='failed',errors=[str(e)],new_count=0,updated_count=0)
    report['finished_at']=now()
    put(db,'ingestion_runs',{'run_id':run_id,'started_at':report['started_at'],'finished_at':report['finished_at'],'status':report['status'],'new_count':report['new_count'],'updated_count':report['updated_count'],'rejected_count':len(report['errors']),'error_ref':dumps(report['errors']) if report['errors'] else None});db.commit()
    log=ROOT/'runtime'/'import_log.json'; log.parent.mkdir(parents=True,exist_ok=True); log.write_text(dumps(report),encoding='utf-8')
    return report

def build_index(db):
    chunks=[]
    for e in rows(db,'evidence'):
        s=one(db,'sources','source_id',e['source_id'])
        text=e.get('excerpt') or ''
        if not text: continue
        chunk={'chunk_id':'CH-'+digest(e['evidence_id'])[:18],'source_id':e['source_id'],'document_version':s.get('version') if s else None,'locator':e.get('locator'),'text':text,'content_hash':digest(text),'access_scope':('internal' if s and (s.get('source_type') in ('user_provided','internal','private') or 'private' in (s.get('access_note') or '').lower() or 'restricted' in (s.get('access_note') or '').lower()) else 'public')}
        chunks.append(chunk)
    db.execute('DELETE FROM search_chunks')
    db.executemany('INSERT INTO search_chunks(chunk_id,source_id,locator,text) VALUES (?,?,?,?)',[(r['chunk_id'],r['source_id'],r['locator'],r['text']) for r in chunks]); db.commit()
    (ROOT/'document_chunks.jsonl').write_text(''.join(dumps(c)+'\n' for c in chunks),encoding='utf-8')
    index=ROOT/'search_index'; index.mkdir(exist_ok=True)
    (index/'manifest.json').write_text(dumps({'engine':'SQLite FTS5 + Unicode substring fallback','embedding_model_ref':None,'chunk_count':len(chunks),'built_at':now(),'content_hash':digest(chunks),'database':'runtime/kotra.sqlite','scope':'source-scoped evidence excerpts; not complete source texts'}),encoding='utf-8')
    return len(chunks)

def search(db,q):
    if not q.strip(): return []
    # Literal substring supports Korean substrings; parameterized query avoids FTS syntax errors.
    return [dict(r) for r in db.execute('SELECT chunk_id,source_id,locator,text FROM search_chunks WHERE text LIKE ? LIMIT 100',('%'+q+'%',))]
