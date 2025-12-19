import requests
def get_weather(input_text: str) -> str:
    city = input_text.strip()
    if not city:
        return 'No city provided.'
    try:
        # Uses wttr.in public API (no key) - simple text output
        resp = requests.get(f'https://wttr.in/{city}?format=3', timeout=5)
        return resp.text
    except Exception as e:
        return 'Weather tool failed: ' + str(e)

tool_name = 'get_weather'
tool_description = 'Fetch simple weather text from wttr.in (demo)'
tool_params = [{'name':'city_name','type':'string','description':'City name'}]
