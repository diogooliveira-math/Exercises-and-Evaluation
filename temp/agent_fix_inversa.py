# Agent script to scan and create backups and .agentfix.tex files for target directories
import os,glob,datetime,re,subprocess
root=os.path.abspath(os.getcwd())
paths=[
    os.path.join(root,'SebentasDatabase','matematica','P4_funcoes','4-funcao_inversa'),
    os.path.join(root,'ExerciseDatabase','matematica','P4_funcoes','4-funcao_inversa')
]
tex_files=[]
for p in paths:
    for f in glob.glob(os.path.join(p,'**','*.tex'), recursive=True):
        tex_files.append(f)
tex_files=sorted(tex_files)
report_lines=[]
created=[]
ts=datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
for fp in tex_files:
    rel=os.path.relpath(fp, root)
    with open(fp,'rb') as r:
        data=r.read()
    try:
        text=data.decode('utf-8')
        decode_err=False
    except Exception:
        text=data.decode('utf-8','replace')
        decode_err=True
    lines=text.splitlines()
    problems=[]
    # detect \end{figure without closing }
    for i,l in enumerate(lines, start=1):
        if '\\end{figure' in l and '\\end{figure}' not in l:
            problems.append(('missing_end_figure_brace',i,l.strip()))
    # count braces
    openb=text.count('{')
    closeb=text.count('}')
    if openb!=closeb:
        problems.append(('unbalanced_braces',openb,closeb))
    # count $ occurrences
    dollar=text.count('$')
    if dollar%2==1:
        problems.append(('odd_dollars',dollar))
    # \exercicio on own line
    for i,l in enumerate(lines, start=1):
        if re.match(r'^\s*\\exercicio\s*$', l):
            problems.append(('exercicio_alone',i))
    # subexercicio unclosed
    for i,l in enumerate(lines, start=1):
        if '\\subexercicio{' in l and '}' not in l:
            problems.append(('subexercicio_unclosed',i,l.strip()))
    if decode_err:
        problems.append(('decode_error','contains replacement chars'))
    if problems:
        # create backup
        bak=fp.replace('.tex', f'.bak_agent_{ts}.tex')
        with open(bak,'wb') as w:
            w.write(data)
        # attempt fixes heuristically
        newlines=list(lines)
        fixed_desc=[]
        for idx,l in enumerate(newlines):
            if '\\end{figure' in l and '\\end{figure}' not in l:
                newlines[idx]=l.replace('\\end{figure','\\end{figure}')
                fixed_desc.append(('fixed_end_figure',idx+1))
        openb=sum(ln.count('{') for ln in newlines)
        closeb=sum(ln.count('}') for ln in newlines)
        if openb>closeb:
            need=openb-closeb
            newlines.append('% %% Agent added to balance braces\n'+('}'*need))
            fixed_desc.append(('balanced_braces_appended',need))
        dollar=sum(ln.count('$') for ln in newlines)
        if dollar%2==1:
            newlines.append('% %% Agent added to close unmatched $\n$')
            fixed_desc.append(('closed_dollar_appended',1))
        # no automatic fix for \\exercicio alone; suggest manual
        newtext='\n'.join(newlines)
        agent=fp.replace('.tex','.agentfix.tex')
        with open(agent,'w',encoding='utf-8') as w:
            w.write(newtext)
        # try compile with pdflatex
        pdf=None
        logpath=None
        compile_ok=False
        try:
            dirname=os.path.dirname(agent)
            fname=os.path.basename(agent)
            # Run pdflatex twice for references
            cmd=['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory',dirname,fname]
            p=subprocess.run(cmd, cwd=dirname, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
            out1=p.stdout.decode('utf-8',errors='replace')
            # check pdf
            pdfpath=os.path.join(dirname, fname.replace('.agentfix.tex','.agentfix.pdf'))
            # Note: pdflatex will produce .pdf with same base name .agentfix.pdf
            logpath=agent.replace('.agentfix.tex','_agentfix_error.log')
            if os.path.exists(agent.replace('.agentfix.tex','.agentfix.pdf')):
                compile_ok=True
                pdf=agent.replace('.agentfix.tex','.agentfix.pdf')
            else:
                # save log
                with open(logpath,'w',encoding='utf-8') as lg:
                    lg.write(out1)
        except Exception as e:
            with open(agent.replace('.agentfix.tex','_agentfix_error.log'),'w',encoding='utf-8') as lg:
                lg.write(str(e))
        created.append((bak,agent,pdf,logpath,problems,fixed_desc))
        report_lines.append({'file':rel,'problems':problems,'backup':bak,'agentfix':agent,'pdf':pdf,'log':logpath,'fixes':fixed_desc})
# write report
report_file=os.path.join(root,'temp','agentfix_report_4-funcao_inversa.txt')
with open(report_file,'w',encoding='utf-8') as r:
    r.write('Agent fix report for 4-funcao_inversa\n')
    r.write('Timestamp: '+ts+'\n\n')
    for it in report_lines:
        r.write('File: '+it['file']+'\n')
        r.write(' Problems:\n')
        for p in it['problems']:
            r.write('  - '+repr(p)+'\n')
        r.write(' Backup: '+it['backup']+'\n')
        r.write(' Agentfix: '+it['agentfix']+'\n')
        r.write(' PDF: '+str(it['pdf'])+'\n')
        r.write(' Log: '+str(it['log'])+'\n')
        r.write(' Applied fixes: '+repr(it['fixes'])+'\n')
        r.write('\n')
print('Done. Scanned',len(tex_files),'files. Report at',report_file)
