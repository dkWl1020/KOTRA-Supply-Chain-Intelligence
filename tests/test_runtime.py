import csv,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from api.store import connect,initialize,put,one,rows,import_csv,validate,record_exists
from api.services import analyze,make_report,edit_report,review_report,export_report,validate_result,context_for,create_watchlist,refresh_alerts,update_alert
from ingest.feeds import collect_usgs

class RuntimeTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.db=connect(Path(self.temp.name)/'db.sqlite');initialize(self.db)
  put(self.db,'companies',{'company_id':'CO-T','name_en':'Test corporation','country':'US','entity_type':'company','is_demo':1})
  put(self.db,'sources',{'source_id':'SRC-T','publisher':'Test fixture','title':'Fixture','source_type':'test_fixture','url':'https://example.invalid/fixture','version':'1'})
  put(self.db,'evidence',{'evidence_id':'EVD-T','record_type':'companies','record_id':'CO-T','source_id':'SRC-T','locator':'fixture','excerpt':'시험용 기업이다.','support_type':'test_fixture'})
  self.db.commit()
 def tearDown(self):self.db.close();self.temp.cleanup()
 def test_analysis_report_review_edit_and_export(self):
  analysis=analyze(self.db,{'company_id':'CO-T','use_ai':False});self.assertEqual(analysis['status'],'completed')
  report=make_report(self.db,{'analysis_id':analysis['analysis_id'],'company_id':'CO-T'})
  approved=review_report(self.db,report['report_id'],{'version':1,'decision':'approved'});self.assertEqual(approved['status'],'approved')
  edited=edit_report(self.db,report['report_id'],{'version':1,'content':'<script>bad</script>수정'});self.assertEqual(edited['version'],2);self.assertEqual(edited['status'],'draft');self.assertIsNone(edited['review_id'])
  self.assertNotIn('<script>bad</script>',export_report(self.db,report['report_id']));self.assertIn('&lt;script&gt;',export_report(self.db,report['report_id']))
  with self.assertRaises(ValueError):edit_report(self.db,report['report_id'],{'version':1,'content':'stale'})
  self.db.rollback()
  snapshots=self.db.execute('SELECT COUNT(*) FROM _record_snapshots WHERE record_type="reports"').fetchone()[0];self.assertEqual(snapshots,3)
 def test_reject_invented_or_mismatched_citations(self):
  context=context_for(self.db,'CO-T')
  for finding in [ {'statement':'x','evidence_ids':['EVD-NO'],'record_ids':['CO-T']},{'statement':'x','evidence_ids':['EVD-T'],'record_ids':[]},{'statement':'x','evidence_ids':[],'record_ids':['CO-T']}]:
   with self.assertRaises(ValueError):validate_result({'summary':'','findings':[finding],'limitations':[],'response_options':[]},context)
 def test_no_ai_credentials_does_not_fall_back(self):
  with patch.dict(os.environ,{'OPENAI_API_KEY':'','OPENAI_MODEL':''}):
   with self.assertRaises(ValueError):analyze(self.db,{'company_id':'CO-T','use_ai':True})
  self.assertEqual(rows(self.db,'analysis_runs')[0]['status'],'failed')
 def test_csv_idempotence_atomic_reject_and_numeric_zero(self):
  d=Path(self.temp.name)/'data';d.mkdir()
  def write(row):
   with (d/'companies.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['company_id','name_en','country','entity_type','parent_company_id','is_demo']);w.writeheader();w.writerow(row)
  row={'company_id':'CO-NEW','name_en':'New','country':'US','entity_type':'company','is_demo':'0'};write(row)
  self.assertEqual(import_csv(self.db,d)['status'],'success');self.assertEqual(one(self.db,'companies','company_id','CO-NEW')['is_demo'],0)
  self.assertEqual(import_csv(self.db,d)['unchanged_count'],1)
  row['name_en']='Edited';write(row);self.assertEqual(import_csv(self.db,d)['status'],'success')
  self.assertEqual(self.db.execute('SELECT MAX(version) FROM _record_snapshots WHERE record_id="CO-NEW"').fetchone()[0],2)
  row.update(company_id='CO-BAD',parent_company_id='NO-SUCH');write(row);self.assertEqual(import_csv(self.db,d)['status'],'failed');self.assertIsNone(one(self.db,'companies','company_id','CO-BAD'))
 def test_poly_reference_rejects_unknown_composite(self):
  self.assertFalse(record_exists(self.db,'region_industries','US-Z|IND-Z'))
 def test_alert_dedupe_and_replay_exclusion(self):
  put(self.db,'events',{'event_id':'EVENT-T','event_type':'test','title':'test','event_status':'active','is_replay':0})
  put(self.db,'event_impacts',{'impact_id':'IM-T','event_id':'EVENT-T','target_type':'companies','target_id':'CO-T','impact_type':'reported','assessment_basis':'test'})
  self.db.commit();create_watchlist(self.db,{'target_type':'companies','target_id':'CO-T'});self.assertEqual(refresh_alerts(self.db)['created'],1);self.assertEqual(refresh_alerts(self.db)['created'],0)
  a=rows(self.db,'alerts')[0];update_alert(self.db,a['alert_id'],{'action':'read'});refresh_alerts(self.db);self.assertIsNotNone(one(self.db,'alerts','alert_id',a['alert_id'])['read_at'])
  put(self.db,'events',{'event_id':'EVENT-REPLAY','event_type':'test','title':'test','event_status':'active','is_replay':1});put(self.db,'event_impacts',{'impact_id':'IM-R','event_id':'EVENT-REPLAY','target_type':'companies','target_id':'CO-T','impact_type':'reported','assessment_basis':'test'});self.db.commit();self.assertEqual(refresh_alerts(self.db)['created'],0)
 def test_collection_failure_preserves_prior_events(self):
  put(self.db,'events',{'event_id':'EXISTING','event_type':'test','title':'existing','event_status':'observed'});self.db.commit()
  def fail(url):raise RuntimeError('fixture offline')
  result=collect_usgs(self.db,fetcher=fail);self.assertEqual(result['status'],'failed');self.assertIsNotNone(one(self.db,'events','event_id','EXISTING'));self.assertEqual(rows(self.db,'ingestion_runs')[0]['status'],'failed')
 def test_missing_target_regulation_is_not_silently_imported(self):
  put(self.db,'classification_mappings',{'mapping_id':'MAP-T','target_type':'companies','target_id':'NO-SUCH','code_system':'NAICS','code_version':'2022','code':'31','mapping_scope':'test','source_id':'SRC-T'})
  self.assertTrue(any(x['table']=='classification_mappings' for x in validate(self.db)))
if __name__=='__main__':unittest.main()

class HandlerTests(unittest.TestCase):
 setUp=RuntimeTests.setUp
 tearDown=RuntimeTests.tearDown
 def request(self,method,path,body=None,origin=None):
  import io
  from email.message import Message
  from api.server import Handler
  from api.store import connect
  h=Handler.__new__(Handler);h.path=path;h.headers=Message();h.headers['Host']='127.0.0.1:8000'
  if origin:h.headers['Origin']=origin
  raw=json.dumps(body or {}).encode();h.rfile=io.BytesIO(raw);h.headers['Content-Type']='application/json';h.headers['Content-Length']=str(len(raw))
  result={}
  def send(value,status=200,ctype='application/json; charset=utf-8'):result.update(value=value,status=status,ctype=ctype)
  h.send=send
  with patch('api.server.connect',lambda:connect(Path(self.temp.name)/'db.sqlite')):h.handle_request(method)
  return result
 def test_handler_company_analysis_review_roundtrip(self):
  cat=self.request('GET','/api/catalog');self.assertEqual(cat['status'],200);self.assertEqual(cat['value']['counts']['companies'],1)
  company=self.request('GET','/api/data/companies?q=Test');self.assertEqual(company['value']['total'],1)
  a=self.request('POST','/api/analyze',{'company_id':'CO-T','use_ai':False});self.assertEqual(a['status'],200)
  r=self.request('POST','/api/reports',{'company_id':'CO-T','analysis_id':a['value']['analysis_id']});self.assertEqual(r['status'],201)
  report=r['value'];approved=self.request('POST','/api/reports/'+report['report_id']+'/review',{'version':1,'decision':'approved'});self.assertEqual(approved['value']['status'],'approved')
  edited=self.request('PATCH','/api/reports/'+report['report_id'],{'version':1,'content':'변경'});self.assertEqual(edited['value']['status'],'draft')
  exported=self.request('GET','/api/reports/'+report['report_id']+'/export');self.assertEqual(exported['status'],200);self.assertIn('변경',exported['value'])
 def test_handler_rejects_cross_site_write_and_unknown_tables(self):
  self.assertEqual(self.request('POST','/api/watchlists',{'target_type':'companies','target_id':'CO-T'},origin='https://example.invalid')['status'],403)
  self.assertEqual(self.request('GET','/api/data/_record_snapshots')['status'],400)
