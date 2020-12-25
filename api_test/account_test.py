import logging
import os
import pytest
import requests

from datetime import datetime
from py.xml import html


url = 'http://127.0.0.1:8000'
account_name = 'app'
account_code = 'test'
bad_account_name = 'bad'
bad_account_code = 'bad'

################################################################

def pytest_namespace():
  return {'current_account_total': 0}

def test_home():
  '''
    Testing site connection
  '''
  route_test = '/'
  x = requests.get(url + route_test, timeout=0.001)
  if 'Welcome to' in x.content.decode('utf-8'):
    print ()
    assert True
  else:
    print('Unable to connect to home')
    assert False

def test_account():
  '''
    Testing connection to site with account
  '''
  route_test = '/test'
  bad_auth=(bad_account_name, bad_account_code)
  auth=(account_name, account_code)
  test_failed = False

  x = requests.get(url + route_test, auth=auth)
  if not 'Account credentials are correct.' in (x.content.decode('utf-8')):
    print ('Credentialed test failed.')
    test_failed = True

  x = requests.get(url + route_test, auth=bad_auth)
  if not type(x.json()) is str:
    if not 'Invalid Username/Password.' in (x.json()['description']):
      print ('Bad Credentialed test failed.')
      test_failed = True
  else:
    print ('Bad Credentialed test failed.')
    test_failed = True

  if test_failed:
    assert False
  else:
    print ()
    assert True

def test_get_accounts():
  '''
    Testing to see if api can retrieve list of accounts
  '''
  route_test = '/account'
  auth=(account_name, account_code)
  test_failed = False

  results = requests.get(url + route_test, auth=auth)
  if 'error' in results.json():
    pytest.current_account_total = len(results.json()['response'])
    if results.json()['error']:
      print ('Unable to get accounts.')
      test_failed = True
  else:
    print ('Unable to get accounts.')
    test_failed = True

  if test_failed:
    assert False
  else:
    print ()
    assert True

def test_post_accounts():
  '''
    Testing to see if api can insert new account and error handling
  '''
  route_test = '/account'
  auth=(account_name, account_code)
  test_failed = False

  payload = {
              "name":"app1",
              "code":"test",
              "description":"Test"
            }

  results = requests.post(url + route_test, auth=auth, json=payload)
  if 'error' in results.json():
    if results.json()['error']:
      print ('Unable to create account.')
      test_failed = True

  results = requests.get(url + route_test, auth=("app1", "test"))
  if 'error' in results.json():
    if results.json()['error']:
      print ('Unable to verify account.')
      test_failed = True
    if len(results.json()['response']) != pytest.current_account_total + 1:
      print ('Unable to verify account.')
      test_failed = True


  results = requests.post(url + route_test, auth=auth, json=payload)
  if not 'error' in results.json():
    if results.json()['error']:
      print ('Unable to check account.')
      test_failed = True

  if test_failed:
    assert False
  else:
    print ()
    assert True

def test_update_accounts():
  '''
    Testing to see if api can update account and error handling
  '''
  route_test = '/account'
  auth=(account_name, account_code)
  test_failed = False

  payload = {
              "name":"app2",
              "code":"test",
              "description":"Test"
            }

  results = requests.put(url + route_test, auth=auth, json=payload)
  if 'error' in results.json():
    if not results.json()['error']:
      print ('Unable to check failed update account. Because account exists.')
      test_failed = True

  results = requests.post(url + route_test, auth=auth, json=payload)
  if 'error' in results.json():
    if results.json()['error']:
      print ('Unable to create account.')
      test_failed = True

  results = requests.get(url + route_test, auth=("app2", "test"))
  if 'error' in results.json():
    if results.json()['error']:
      print ('Unable to verify account.')
      test_failed = True

  results = requests.post(url + route_test, auth=auth, json=payload)
  if not 'error' in results.json():
    if results.json()['error']:
      print ('Unable to check account.')
      test_failed = True

  if test_failed:
    assert False
  else:
    print ()
    assert True

def test_delete_accounts():
  '''
    Testing to see if api can delete account and error handling
  '''
  route_test = '/account'
  auth=(account_name, account_code)
  test_failed = False

  payload = {
              "name":"app1",
            }

  results = requests.delete(url + route_test, auth=auth, json=payload)
  if 'error' in results.json():
    if results.json()['error']:
      print ('Unable to delete account')
      test_failed = True

  results = requests.delete(url + route_test, auth=auth, json=payload)
  if not 'error' in results.json():
    if results.json()['error']:
      print ('Unable to check failed delete account.')
      test_failed = True

  payload = {
              "name":"app2",
            }

  results = requests.delete(url + route_test, auth=auth, json=payload)
  if 'error' in results.json():
    if results.json()['error']:
      print ('Unable to delete account')
      test_failed = True

  if test_failed:
    assert False
  else:
    print ()
    assert True

def test_failed():
  '''
    Testing Failed
  '''
  assert False

def test_skip():
  '''
    Testing Skipped
  '''
  pytest.skip('Example Skip')