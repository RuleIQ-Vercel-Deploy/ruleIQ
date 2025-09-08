"""
Fix JSON parsing errors in comprehensive Postman collections
Addresses duplicate keys, malformed structures, and syntax errors
"""
from typing import Any, Dict, Tuple
import json
import re
import sys
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


def fix_json_file(filepath) ->Tuple[Any, ...]:
    """Fix common JSON errors in Postman collections"""
    logger.info('🔧 Fixing JSON errors in: %s' % filepath)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub('"raw":\\s*"[^"]*",\\s*"raw":', '"raw":', content)
        content = re.sub(
            '"raw":\\s*"([^"]*)\\\\\\",\\\\n\\s*\\\\"host\\\\".*?\\\\"path\\\\".*?\\]\\\\n\\s*\\}"'
            , '"raw": "\\1"', content, flags=re.MULTILINE | re.DOTALL)
        content = re.sub('\\\\"', '"', content)
        content = re.sub(',(\\s*[}\\]])', '\\1', content)
        content = re.sub('"raw":\\s*"\\s*"', '"raw": ""', content)
        try:
            json_data = json.loads(content)
            logger.info('✅ JSON structure validated successfully')
            output_path = filepath.replace('.json', '_repaired.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info('✅ Repaired file saved as: %s' % output_path)
            return output_path, len(json_data.get('item', []))
        except json.JSONDecodeError as e:
            logger.info('❌ JSON validation failed after fixes: %s' % e)
            debug_path = filepath.replace('.json', '_debug.json')
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info('📋 Debug file saved as: %s' % debug_path)
            return None, 0
    except Exception as e:
        logger.info('❌ Error processing file: %s' % e)
        return None, 0


def main() ->Dict[str, Any]:
    """Fix all comprehensive Postman collection files"""
    files_to_fix = ['ruleiq_comprehensive_postman_collection_fixed.json',
        'ruleiq_comprehensive_postman_collection_v2.json']
    results = []
    for filename in files_to_fix:
        filepath = f'/home/omar/Documents/ruleIQ/{filename}'
        if Path(filepath).exists():
            output_path, endpoint_count = fix_json_file(filepath)
            if output_path:
                results.append((output_path, endpoint_count))
    logger.info('\n📊 JSON Repair Summary:')
    for output_path, count in results:
        logger.info('✅ %s: %s endpoints ready for testing' % (Path(
            output_path).name, count))
    return results


if __name__ == '__main__':
    main()
