#!/usr/bin/env python3
"""Check pytest test collection"""
import subprocess
import sys

def check_test_collection():
    """Run pytest collection and report results."""
    try:
        # Run pytest collection only
        result = subprocess.run(
            ['python', '-m', 'pytest', '--collect-only', '-q'],
            capture_output=True,
            text=True,
            cwd='/home/omar/Documents/ruleIQ'
        )
        
        output = result.stdout + result.stderr
        
        # Look for test collection count
        lines = output.strip().split('\n')
        for line in lines:
            if 'tests collected' in line.lower() or 'test collected' in line.lower():
                print(f"Test collection result: {line}")
                # Extract number
                import re
                match = re.search(r'(\d+)\s+test', line.lower())
                if match:
                    count = int(match.group(1))
                    print(f"\n✓ Successfully collecting {count} tests")
                    if count >= 2610:
                        print("🎉 Target reached! All 2,610 tests are now collecting!")
                    else:
                        print(f"⚠️ Still need to fix {2610 - count} more tests")
                    return count
        
        # If we couldn't find the count in expected format, show full output
        print("Full pytest collection output:")
        print(output)
        
        # Try alternative parsing
        if 'error' in output.lower() or 'failed' in output.lower():
            print("\n❌ There are still errors preventing test collection")
            # Show first few errors
            error_lines = [l for l in lines if 'error' in l.lower() or 'import' in l.lower()][:10]
            if error_lines:
                print("\nFirst few errors:")
                for line in error_lines:
                    print(f"  {line}")
            return 0
            
    except Exception as e:
        print(f"Error running pytest: {e}")
        return 0

if __name__ == "__main__":
    count = check_test_collection()
    sys.exit(0 if count >= 2610 else 1)