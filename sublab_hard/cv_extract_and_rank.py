"""HW2 Hard: extract evidence-backed CVs, get criterion scores, rank IN CODE."""
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from jsonschema import validate
from dotenv import load_dotenv
load_dotenv()

ROOT=Path(__file__).resolve().parents[1]
load_dotenv(ROOT/'.env')
MODEL='gpt-5.6-luna'
FIELDS=['candidate_id','full_name','degree','graduation_year','gpa_4_scale',
        'gpa_original_scale','languages','published_peer_reviewed_outputs',
        'relevant_experience_months','evidence','ambiguities','unpublished_papers']
SCHEMA={'type':'object','required':FIELDS,'additionalProperties':False,
 'properties':{
  'candidate_id':{'type':'string'}, 'full_name':{'type':['string','null']},
  'degree':{'type':['string','null']},'graduation_year':{'type':['integer','null']},
  'gpa_4_scale':{'type':['number','null']},'gpa_original_scale':{'type':['string','null']},
  'languages':{'type':'array','items':{'type':'string'}},
  'published_peer_reviewed_outputs':{'type':['integer','null']},
  'relevant_experience_months':{'type':['integer','null']},
  'evidence':{'type':'object','additionalProperties':{'type':['string','null']}},
  'ambiguities':{'type':'array','items':{'type':'string'}},
  'unpublished_papers':{'type':'array','items':{'type':'string'}}}}

def call_json(client,system,user):
    response=client.chat.completions.create(model=MODEL,
        response_format={'type':'json_object'}, messages=[{'role':'system','content':system},
        {'role':'user','content':user}])
    return json.loads(response.choices[0].message.content)

def main():
    client=OpenAI();rubric=json.loads((ROOT/'data'/'candidate_rubric.json').read_text(encoding='utf-8'))
    extracted=[]; scores=[]
    files=sorted((ROOT/'data'/'candidates').glob('story-*.md'))
    if len(files)!=6: raise FileNotFoundError('Expected 6 candidate stories in data/candidates/')
    for path in files:
        story=path.read_text(encoding='utf-8'); cid=path.stem
        system=('You are a rigorous evidence-based CV extractor. Return EXACTLY one JSON object matching the schema. '
                'Every field must have a supporting literal quote in evidence keyed by field name; use null if absent. '
                'No guessing or averaging; any contradiction gives null and a note in ambiguities. '
                'Convert stated GPA to a 4.0 scale; record original scale. '
                'Only published or accepted peer-reviewed papers count. Submitted, under review, in preparation, '
                'in press and planned do NOT count: put in unpublished_papers. '
                'Count relevant experience in months; overlapping intervals count once; undated experience is excluded. '
                'If publications or experience are not mentioned, report zero only if clearly none; else use null. '
                'JSON SCHEMA: '+json.dumps(SCHEMA))
        try:
            cv=call_json(client,system,'Candidate ID is '+cid+'\nSTORY:\n'+story)
            validate(cv,SCHEMA)
            cv['candidate_id']=cid
            valid=True
        except Exception as exc:
            print(cid,'extraction failure:',exc);valid=False;cv={'candidate_id':cid,'error':str(exc)}
        extracted.append({'id':cid,'valid':valid,'cv':cv})
        print('\nEXTRACTION',cid,'valid=',valid,'null=',[k for k,v in cv.items() if v is None])
        print(json.dumps(cv,ensure_ascii=False,indent=2))
        if not valid: continue
        scoring_system=('Score the candidate using ONLY the rubric below and the validated extracted CV. '
                        'Return a JSON object with exactly three numeric keys: academic, research, experience. '
                        'Each score 0 to 5. Do not calculate weighted scores or rank. '
                        'For contradictions treat the disputed GPA as unknown; explain this in written report. '
                        'RUBRIC: '+json.dumps(rubric,ensure_ascii=False))
        try:
            result=call_json(client,scoring_system,json.dumps(cv,ensure_ascii=False))
            if set(result)!={'academic','research','experience'}:raise ValueError('Unexpected keys')
            if not all(isinstance(result[k],(float,int)) and 0<=result[k]<=5 for k in result):raise ValueError('Score outside 0-5')
            weights={c['id']:c['weight'] for c in rubric['criteria']}
            total=round(sum(result[k]*weights[k] for k in weights),2)
            scores.append({'id':cid,**result,'weighted_total':total})
            print('SCORES',cid,result,'CODE TOTAL=',total)
        except Exception as exc:print(cid,'scoring failed:',exc)
    ranked=sorted(scores,key=lambda r:(-r['weighted_total'],r['id']))
    print('\n### CODE RANKING')
    for item in ranked:print(item)
    print('Winner:',ranked[0]['id'] if ranked else 'none')
    narrative=client.chat.completions.create(model=MODEL,messages=[
        {'role':'system','content':'You are a committee adviser. Give a short prose recommendation for one winner and your reasoning.'},
        {'role':'user','content':'RUBRIC: '+json.dumps(rubric,ensure_ascii=False)+'\nCVs: '+json.dumps([x['cv'] for x in extracted if x['valid']],ensure_ascii=False)+'\nWho should win?'}
    ]).choices[0].message.content
    print('\n### INDEPENDENT MODEL PROSE RECOMMENDATION\n'+narrative)
    (ROOT/'hard_results.json').write_text(json.dumps({'extractions':extracted,'scores':scores,'ranking':ranked,'model_prose':narrative},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved hard_results.json')

if __name__=='__main__': main()
