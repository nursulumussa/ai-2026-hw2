"""HW2 Medium: compare entire chat vs structured compressed memory."""
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
load_dotenv()

ROOT=Path(__file__).resolve().parents[1]
load_dotenv(ROOT/'.env')
MODEL='gpt-5.6-luna'
SYSTEM='You are a study grant office assistant. Answer concisely and honestly. Distinguish applicant claims from confirmed decisions. Remember the conversation provided to you.'

def read(name): return json.loads((ROOT/'data'/name).read_text(encoding='utf-8'))

class Session:
    def __init__(self,client):
        self.client=client; self.messages=[{'role':'system','content':SYSTEM}]
        self.state=None; self.last_tokens=0
    def respond(self,question):
        self.messages.append({'role':'user','content':question})
        res=self.client.chat.completions.create(model=MODEL,messages=self.messages)
        self.last_tokens=res.usage.prompt_tokens if res.usage else 0
        answer=res.choices[0].message.content or ''
        self.messages.append({'role':'assistant','content':answer})
        return answer
    def compress(self):
        schema=read('memory_state.schema.json')
        guidance=('Compress this conversation into a JSON object with EXACTLY these seven fields: '
                  'applicant_id, topic, facts, decisions, constraints, open_questions, language. '
                  'Keep exact document names, money amounts, appointment limitations, unanswered questions, and applicant ID. '
                  'Facts are assertions of the applicant only, not your guesses. Empty arrays instead of missing arrays. '
                  'Return ONLY JSON. Schema: '+json.dumps(schema,ensure_ascii=False))
        try:
            result=self.client.chat.completions.create(model=MODEL,
                response_format={'type':'json_object'},
                messages=self.messages+[{'role':'user','content':guidance}])
            candidate=json.loads(result.choices[0].message.content)
            validate(candidate,schema)
        except (ValueError,ValidationError,Exception) as exc:
            print('Compression failed; history preserved:',exc)
            return False
        self.state=candidate
        self.messages=[{'role':'system','content':SYSTEM},
                       {'role':'system','content':'Validated session memory (do not invent missing details): '+json.dumps(candidate,ensure_ascii=False)}]
        print('Compression successful. State:',json.dumps(candidate,ensure_ascii=False,indent=2))
        return True

def scripted(client,compressed):
    script=read('chat_script.json'); session=Session(client)
    rows=[]; probe_rows=[]
    for line in script['conversation']:
        if line=='<compress>':
            if compressed: session.compress()
            continue
        session.respond(line)
        rows.append(session.last_tokens)
    print('\nMODE:', 'B compressed' if compressed else 'A full')
    for i,n in enumerate(rows,1):print(f'Call {i}: {n} prompt tokens')
    print('Peak',max(rows),'Total',sum(rows))
    for probe in script['probes']:
        answer=session.respond(probe['question'])
        # expect_contains offers acceptable tokens/alternatives; Q5 requires both employer and letter.
        candidates=probe['expect_contains']
        got=(all(x.lower() in answer.lower() for x in candidates) if probe['id']=='Q-5'
             else any(x.lower() in answer.lower() for x in candidates))
        probe_rows.append({'id':probe['id'],'retrieved':got,'answer':answer})
        print(probe['id'],'retrieved=',got,'answer=',answer)
    return {'tokens':rows,'peak':max(rows),'total':sum(rows),
            'probes':probe_rows,'state':session.state}

def interactive(client):
    s=Session(client)
    print('Commands: compress, tokens, exit')
    while True:
        question=input('You: ').strip()
        if question.lower()=='exit': break
        if question.lower()=='tokens':print('Last prompt tokens:',s.last_tokens);continue
        if question.lower()=='compress':s.compress();continue
        if question: print('Assistant:',s.respond(question))

def main():
    args=argparse.ArgumentParser(); args.add_argument('--interactive',action='store_true')
    opt=args.parse_args(); client=OpenAI()
    if opt.interactive:interactive(client);return
    runs={'A':scripted(client,False),'B':scripted(client,True)}
    (ROOT/'medium_results.json').write_text(json.dumps(runs,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved medium_results.json')

if __name__=='__main__': main()
