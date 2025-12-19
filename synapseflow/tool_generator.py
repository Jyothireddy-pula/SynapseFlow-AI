import os, re, json, textwrap

TOOL_TEMPLATE = '''"""Auto-generated tool: {name}

Description:
{desc}
"""

def {func_name}(input_text: str) -> str:
    """Auto-generated stub. Replace with real implementation."""
    return "AUTO-GEN: " + input_text

tool_name = '{tool_name}'
tool_description = {desc_json}
tool_params = {params_json}
'''

def slugify(name: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9_]+', '_', name).strip('_').lower()
    if s and s[0].isdigit():
        s = '_' + s
    return s

def create_tool_from_description(description: str, tools_dir: str = 'synapseflow/tools'):
    os.makedirs(tools_dir, exist_ok=True)
    lines = [l.strip() for l in description.strip().splitlines() if l.strip()]
    name = lines[0][:60] if lines else 'generated_tool'
    func_name = slugify(name)
    file_name = func_name + '.py'
    params = []
    for line in lines:
        if line.lower().startswith('use:'):
            params.append({'name':'input_text','description':line[4:].strip(),'type':'string'})
    content = TOOL_TEMPLATE.format(name=name, desc=description, func_name=func_name, tool_name=name.replace("'",''), desc_json=json.dumps(description), params_json=json.dumps(params))
    path = os.path.join(tools_dir, file_name)
    with open(path, 'w') as f:
        f.write(content)
    return path

if __name__ == '__main__':
    p = create_tool_from_description('Weather tool\nUse: city name in input_text.')
    print('Created', p)
