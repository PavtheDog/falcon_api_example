import logging
import os
import pytest
import requests

from datetime import datetime
from py.xml import html

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