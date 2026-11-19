"""Local-only HTTP API. The development server is not a multi-user deployment."""
import json,mimetypes,os,sqlite3,urllib.parse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from .store import *
from .services import *
from ingest.feeds import collect_usgs
READABLE={'regions','region_memberships','industries','companies','facilities','products','activities','statistics','projects','relationships','routes','route_segments','risk_profiles','events','event_impacts','regulations','response_options','sources','evidence','metric_definitions','classification_mappings','relationship_routes','regulation_scopes','evaluation_cases','region_industries','collection_sources','company_contexts','watchlists','alerts','analysis_runs','review_history','reports','ingestion_runs','record_versions'}

def query_data(db,table,params):
    if table not in READABLE:raise ValueError('이 데이터셋은 조회할 수 없어요')
    rs=rows(db,table); q=params.get('q','').strip().casefold()
    if q:rs=[r for r in rs if q in ' '.join(str(v) for v in r.values() if v is not None).casefold()]
    region=params.get('region_id'); industry=params.get('industry_id')
    if region:
        members={region}
        # Display union only: Bay9 is a known northern-California facility grouping,
        # not a replacement for a 40-county statistical boundary.
        if region=='US-CA-NORTH':members.add('US-CA-BAY9')
        memberships=rows(db,'region_memberships');regions=rows(db,'regions')
        while True:
            expanded=members|{r['member_region_id'] for r in memberships if r['research_region_id'] in members}|{r['region_id'] for r in regions if r.get('parent_id') in members}
            if expanded==members:break
            members=expanded
        facilities={r['facility_id'] for r in rows(db,'facilities') if r.get('region_id') in members}
        companies={r['operator_company_id'] for r in rows(db,'facilities') if r['facility_id'] in facilities}
        if table=='companies':rs=[r for r in rs if r['company_id'] in companies]
        elif table=='relationships':rs=[r for r in rs if r.get('from_company_id') in companies or r.get('to_company_id') in companies]
        elif 'region_id' in columns(db,table):rs=[r for r in rs if r.get('region_id') in members]
        elif table=='events':rs=[r for r in rs if r.get('location_ref') in members]
    if industry:
        if 'industry_id' in columns(db,table):rs=[r for r in rs if r.get('industry_id')==industry]
        elif table in ('companies','relationships'):
            ids={r['company_id'] for r in rows(db,'activities') if r.get('industry_id')==industry}
            rs=[r for r in rs if r['company_id'] in ids] if table=='companies' else [r for r in rs if r.get('from_company_id') in ids or r.get('to_company_id') in ids]
    for k,v in params.items():
        if k not in ('q','region_id','industry_id','limit','offset') and k in columns(db,table):rs=[r for r in rs if str(r.get(k,''))==v]
    total=len(rs);offset=max(0,int(params.get('offset',0)));limit=min(1000,max(1,int(params.get('limit',100))))
    return {'rows':rs[offset:offset+limit],'total':total}

class Handler(BaseHTTPRequestHandler):
    server_version='KSeattleLocal/1.0'
    def log_message(self,format,*args):pass
    def send(self,obj,status=200,ctype='application/json; charset=utf-8'):
        body=(dumps(obj) if ctype.startswith('application/json') else obj).encode() if not isinstance(obj,bytes) else obj
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
    def handle_request(self,method):
        db=None
        try:
            u=urllib.parse.urlsplit(self.path);path=u.path;params={k:v[-1] for k,v in urllib.parse.parse_qs(u.query).items()}
            host=self.headers.get('Host','').split(':')[0]
            if host not in ('localhost','127.0.0.1','[::1]'):return self.send({'error':'로컬 실행 주소만 허용해요'},403)
            data={}
            if method!='GET':
                origin=self.headers.get('Origin')
                if origin and urllib.parse.urlsplit(origin).netloc!=self.headers.get('Host'):return self.send({'error':'다른 사이트의 쓰기 요청은 허용하지 않아요'},403)
                if not self.headers.get('Content-Type','').startswith('application/json'):return self.send({'error':'JSON 요청이 필요해요'},415)
                length=int(self.headers.get('Content-Length',0))
                if length>2_000_000:return self.send({'error':'요청 크기 초과'},413)
                data=json.loads(self.rfile.read(length) or b'{}')
                if not isinstance(data,dict):raise ValueError('객체 형식 요청이 필요해요')
            if not path.startswith('/api/'):
                if method!='GET':return self.send({'error':'경로 오류'},404)
                rel='index.html' if path=='/' else urllib.parse.unquote(path.lstrip('/'))
                file=(ROOT/'web'/rel).resolve()
                if not file.is_relative_to((ROOT/'web').resolve()) or not file.is_file():return self.send({'error':'파일이 없어요'},404)
                return self.send(file.read_bytes(),ctype=(mimetypes.guess_type(file.name)[0] or 'application/octet-stream')+'; charset=utf-8')
            db=connect();parts=path.strip('/').split('/')
            if method=='GET':
                if path=='/api/catalog':return self.send({'counts':{t:db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in sorted(READABLE) if t in tables(db)},'datasets':sorted(READABLE),'mode':'single_operator','ai_configured':bool(os.environ.get('OPENAI_API_KEY') and os.environ.get('OPENAI_MODEL'))})
                if path.startswith('/api/data/'):return self.send(query_data(db,parts[2],params))
                if path=='/api/search':return self.send({'rows':search(db,params.get('q',''))})
                if path=='/api/map':return self.send({'facilities':[r for r in rows(db,'facilities') if r.get('latitude') is not None and r.get('longitude') is not None]})
                if len(parts)==4 and parts[1]=='reports' and parts[3]=='export':return self.send(export_report(db,parts[2]),ctype='text/html; charset=utf-8')
            if method=='POST':
                if path=='/api/analyze':return self.send(analyze(db,data))
                if path=='/api/reports':return self.send(make_report(db,data),201)
                if path=='/api/watchlists':return self.send(create_watchlist(db,data),201)
                if path=='/api/refresh-alerts':return self.send(refresh_alerts(db))
                if path=='/api/ingest/usgs':return self.send(collect_usgs(db))
                if len(parts)==4 and parts[1]=='reports' and parts[3]=='review':return self.send(review_report(db,parts[2],data))
            if method=='PATCH':
                if len(parts)==3 and parts[1]=='reports':return self.send(edit_report(db,parts[2],data))
                if len(parts)==3 and parts[1]=='alerts':return self.send(update_alert(db,parts[2],data))
            self.send({'error':'지원하지 않는 API 경로예요'},404)
        except (ValueError,KeyError,json.JSONDecodeError,sqlite3.IntegrityError) as exc:
            if db:db.rollback()
            self.send({'error':str(exc)},400)
        except Exception as exc:
            if db:db.rollback()
            self.send({'error':'작업에 실패했어요. 설정과 입력 자료를 점검해 주세요.','error_type':type(exc).__name__},500)
        finally:
            if db:db.close()
    def do_GET(self):self.handle_request('GET')
    def do_POST(self):self.handle_request('POST')
    def do_PATCH(self):self.handle_request('PATCH')
def serve(port=8000):
    print(f'KOTRA local prototype: http://127.0.0.1:{port} (Ctrl+C to stop)')
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
