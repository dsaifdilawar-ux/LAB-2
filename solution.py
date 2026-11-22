#!/usr/bin/env python3
"""Week 02: create a toy block chain with account balances and tamper check."""
import argparse, hashlib, json


def digest(obj):
    """Deterministic SHA-256 of any JSON-serialisable object."""
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    ).hexdigest()


def make_block(index, previous, transactions):
    block = {'height': index, 'previous_hash': previous, 'transactions': transactions}
    block['hash'] = digest(block)          # hash commits to the body
    return block


def validate(chain):
    for i, block in enumerate(chain):
        body = {k: v for k, v in block.items() if k != 'hash'}
        if block['hash'] != digest(body):
            return False, f'block {i} content changed'
        if i and block['previous_hash'] != chain[i - 1]['hash']:
            return False, f'block {i} points to wrong previous block'
    return True, 'hash links correct'


p = argparse.ArgumentParser()
p.add_argument('--tamper', action='store_true')
args = p.parse_args()

balances = {'Alice': 100, 'Bob': 10}
txs = [{'from': 'Alice', 'to': 'Bob', 'amount': 60, 'nonce': 1},   # extension: 60 (was 25)
       {'from': 'Bob', 'to': 'Alice', 'amount': 50, 'nonce': 1}]

accepted = []
for t in txs:
    if balances[t['from']] < t['amount']:
        print('REJECT insufficient funds:', t)
    else:
        balances[t['from']] -= t['amount']
        balances[t['to']] += t['amount']
        accepted.append(t)

chain = [make_block(0, '0' * 64, [{'genesis': True}])]
chain.append(make_block(1, chain[0]['hash'], accepted))
print('ACCEPTED:', accepted, 'BALANCES:', balances)
assert len(accepted) == 2 and balances == {'Alice': 90, 'Bob': 20}
print('CHAIN:', [(b['height'], b['hash'][:12]) for b in chain])
print('VALID BEFORE TAMPER:', validate(chain))
if args.tamper:
    chain[1]['transactions'][0]['amount'] = 999
    print('VALID AFTER TAMPER:', validate(chain))
    assert not validate(chain)[0]
else:
    assert validate(chain)[0]
print('PASS: transaction admission and tamper evidence demonstrated.')
