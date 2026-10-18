"""Exact measurements, source grounding and safe impact decisions; no guessed truth."""
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re

UNITS = {'cm': Decimal('1'), 'mm': Decimal('0.1'), 'in': Decimal('2.54')}
CONTEXT_KEYS = ('model', 'sku', 'revision', 'region')
QUOTE = re.compile(r'^Maximum total mattress-and-topper height: ([0-9]+(?:\.[0-9]+)?) (cm|mm|in)\.$')


def measure(value, unit='cm'):
    if unit not in UNITS:
        raise ValueError('Unsupported measurement unit')
    try:
        raw = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError('Measurement is not a number') from exc
    if not raw.is_finite() or not Decimal('0') <= raw <= Decimal('10000'):
        raise ValueError('Measurement must be finite and between 0 and 10000')
    if raw.as_tuple().exponent < -6:
        raise ValueError('At most six decimal places are allowed')
    return raw * UNITS[unit]


def fmt(d):
    return format(d.normalize(), 'f')


def verify_evidence(item, ctx):
    if any(item.get(k) != ctx.get(k) or not item.get(k) for k in CONTEXT_KEYS):
        raise ValueError('Evidence belongs to another SKU/revision/region')
    body, quote = item['text'], item['quote']
    start, end = item['start'], item['end']
    if (not isinstance(body, str) or not isinstance(quote, str)
            or type(start) is not int or type(end) is not int
            or start < 0 or end <= start or end > len(body) or body[start:end] != quote):
        raise ValueError('Source quotation does not match its exact text span')
    m = QUOTE.fullmatch(quote)
    if not m or item['unit'] != m.group(2) or measure(m.group(1), m.group(2)) != measure(item['value'], item['unit']):
        raise ValueError('Value differs from quoted source')
    if measure(item['value'], item['unit']) != measure(item['normalized_cm'], 'cm'):
        raise ValueError('Stored unit conversion is not exact')
    return True


def fingerprint(bundle):
    snapshot = {k: bundle[k] for k in ('context', 'evidence', 'promises', 'authority')}
    return sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def analyze(bundle, mattress='30', topper='4', unit='cm'):
    required = measure(mattress, unit) + measure(topper, unit)
    if required <= 0:
        raise ValueError('Total height must be positive')
    verified, rejected = [], []
    for e in bundle['evidence']:
        try:
            verify_evidence(e, bundle['context'])
            verified.append(e)
        except (ValueError, TypeError, KeyError) as exc:
            rejected.append({'id':e.get('id'), 'reason':str(exc)})
    values = sorted({measure(e['normalized_cm'], 'cm') for e in verified})
    chosen = next((e for e in verified if e['id'] == bundle['authority']), None)
    blocked = bool(rejected or (bundle['authority'] and not chosen))
    if blocked or not values:
        state, limit, reason = 'BLOCKED', None, 'Missing, altered or invalid evidence. No automatic approval.'
    elif len(values) > 1 and not chosen:
        state, limit, reason = 'REVIEW_REQUIRED', None, 'Conflicting source limits: a person must choose and justify the authoritative document.'
    else:
        limit = measure(chosen['normalized_cm'], 'cm') if chosen else values[0]
        state = 'PASS' if required <= limit else 'FAIL'
        reason = 'Fits according to documented limit' if state == 'PASS' else 'Requested dimensions exceed documented limit'
    # Counterfactuals are review aids, not decisions. Every candidate comes from
    # a verified graph-backed evidence node; no source is silently preferred.
    alternatives = []
    if not rejected and len(values) > 1 and not chosen:
        for e in verified:
            candidate_limit = measure(e['normalized_cm'], 'cm')
            unsupported = [p for p in bundle['promises']
                           if measure(p['required_cm'], 'cm') > candidate_limit]
            alternatives.append({
                'evidence_id': e['id'], 'title': e['title'],
                'limit_cm': fmt(candidate_limit),
                'requested_result': 'PASS' if required <= candidate_limit else 'FAIL',
                'affected_count': len(unsupported),
                'affected_titles': [p['title'] for p in unsupported],
                'disclaimer': 'What-if scenario; not an approved source or final decision.'
            })
    changes = []
    for p in bundle['promises']:
        # Traceable, variant-scoped drafts; no speculative output if source truth is missing.
        height = measure(p['required_cm'], 'cm')
        risk = 'unknown' if limit is None else ('wrong_promise' if height > limit else 'okay')
        changes.append({'promise_id':p['id'], 'document_id':p['document_id'], 'title':p['title'],
                        'current':p['text'], 'height_cm':fmt(height), 'risk':risk,
                        'action':'REVIEW_DRAFT' if risk=='wrong_promise' else ('KEEP' if risk=='okay' else 'AWAIT_AUTHORITY'),
                        'suggestion': (f'For SKU {bundle["context"]["sku"]}, the approved maximum combined mattress-and-topper height is {fmt(limit)} cm. '
                                       f'A height of {fmt(height)} cm is not supported by the selected source.'
                                       if risk=='wrong_promise' else None)})
    return {'context':bundle['context'], 'state':state, 'reason':reason, 'required_cm':fmt(required),
            'limit_cm':fmt(limit) if limit is not None else None,
            'source_limits_cm':[fmt(v) for v in values], 'authority_id':bundle['authority'],
            'evidence':verified, 'rejected_evidence':rejected, 'alternatives':alternatives,
            'fingerprint':fingerprint(bundle), 'affected':changes,
            'impact_count':sum(c['risk']=='wrong_promise' for c in changes),
            'needs_source_review':state in ('REVIEW_REQUIRED','BLOCKED'),
            'source_disagreement':len(values)>1,
            'note':'Synthetic data; documentary support is not a physical guarantee. All edits are drafts requiring approval.'}
