#!/usr/bin/env python3
"""python run.py init | validate | index | serve | collect-usgs"""
import argparse,json,os
from api.store import *
def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['init','validate','index','serve','collect-usgs']);parser.add_argument('--port',type=int,default=8000);args=parser.parse_args()
    # A local .env is optional. Never prints keys.
    env=ROOT/'.env'
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                k,v=line.split('=',1);os.environ.setdefault(k.strip(),v.strip().strip('\"').strip("'"))
    db=connect();initialize(db)
    if args.command=='init':
        result=import_csv(db)
        if result['status']=='success':result['indexed_chunks']=build_index(db)
        print(dumps(result));raise SystemExit(0 if result['status']=='success' else 1)
    if args.command=='validate':
        errors=validate(db);print(dumps({'errors':errors,'valid':not errors}));raise SystemExit(bool(errors))
    if args.command=='index':print(dumps({'chunks':build_index(db)}))
    if args.command=='collect-usgs':
        from ingest.feeds import collect_usgs
        result=collect_usgs(db);print(dumps(result));raise SystemExit(result['status']!='success')
    if args.command=='serve':
        db.close()
        from api.server import serve
        serve(args.port)
if __name__=='__main__':main()
