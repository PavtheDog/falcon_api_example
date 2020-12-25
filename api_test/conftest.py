from datetime import datetime
from py.xml import html
import pytest
import os
import sys

def pytest_html_report_title(report):
    report.title = "API Test"

def pytest_html_results_table_header(cells):
    cells.insert(2, html.th("Description"))
    #cells.insert(1, html.th("Time", class_="sortable time", col="time"))
    cells.pop()

def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(report.description))
    #cells.insert(1, html.td(datetime.utcnow(), class_="col-time"))
    cells.pop()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)

def pytest_configure(config):
  del config._metadata['Python'] 
  del config._metadata['Platform']
  del config._metadata['Packages']  
  del config._metadata['Plugins'] 
  #print (config._metadata) 
  config._metadata['Python'] = sys.version.split (' ')[0]

def pytest_report_teststatus(report):
  if report.when == 'call': # <-- Added this line
    if report.passed:
      letter = '-'
      longrep = ' \u2714 '
    elif report.skipped:
      letter = 'S'
      longrep = ' \u27A5 '
    elif report.failed:
      letter = 'F'
      longrep = ' \u2717 '
    return report.outcome, letter, report.outcome.upper() + longrep


#def pytest_html_results_summary(prefix):
#  prefix.extend([html.p("Testing against URL: ")])

#def pytest_html_results_table_row(report, cells):
#    if report.passed:
#        del cells[:]
####################################################

"""
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    extra.append(pytest_html.extras.text("some string", name="Different title"))
    if report.when == "call":
        # always add url to report
        extra.append(pytest_html.extras.url("http://www.example.com/"))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            extra.append(pytest_html.extras.html("<div>Additional HTML</div>"))
        report.extra = extra
"""

