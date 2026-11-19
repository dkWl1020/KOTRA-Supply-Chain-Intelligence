"""Evidence-constrained analysis and durable report/review workflows."""
import html,json,os,urllib.request
from .store import *

def snapshot(db,table,row):
    keys=pk(db,table); rid='|'.join(str(row[k]) for k in keys)
    old=db.execute('SELECT version,snapshot FROM _record_snapshots WHERE record_type=? AND record_id=? ORDER BY version DESC LIMIT 1',(table,rid)).fetchone()
    content=dumps(row)
    if old and old['snapshot']==content: return old['version']
    version=(old['version'] if old else 0)+1
    db.execute('INSERT INTO _record_snapshots VALUES (?,?,?,?,?)',(table,rid,version,content,now()))
    put(db,'record_versions',{'record_type':table,'record_id':rid,'version':version,'valid_from':now(),'recorded_at':now(),'change_type':'update' if old else 'create','changed_by':'local_operator'})
    return version

def evidence_for(db,table,ids):
    return [r for r in rows(db,'evidence') if resolve_table(r['record_type'])==table and r['record_id'] in ids]

def context_for(db,company_id,event_id=None):
    company=one(db,'companies','company_id',company_id)
    if not company: raise ValueError('기업 ID를 선택해 주세요')
    records={'companies':[company],'facilities':[r for r in rows(db,'facilities') if company_id in (r.get('operator_company_id'),r.get('owner_company_id'))], 'relationships':[r for r in rows(db,'relationships') if company_id in (r.get('from_company_id'),r.get('to_company_id'))]}
    records['activities']=[r for r in rows(db,'activities') if r.get('company_id')==company_id]
    records['statistics']=[r for r in rows(db,'statistics') if r.get('company_id')==company_id or r.get('facility_id') in {f['facility_id'] for f in records['facilities']}]
    targets={('companies',company_id)}|{('facilities',r['facility_id']) for r in records['facilities']}|{('relationships',r['relationship_id']) for r in records['relationships']}
    impacts=[r for r in rows(db,'event_impacts') if (resolve_table(r['target_type']),r['target_id']) in targets]
    if event_id:
        event=one(db,'events','event_id',event_id)
        if not event: raise ValueError('사건 ID가 존재하지 않아요')
        records['events']=[event]; impacts=[r for r in impacts if r.get('event_id')==event_id]
    else:
        eventids={r.get('event_id') for r in impacts}; records['events']=[r for r in rows(db,'events') if r['event_id'] in eventids]
    records['event_impacts']=impacts
    records['company_contexts']=[r for r in rows(db,'company_contexts') if r['company_id']==company_id]
    industries={r['industry_id'] for r in records['activities']}
    records['response_options']=[r for r in rows(db,'response_options') if r.get('industry_id') in industries][:12]
    ev=[]
    for table,rs in records.items():
        keys=pk(db,table)
        if len(keys)==1: ev.extend(evidence_for(db,table,{r[keys[0]] for r in rs}))
    ev=list({e['evidence_id']:e for e in ev}.values())
    sourceids={r['source_id'] for r in ev}
    return {'company_id':company_id,'selected_event_id':event_id,'records':records,'evidence':ev,'sources':[r for r in rows(db,'sources') if r['source_id'] in sourceids]}

def validate_result(result,context):
    if not isinstance(result,dict): raise ValueError('AI 출력은 객체여야 해요')
    required=('summary','findings','limitations','response_options')
    if any(k not in result for k in required): raise ValueError('AI 출력 항목이 빠졌어요')
    if not isinstance(result['summary'],str) or any(not isinstance(result[k],list) for k in required[1:]): raise ValueError('AI 출력 자료형 오류')
    valid_e={e['evidence_id'] for e in context['evidence']}
    valid_r={str(r[next(iter(r))]) for table,rs in context['records'].items() for r in rs}
    evidence_by_id={e['evidence_id']:e for e in context['evidence']}
    for finding in result['findings']:
        if not isinstance(finding,dict) or not isinstance(finding.get('statement'),str): raise ValueError('주장 형식 오류')
        eids=finding.get('evidence_ids'); rids=finding.get('record_ids')
        if not isinstance(eids,list) or not isinstance(rids,list): raise ValueError('근거·기록 ID 목록 오류')
        if not eids: raise ValueError('근거 없는 사실 주장은 저장할 수 없어요')
        if not rids or not set(eids)<=valid_e or not set(rids)<=valid_r: raise ValueError('조회 범위를 벗어난 근거·기록 ID')
        supported={evidence_by_id[e]['record_id'] for e in eids}
        if not set(rids)<=supported:raise ValueError('근거와 주장 대상 기록이 일치하지 않아요')
    if any(not isinstance(x,str) for x in result['limitations']): raise ValueError('제한 항목 형식 오류')
    if any(not isinstance(x,str) for x in result['response_options']): raise ValueError('대응 항목 형식 오류')
    return result

