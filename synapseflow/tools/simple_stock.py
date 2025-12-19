def simple_stock(input_text: str) -> str:
    sym = input_text.strip().upper()
    if not sym:
        return 'No symbol provided.'
    return f'{sym}: PRICE=123.45 (demo placeholder)'

tool_name = 'simple_stock'
tool_description = 'Demo stock price tool (placeholder)'
tool_params = [{'name':'symbol','type':'string','description':'Stock symbol'}]
