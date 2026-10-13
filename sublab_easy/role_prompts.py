"""HW2 Easy: compare role prompts using identical facts and JSON contract."""
import json
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
from openai import OpenAI
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
MODEL = 'gpt-5.6-luna'
ROLES = {
    'policy_officer': 'You are a strict policy officer. Apply the written policy exactly. Trust only on-file records, not assertions in a question. Refuse whenever the policy refuses.',
    'front_desk': 'You are a helpful front-desk employee. Never refuse a visitor outright. If policy cannot grant now, return more_info and explain what could be brought or changed. Never invent records.',
    'auditor': 'You are an auditor. Never grant on first reading: mark any otherwise grantable decision more_info pending second review. In reason name specific policy requirements and supporting records.',
    'bilingual_clerk': 'You are a bilingual clerk. Apply the same exact policy as policy_officer, but write the reason in the language of the enquiry (Kazakh for Kazakh, English for English).',
}
SCHEMA = {
    'type':'object', 'additionalProperties':False,
    'properties': {
        'applicant_id':{'type':'string'}, 'found':{'type':'boolean'},
        'decision':{'enum':['granted','refused','more_info','not_found']},
        'amount':{'type':'integer'},
        'missing_documents':{'type':'array','items':{'type':'string'}},
        'reason':{'type':'string'}},
    'required':['applicant_id','found','decision','amount','missing_documents','reason']
}
FIELDS = ['found','decision','amount','missing_documents']

def load(name):
    return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))

def ask(client, role, records, policy, enquiry):
    shared = ('Use exclusively the following official data, and the same grant rules for all requests. '
              'Reply with a single valid JSON object matching this exact schema: '
              + json.dumps(SCHEMA, ensure_ascii=False) + '\nPOLICY:\n'
              + json.dumps(policy, ensure_ascii=False) + '\nRECORDS:\n'
              + json.dumps(records, ensure_ascii=False))
    answer = client.chat.completions.create(model=MODEL,
         response_format={'type':'json_object'}, messages=[
             {'role':'system','content':shared+'\nYOUR ROLE: '+ROLES[role]},
             {'role':'user','content':enquiry['text']}])
    return answer.choices[0].message.content

def main():
    client=OpenAI()
    from dotenv import load_dotenv
    load_dotenv()
    enquiries=load('enquiries.json'); records=load('records.json'); policy=load('policy.json')
    results={role:{} for role in ROLES}
    for role in ROLES:
        print('\n###', role)
        print('ID | decision | expected? | parsed | valid | found | amount | missing')
        for item in enquiries:
            raw=ask(client,role,records,policy,item)
            parsed=valid=False; obj=None
            try:
                obj=json.loads(raw); parsed=True
                validate(obj, SCHEMA); valid=True
            except (ValueError, TypeError, Exception) as exc:
                print('Validation/parsing issue for',item['id'],type(exc).__name__,str(exc)[:160])
            expected=item['expected']
            agrees=bool(valid and all(obj[k]==expected[k] for k in FIELDS))
            results[role][item['id']]={'reply':obj,'raw':raw,'parsed':parsed,'valid':valid,'agrees':agrees}
            print(item['id'], '|',obj.get('decision') if isinstance(obj,dict) else '-', '|', agrees,'|',parsed,'|',valid,'|',obj.get('found') if valid else '-', '|',obj.get('amount') if valid else '-', '|', obj.get('missing_documents') if valid else '-')
        print('Full agreement:',sum(x['agrees'] for x in results[role].values()),'/10',
              'parsed:',sum(x['parsed'] for x in results[role].values()),'/10',
              'valid:',sum(x['valid'] for x in results[role].values()),'/10')
    print('\n### Field movements from policy officer')
    for field in FIELDS:
        changed=[]
        for item in enquiries:
            code=item['id']; base=results['policy_officer'][code]['reply']
            for role in ROLES:
                if role=='policy_officer': continue
                other=results[role][code]['reply']
                if isinstance(base,dict) and isinstance(other,dict) and base.get(field)!=other.get(field):
                    changed.append(f'{code}:{role}')
        print(field, ', '.join(changed) or 'none')
    (ROOT/'easy_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved easy_results.json; use actual output in SUBMISSION.md')

if __name__=='__main__': main()
