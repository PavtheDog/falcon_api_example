# falcon_api_example
Example using Falcon API<br />
<br />
Windows:<br />
- API:<br />
   - hupper -m waitress --port=8000 app:api<br />
- API Test:<br />
  - pytest --html=api_report.html --self-contained-html --tb=no<br />