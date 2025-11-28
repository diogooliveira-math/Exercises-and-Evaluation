import json
import subprocess
import sys
from pathlib import Path

def test_agent_clarify_flow_accepts_high_confidence():
    data = {
        'status':'needs_clarification',
        'missing':['module','concept'],
        'applied':{
            'module':{'value':'P4_funcoes','confidence':0.9},
            'concept':{'value':'1-generalidades_funcoes','confidence':0.95}
        },
        'suggestions':{
            'tags':['funcoes']
        },
        'parsed':{
            'discipline':'matematica',
            'statement':'Teste...'
        }
    }
    f = Path('tests') / 'tmp_needs.json'
    f.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    proc = subprocess.run([sys.executable,'scripts/agent_clarify_flow.py','--input-file',str(f)], capture_output=True, text=True)
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out['status'] == 'accept'
    assert 'command' in out


def test_agent_clarify_flow_clarify_on_low_confidence():
    data = {
        'status':'needs_clarification',
        'missing':['module','concept'],
        'applied':{
            'module':{'value':'P4_funcoes','confidence':0.4},
            'concept':{'value':'1-generalidades_funcoes','confidence':0.5}
        },
        'suggestions':{},
        'parsed':{
            'discipline':'matematica',
            'statement':'Teste...'
        }
    }
    f = Path('tests') / 'tmp_needs2.json'
    f.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    proc = subprocess.run([sys.executable,'scripts/agent_clarify_flow.py','--input-file',str(f),'--threshold','0.6'], capture_output=True, text=True)
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out['status'] == 'clarify'
    assert 'question' in out
