#!/usr/bin/env python3
"""Final comprehensive test suite for EVENTHUB backend"""

import requests
import json

BASE = 'http://localhost:5000'

print('='*70)
print('COMPREHENSIVE BACKEND API TEST SUITE - FINAL')
print('='*70)

# Test 1: GET initial state
print('\n[TEST 1] GET /events - Read Initial Events')
r = requests.get(BASE + '/events')
status1 = 'PASS' if r.status_code == 200 else 'FAIL'
print('Status:', r.status_code, '(Expected: 200) -', status1)
initial = r.json()
print('Events count:', len(initial))
for e in initial:
    print('  - ID %d: %s' % (e['id'], e['title']))

# Test 2: POST first event
print('\n[TEST 2] POST /events - Create Birthday Party')
p1 = {'title': 'Birthday Party', 'description': 'Fun celebration', 'date': '2026-06-15'}
r = requests.post(BASE + '/events', json=p1)
status2 = 'PASS' if r.status_code == 201 else 'FAIL'
print('Status:', r.status_code, '(Expected: 201) -', status2)
e1 = r.json()
print('Created: ID %d - %s' % (e1['id'], e1['title']))

# Test 3: POST second event
print('\n[TEST 3] POST /events - Create Conference')
p2 = {'title': 'Annual Tech Conference', 'description': 'Tech gathering', 'date': '2026-07-01'}
r = requests.post(BASE + '/events', json=p2)
status3 = 'PASS' if r.status_code == 201 else 'FAIL'
print('Status:', r.status_code, '(Expected: 201) -', status3)
e2 = r.json()
print('Created: ID %d - %s' % (e2['id'], e2['title']))

# Test 4: PUT - update first event
print('\n[TEST 4] PUT /events/%d - Update Event' % e1['id'])
update = {'title': 'Birthday Bash Updated', 'description': 'Updated description!'}
r = requests.put(BASE + '/events/%d' % e1['id'], json=update)
status4 = 'PASS' if r.status_code == 200 else 'FAIL'
print('Status:', r.status_code, '(Expected: 200) -', status4)
updated = r.json()
print('Updated: ID %d - %s' % (updated['id'], updated['title']))

# Test 5: DELETE - remove second event
print('\n[TEST 5] DELETE /events/%d - Delete Event' % e2['id'])
r = requests.delete(BASE + '/events/%d' % e2['id'])
status5 = 'PASS' if r.status_code == 204 else 'FAIL'
print('Status:', r.status_code, '(Expected: 204) -', status5)

# Test 6: GET final state
print('\n[TEST 6] GET /events - Final State')
r = requests.get(BASE + '/events')
status6 = 'PASS' if r.status_code == 200 else 'FAIL'
print('Status:', r.status_code, '(Expected: 200) -', status6)
final = r.json()
print('Total events:', len(final))
for e in final:
    print('  - ID %d: %s (desc: %s)' % (e['id'], e['title'], e['description']))

# Test 7: Verify error handling - GET non-existent event
print('\n[TEST 7] GET /events/999999 - Error Handling')
r = requests.get(BASE + '/events/999999')
print('Status:', r.status_code, '(Expected: 404)')

# Test 8: Verify error handling - POST without title
print('\n[TEST 8] POST /events (no title) - Error Handling')
r = requests.post(BASE + '/events', json={'description': 'No title', 'date': '2026-01-01'})
print('Status:', r.status_code, '(Expected: 400)')

print('\n' + '='*70)
print('SUMMARY')
print('='*70)
results = [status1, status2, status3, status4, status5, status6]
passed = sum(1 for s in results if s == 'PASS')
print('Tests Passed: %d/6' % passed)
print('='*70)
