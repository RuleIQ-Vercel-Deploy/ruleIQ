from typing import Any
import json
import re
import logging
logger = logging.getLogger(__name__)
with open('ruleiq_comprehensive_postman_collection.json', 'r') as f:
    content = f.read()
pattern = '"raw":\\s*"(\\{[^"]*\\})"'


def fix_json_string(match) ->Any:
    raw_content = match.group(1)
    escaped = raw_content.replace('\\', '\\\\').replace('\n', '\\n').replace(
        '"', '\\"')
    return f'"raw": "{escaped}"'


content = re.sub(pattern, fix_json_string, content, flags=re.DOTALL)


def fix_multiline_json(content) ->Any:
    lines = content.split('\n')
    result = []
    in_raw_block = False
    raw_content = []
    raw_prefix = ''
    for i, line in enumerate(lines):
        if '"raw": "' in line and (line.strip().endswith('{') or '{' in
            line and not line.strip().endswith('"}') and not line.strip().
            endswith('"},')):
            in_raw_block = True
            parts = line.split('"raw": "', 1)
            raw_prefix = parts[0] + '"raw": "'
            raw_content = [parts[1]]
            result.append(raw_prefix)
        elif in_raw_block:
            if line.strip() == '}' and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if (next_line == '"' or next_line == '",' or next_line.
                    startswith('}')):
                    raw_content.append(line)
                    json_str = '\n'.join(raw_content)
                    escaped = json_str.replace('\\', '\\\\').replace('\n',
                        '\\n').replace('"', '\\"')
                    result[-1] += escaped + '"'
                    in_raw_block = False
                    raw_content = []
                    raw_prefix = ''
                    continue
            elif line.strip() == '}' and (i + 1 >= len(lines) or lines[i + 
                1].strip().startswith('}')):
                raw_content.append(line)
                json_str = '\n'.join(raw_content)
                escaped = json_str.replace('\\', '\\\\').replace('\n', '\\n'
                    ).replace('"', '\\"')
                result[-1] += escaped + '"'
                in_raw_block = False
                raw_content = []
                raw_prefix = ''
            elif line.strip() in ['}"', '}",']:
                raw_content.append(line.replace('}"', '}').replace('}",', '}'))
                json_str = '\n'.join(raw_content)
                escaped = json_str.replace('\\', '\\\\').replace('\n', '\\n'
                    ).replace('"', '\\"')
                result[-1] += escaped + '"' + line[line.rfind('}') + 1:]
                in_raw_block = False
                raw_content = []
                raw_prefix = ''
            else:
                raw_content.append(line)
        else:
            result.append(line)
    if in_raw_block and raw_content:
        json_str = '\n'.join(raw_content)
        escaped = json_str.replace('\\', '\\\\').replace('\n', '\\n').replace(
            '"', '\\"')
        result[-1] += escaped + '"'
    return '\n'.join(result)


content = fix_multiline_json(content)
with open('ruleiq_comprehensive_postman_collection_fixed.json', 'w') as f:
    f.write(content)
try:
    with open('ruleiq_comprehensive_postman_collection_fixed.json', 'r') as f:
        json.load(f)
    logger.info('✅ JSON is now valid!')
except Exception as e:
    logger.info('❌ JSON still has issues: %s' % e)
