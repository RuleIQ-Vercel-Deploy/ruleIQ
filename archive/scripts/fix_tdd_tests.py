#!/usr/bin/env python3
"""
Fix TDD tests that were written expecting NameError but now need to test actual functionality.
"""
import re
import logging
logger = logging.getLogger(__name__)

def fix_test_file(filepath):
    """Fix all pytest.raises(NameError) patterns in the test file."""

    with open(filepath, "r") as f:
        content = f.read()

    # Count occurrences
    pattern = r"with pytest\.raises\(NameError\):"
    matches = re.findall(pattern, content)
    logger.info(f"Found {len(matches)} occurrences of pytest.raises(NameError)")

    # Remove the pytest.raises(NameError) blocks and unindent the code inside
    lines = content.split("\n")
    new_lines = []
    skip_next = False
    inside_raises_block = False

    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue

        if "with pytest.raises(NameError):" in line:
            inside_raises_block = True
            # Skip this line and the next (which might be a comment)
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("#"):
                skip_next = True
            continue
        elif inside_raises_block and line and not line[0].isspace():
            # We've exited the indented block
            inside_raises_block = False
            new_lines.append(line)
        elif inside_raises_block and line.strip():
            # Unindent the line (remove 4 spaces)
            if line.startswith("            "):
                new_lines.append(line[4:])
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Write back
    with open(filepath, "w") as f:
        f.write("\n".join(new_lines))

    logger.info(f"Fixed {filepath}")

if __name__ == "__main__":
    fix_test_file("tests/models/test_compliance_state.py")
    logger.info("Done!")