def offline_analysis(context):
    c=context['records']['companies'][0]; findings=[]
    for e in context['evidence'][:20]:
        if e.get('excerpt'): findings.append({'statement':e['excerpt'],'evidence_ids':[e['evidence_id']],'record_ids':[e['record_id']]})
    limits=['이 결과는 저장된 근거를 모은 규칙 기반 미리보기예요. 생성형 AI는 실행하지 않았어요.','공개 자료만으로 기업의 재고·납품 물량·실제 이용 경로·피해액을 추정하지 않아요.']
    if context['selected_event_id'] and not context['records']['event_impacts']: limits.append('선택한 사건과 이 기업을 잇는 등록된 영향 근거가 없어요. 거래 중단으로 해석할 수 없어요.')
    if any(e.get('is_replay') for e in context['records']['events']): limits.append('과거 사건이 포함되어 있어요. 현재 진행 중인 위험으로 표시하지 않아요.')
    return {'summary':f"{c.get('name_ko') or c['name_en']}의 등록 자료 {len(context['evidence'])}개 근거를 검토할 수 있어요.",'findings':findings,'limitations':limits,'response_options':[r['action'] for r in context['records']['response_options'] if r.get('action')]}

def call_ai(context):
    key=os.environ.get('OPENAI_API_KEY'); model=os.environ.get('OPENAI_MODEL')
    if not key or not model: raise ValueError('OPENAI_API_KEY와 OPENAI_MODEL을 설정한 뒤 AI 분석을 실행해 주세요')
    prompt=(ROOT/'prompts'/'company_impact.md').read_text(encoding='utf-8')
    payload={'model':model,'messages':[{'role':'system','content':prompt},{'role':'user','content':dumps(context)}],'response_format':{'type':'json_object'}}
    request=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(request,timeout=90) as response: output=json.load(response)
    content=output['choices'][0]['message'].get('content')
    if not content: raise ValueError('AI가 분석 결과를 반환하지 않았어요')
    return validate_result(json.loads(content),context)

def analyze(db,data):
    context=context_for(db,data.get('company_id'),data.get('event_id') or None)
    aid=uid('AN'); record={'analysis_id':aid,'case_ref':data.get('event_id'),'context_version':max([x.get('version') or 1 for x in context['records']['company_contexts']] or [1]),'input_record_versions':context['records'],'source_versions':context['sources'],'model_ref':os.environ.get('OPENAI_MODEL') if data.get('use_ai') else 'rules-v1','prompt_version':'company-impact-v1','schema_version':'analysis-v1','status':'running','created_at':now()}
    put(db,'analysis_runs',record); db.commit()
    try:
        result=call_ai(context) if data.get('use_ai') else offline_analysis(context)
        validate_result(result,context)
        # Retain exact evidence payload so later source revisions do not change this analysis.
        result['evidence_snapshot']=context['evidence']; result['source_snapshot']=context['sources']; result['company_id']=data['company_id']
        record.update(status='completed',result=result); put(db,'analysis_runs',record); snapshot(db,'analysis_runs',record); db.commit()
        return record
    except Exception as exc:
        record.update(status='failed',error=str(exc)); put(db,'analysis_runs',record); db.commit(); raise

def make_report(db,data):
    analysis=one(db,'analysis_runs','analysis_id',data.get('analysis_id'))
    if not analysis or analysis['status']!='completed': raise ValueError('완료된 분석을 선택해 주세요')
    result=json.loads(analysis['result'])
    if data.get('company_id')!=result.get('company_id'): raise ValueError('분석 기업과 보고서 기업이 달라요')
    text=result['summary']+'\n\n[자료에서 확인할 내용]\n'+'\n'.join(f"• {f['statement']} ({', '.join(f['evidence_ids'])})" for f in result['findings'])+'\n\n[분석 범위]\n'+'\n'.join('• '+x for x in result['limitations'])+'\n\n[대응 선택지]\n'+'\n'.join('• '+x for x in result['response_options'])
    report={'report_id':uid('RP'),'company_id':data['company_id'],'analysis_id':data['analysis_id'],'version':1,'content':text,'evidence_refs':sorted({x for f in result['findings'] for x in f['evidence_ids']}),'status':'draft','created_at':now()}
    put(db,'reports',report); snapshot(db,'reports',report); db.commit(); return report

