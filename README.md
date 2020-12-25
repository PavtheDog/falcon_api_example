![PavWeb2](https://user-images.githubusercontent.com/51343959/58841379-986b4180-8637-11e9-9dd2-219979601ac8.PNG)

# falcon_api_example
Example using Falcon API<br />
<br />
Windows:<br />
- API:<br />
   - hupper -m waitress --port=8000 app:api<br />
- API Test:<br />
  - pytest --html=api_report.html --self-contained-html --tb=no<br />