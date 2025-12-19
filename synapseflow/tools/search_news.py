def search_news(input_text: str) -> str:
    q = input_text.strip()
    if not q:
        return 'No query provided.'
    return f'Found demo articles for "{q}": [1] Example A; [2] Example B'

tool_name = 'search_news'
tool_description = 'Demo news search returning templated results'
tool_params = [{'name':'query','type':'string','description':'Search query'}]