def edit_report(db,id,data):
    db.execute('BEGIN IMMEDIATE')
    report=one(db,'reports','report_id',id)
    if not report: raise ValueError('보고서가 없어요')
    if data.get('version')!=report['version']: raise ValueError('다른 변경이 있어요. 보고서를 다시 열어 주세요')
    if not isinstance(data.get('content'),str) or not data['content'].strip(): raise ValueError('내용을 입력해 주세요')
    report.update(content=data['content'],version=report['version']+1,status='draft',review_id=None,export_file_ref=None)
    put(db,'reports',report); snapshot(db,'reports',report); db.commit(); return report

def review_report(db,id,data):
    db.execute('BEGIN IMMEDIATE')
    report=one(db,'reports','report_id',id)
    if not report: raise ValueError('보고서가 없어요')
    if data.get('version')!=report['version']: raise ValueError('수정된 버전을 다시 검토해 주세요')
    if data.get('decision') not in ('approved','rejected'): raise ValueError('검토 결정을 선택해 주세요')
    review={'review_id':uid('RV'),'analysis_id':report['analysis_id'],'report_version':report['version'],'reviewer_id':None,'decision':data['decision'],'edited_content':report['content'],'reason':data.get('reason',''),'reviewed_at':now()}
    put(db,'review_history',review); report.update(review_id=review['review_id'],status=data['decision']); put(db,'reports',report); snapshot(db,'reports',report); db.commit(); return report

def export_report(db,id):
    report=one(db,'reports','report_id',id)
    if not report: raise ValueError('보고서가 없어요')
    analysis=one(db,'analysis_runs','analysis_id',report['analysis_id']); result=json.loads(analysis['result'])
    sources={s['source_id']:s for s in result.get('source_snapshot',[])}; refs=[]
    for e in result.get('evidence_snapshot',[]):
        s=sources.get(e['source_id'],{}); url=s.get('url','')
        if not url.startswith(('https://','http://')): continue
        refs.append('<li>'+html.escape(e['evidence_id'])+' · <a href="'+html.escape(url,quote=True)+'">'+html.escape(s.get('title','자료'))+'</a> · '+html.escape(e.get('locator') or '')+'</li>')
    template=(ROOT/'report_templates'/'report.html').read_text(encoding='utf-8')
    return template.replace('{{title}}',html.escape('기업 대응 검토 보고서')).replace('{{status}}',html.escape(report['status'])).replace('{{version}}',str(report['version'])).replace('{{content}}',html.escape(report['content'])).replace('{{references}}',''.join(refs))

def create_watchlist(db,data):
    table=resolve_table(data.get('target_type'))
    if table not in ('companies','facilities','regions','industries','products'): raise ValueError('관심 대상 유형 오류')
    if not record_exists(db,table,data.get('target_id')): raise ValueError('관심 대상 ID가 없어요')
    existing=next((r for r in rows(db,'watchlists') if r['target_type']==table and r['target_id']==data['target_id']),None)
    if existing:return existing
    row={'watchlist_id':uid('WL'),'owner_id':None,'target_type':table,'target_id':data['target_id'],'filters':data.get('filters') or {},'created_at':now()};put(db,'watchlists',row);db.commit();return row

def refresh_alerts(db):
    rules=json.loads((ROOT/'risk_rules.yaml').read_text(encoding='utf-8'))
    count=0
    for watch in rows(db,'watchlists'):
        for impact in rows(db,'event_impacts'):
            if resolve_table(impact['target_type'])!=watch['target_type'] or impact['target_id']!=watch['target_id']: continue
            event=one(db,'events','event_id',impact.get('event_id'))
            if not event or event.get('is_replay') or event.get('event_status') not in rules['eligible_event_statuses']:continue
            if event.get('ended_at') or (event.get('expires_at') and event['expires_at']<=now()):continue
            dedupe=watch['watchlist_id']+':'+event['event_id']
            if one(db,'alerts','dedupe_key',dedupe):continue
            row={'alert_id':uid('AL'),'event_id':event['event_id'],'regulation_id':impact.get('regulation_id'),'watchlist_id':watch['watchlist_id'],'priority_reason':impact.get('impact_description') or '등록된 영향 연결','dedupe_key':dedupe,'expires_at':event.get('expires_at')};put(db,'alerts',row);count+=1
    db.commit();return {'created':count,'message':'등록된 직접 영향 연결만 알림으로 만들어요. 과거 시연 사건은 제외해요.'}

def update_alert(db,id,data):
    row=one(db,'alerts','alert_id',id)
    if not row:raise ValueError('알림이 없어요')
    action=data.get('action'); field={'read':'read_at','dismiss':'dismissed_at','snooze':'snoozed_until'}.get(action)
    if not field:raise ValueError('알림 동작 오류')
    value=data.get('until') if action=='snooze' else now()
    if action=='snooze':
        try:dt.datetime.fromisoformat(value)
        except Exception:raise ValueError('보류 종료 시각을 ISO 형식으로 입력해 주세요')
    row[field]=value;put(db,'alerts',row);db.commit();return row
