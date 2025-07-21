#!/usr/bin/env python3
"""Fix settings to handle list parsing correctly"""

import re

# Read the current settings file
with open("config/settings.py", "r") as f:
    content = f.read()

# We need to modify how list fields are defined to prevent automatic JSON parsing
# The issue is that pydantic_settings v2 tries to parse List fields as JSON automatically

# Replace List[str] fields with Union[List[str], str] and add validators
replacements = [
    # CORS fields
    (
        r'cors_origins: Annotated\[List\[str\], BeforeValidator\(parse_list_from_string\)\] = Field\(default=\["http://localhost:3000"\]\)',
        'cors_origins: Union[List[str], str] = Field(default=["http://localhost:3000"])',
    ),
    (
        r'cors_allowed_origins: Annotated\[List\[str\], BeforeValidator\(parse_list_from_string\)\] = Field\(default=\["http://localhost:3000"\]\)',
        'cors_allowed_origins: Union[List[str], str] = Field(default=["http://localhost:3000"])',
    ),
    (
        r'allowed_hosts: Annotated\[List\[str\], BeforeValidator\(parse_list_from_string\)\] = Field\(default=\["localhost", "127.0.0.1"\]\)',
        'allowed_hosts: Union[List[str], str] = Field(default=["localhost", "127.0.0.1"])',
    ),
    # File types field
    (
        r'allowed_file_types: Annotated\[List\[str\], BeforeValidator\(parse_list_from_string\)\] = Field\(\s*default=\["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "jpg", "jpeg", "png", "gif"\]\s*\)',
        """allowed_file_types: Union[List[str], str] = Field(
        default=["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "jpg", "jpeg", "png", "gif"]
    )""",
    ),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Add back the field_validator if it's not there
validator_code = '''
    @field_validator("cors_origins", "cors_allowed_origins", "allowed_hosts", "allowed_file_types", mode="before")
    @classmethod
    def parse_list_fields(cls, v):
        """Parse list fields from string or return as-is"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Handle JSON format
            if v.startswith('[') and v.endswith(']'):
                try:
                    import json
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated format
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
'''

# Find where to insert the validator (after the allowed_hosts field)
if '@field_validator("cors_origins"' not in content:
    # Find the line after allowed_hosts definition
    import_pos = content.find(
        'allowed_hosts: Union[List[str], str] = Field(default=["localhost", "127.0.0.1"])'
    )
    if import_pos != -1:
        # Find the next line
        next_line_pos = content.find("\n", import_pos) + 1
        content = content[:next_line_pos] + validator_code + content[next_line_pos:]

# Write the fixed content
with open("config/settings.py", "w") as f:
    f.write(content)

print("Settings file has been updated to handle list parsing correctly")
