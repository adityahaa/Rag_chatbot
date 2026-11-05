"""User-rated additive utility; unknown ratings are excluded, never encoded as 0."""
def score(matrix,criteria,ratings):
    cells={c['key']:c for c in matrix['cells']}
    total=sum(c['weight'] for c in criteria)
    results=[]
    for product in matrix['products']:
        numerator=known=0.;details=[]
        for criterion in criteria:
            key=product+'::'+criterion['field']
            cell=cells.get(key)
            rating=ratings.get(key)
            eligible=bool(cell and cell['confirmed'] and cell['status']=='reviewed' and rating is not None)
            if eligible:
                numerator+=criterion['weight']*rating
                known+=criterion['weight']
            details.append(dict(field=criterion['field'],weight=criterion['weight'],
                rating=rating if eligible else None,reason='Included' if eligible else 'Needs reviewed evidence and a user rating'))
        results.append(dict(product=product,score=round(numerator/known,2) if known else None,
            coverage=round(known/total*100,2) if total else 0,known_weight=known,total_weight=total,
            complete=known==total and total>0,details=details))
    return results

def brief(matrix,criteria,scores,notes=''):
    lines=['# DecisionLens decision brief','', 'Status: working decision support. Final decision belongs to the user.',
        'Synthetic examples are fictional; source dates are supplied metadata, not verified freshness.','',
        '## Decision context',notes or 'Add your objective, budget, non-negotiable requirements and decision owner.','',
        '## Priorities','Field | Requirement | Weight','--- | --- | ---']
    def esc(v): return str(v).replace('|','\\|').replace('\n',' ')
    for c in criteria:
        lines.append(f"{esc(c['field'])} | {esc(c['requirement'])} | {c['weight']}")
    lines+=['','## Evidence and review','Product | Attribute | Value | Status','--- | --- | --- | ---']
    for cell in matrix['cells']:
        lines.append(' | '.join(esc(x) for x in (cell['product'],cell['field'],cell['value'] or 'Not documented',cell['status'])))
        for e in cell['evidence']:
            lines.append(f"\n> {esc(e['excerpt'])}\n\nSource: {esc(e['name'])}; page {e['page'] or 'n/a'}; section {esc(e['section'])}; date {e['source_date'] or 'unknown'}; {e['source_url'] or 'local upload'}; synthetic={e['synthetic']}.\n")
        if cell['note']:
            lines.append('Review note: '+esc(cell['note']))
    lines+=['','## Provisional assessment',
        'Score = sum(weight × user rating) / sum(eligible weights). Ratings: 0–100, assigned by user.',
        'Only confirmed cells with a rating count. Unknown and unresolved conflicting cells are excluded.',
        'Coverage = eligible weight / total weight. Scores with unequal coverage are not directly comparable.',
        'No automatic winner is declared. Changing weights or missing evidence can change the outcome.','']
    for s in scores:
        lines.append(f"- {s['product']}: score {s['score'] if s['score'] is not None else 'unrated'} /100; weighted coverage {s['coverage']}%.")
    lines+=['','## Open questions']
    lines += [f"- {c['product']} / {c['field']}: {c['status']}" for c in matrix['cells'] if c['status'] in ('missing','conflict')]
    lines+=['','## Limitations','Literal label/value extraction misses prose and semantic equivalence. Different dates, plans or scopes may explain flagged conflicts. '
        'A citation is traceability, not proof. No currency, billing-period or unit conversions are inferred. '
        'No independent human assessment of this brief is implied.']
    return '\n'.join(lines)
