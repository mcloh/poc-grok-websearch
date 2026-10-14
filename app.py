import os,time,secrets,asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
import requests
from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel,Field

app=FastAPI(title='Grok OCI · Web Search',docs_url=None,redoc_url=None)
auth=HTTPBasic()
def authorize(c:HTTPBasicCredentials=Depends(auth)):
    if not (secrets.compare_digest(c.username,'poc') and secrets.compare_digest(c.password,os.environ['APP_PASSWORD'])):
        raise HTTPException(401,'Acesso restrito',headers={'WWW-Authenticate':'Basic'})
class Turn(BaseModel):
    role:str
    content:str=Field(max_length=8000)
class Chat(BaseModel):
    message:str=Field(min_length=1,max_length=8000)
    history:list[Turn]=Field(default_factory=list,max_length=12)
@app.get('/health')
def health():return {'status':'ok','provider':'OCI','model':os.environ.get('OCI_MODEL','xai.grok-4.3'),'tool':'web_search'}
@app.get('/',dependencies=[Depends(authorize)])
def index():return FileResponse('static/index.html')
@app.get('/app.js',dependencies=[Depends(authorize)])
def js():return FileResponse('static/app.js',media_type='application/javascript')
lock=asyncio.Semaphore(2)
@app.post('/api/chat',dependencies=[Depends(authorize)])
async def chat(q:Chat):
    if any(t.role not in ('user','assistant') for t in q.history):raise HTTPException(422,'Papel inválido')
    base=os.environ['OCI_BASE_URL'].rstrip('/')
    if urlparse(base).hostname!='inference.generativeai.us-chicago-1.oci.oraclecloud.com':raise HTTPException(503,'Endpoint OCI inválido')
    now=datetime.now(ZoneInfo('America/Sao_Paulo'))
    body={'model':os.environ.get('OCI_MODEL','xai.grok-4.3'),'input':[t.model_dump() for t in q.history]+[{'role':'user','content':q.message}],
      'instructions':f'Você é um assistente em português brasileiro. Hoje é {now.isoformat()}. Use a ferramenta web_search para verificar informações atuais. Cite fontes com URLs e datas. Diferencie data de publicação e data do fato. Nunca invente notícias; se não houver evidência de hoje, diga isso claramente.',
      'tools':[{'type':'web_search'}],'store':False,'max_output_tokens':2400}
    started=time.monotonic()
    async with lock:
      try:r=await asyncio.to_thread(requests.post,base+'/responses',json=body,headers={'Authorization':'Bearer '+os.environ['OCI_API_KEY'],'OpenAI-Project':os.environ['OCI_PROJECT_ID']},timeout=(10,150))
      except requests.RequestException:raise HTTPException(502,'Falha de conexão com OCI')
    if r.status_code!=200:raise HTTPException(502,{'message':'OCI recusou a chamada','provider_status':r.status_code})
    d=r.json();texts=[];citations=[];calls=[]
    for item in d.get('output',[]):
      if item.get('type')=='web_search_call':calls.append(item)
      for c in item.get('content',[]):
        if c.get('text'):texts.append(c['text'])
        for a in c.get('annotations',[]):
          if a.get('type')=='url_citation':citations.append(a)
    return {'answer':'\n'.join(texts),'citations':citations,'web_search_calls':calls,'usage':d.get('usage'),'response_id':d.get('id'),'model':d.get('model'),'provider':'OCI','timestamp':now.isoformat(),'seconds':round(time.monotonic()-started,2),'raw_response':d}
