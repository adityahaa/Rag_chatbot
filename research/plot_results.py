"""Publication-export figures from saved measurements only. No model reruns."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
    run=ROOT/'research/runs'/(ROOT/'research/LATEST_RUN.txt').read_text().strip()
    rows=json.loads((run/'summary.json').read_text())
    methods=['semantic','keyword','hybrid','semantic_diverse','hybrid_diverse']
    labels=['Semantic','BM25','Hybrid','Semantic + diversity','Hybrid + diversity']
    colors=['#547985','#a8b9bc','#096c65','#bd9341','#ddbb78']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    out=ROOT/'research/figures';out.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,3,figsize=(14,4.9),sharex=True,layout='constrained')
    for ax,dataset,title in zip(axes,['aws_real_attributes','rag_multi_synthetic','controlled_synthetic'],[
            'Real product attributes\n60 cases · trivial short-record task',
            'RAG-Multi-Corpus (synthetic)\n31 eligible queries · source-document recall',
            'Controlled synthetic cases\n45 cases with available evidence']):
        data=[next(r for r in rows if r['dataset']==dataset and r['method']==m) for m in methods]
        values=[r['recall_at_3']*100 for r in data]
        ax.barh(labels,values,color=colors,height=.6)
        for i,v in enumerate(values):ax.text(v+1 if v<92 else v-2,i,f'{v:.1f}%',ha='left' if v<92 else 'right',va='center',color='white' if v>=92 and i in (0,2) else '#173b36',fontsize=9)
        ax.invert_yaxis();ax.set_xlim(0,105);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Mean Recall@3 (%)');ax.set_title(title,loc='left',fontsize=11,pad=18)
        ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Retrieval coverage differs by task; diversification is not a consistent improvement',fontsize=14,x=.05,ha='left')
    fig.savefig(out/'retrieval_recall.png',dpi=190,bbox_inches='tight');fig.savefig(out/'retrieval_recall.svg',bbox_inches='tight');plt.close(fig)
    raw=[json.loads(line) for line in (run/'per_case.jsonl').read_text().splitlines()]
    fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
    conditions=['full','missing','conflict','absent'];x=np.arange(4);width=.16
    for j,(method,label,color) in enumerate(zip(methods,labels,colors)):
        vals=[np.mean([r['literal_cell_accuracy'] for r in raw if r.get('dataset')=='controlled_synthetic' and r['method']==method and r['condition']==c])*100 for c in conditions]
        ax.bar(x+(j-2)*width,vals,width,label=label,color=color)
    ax.set_ylim(0,110);ax.set_yticks([0,25,50,75,100]);ax.set_ylabel('Literal cell-status accuracy (%)');ax.set_xticks(x,conditions);ax.set_title('Controlled synthetic cases · 15 held-out groups per condition',loc='left',pad=15)
    ax.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.12),frameon=False,fontsize=9);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.savefig(out/'controlled_conditions.png',dpi=190,bbox_inches='tight');fig.savefig(out/'controlled_conditions.svg',bbox_inches='tight');plt.close(fig)
    print('Saved four chart files from',run.name)
if __name__=='__main__':main()
