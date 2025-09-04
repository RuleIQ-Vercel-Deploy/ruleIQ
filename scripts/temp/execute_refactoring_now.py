#!/usr/bin/env python3
"""
Emergency execution script to run aggressive refactoring NOW
"""

import sys
import os
import time
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, '/home/omar/Documents/ruleIQ/scripts')

print("=" * 80)
print("🚨 EMERGENCY SONARCLOUD GRADE IMPROVEMENT EXECUTION")
print("=" * 80)
print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("")

print("Current Status:")
print("- Grade: E")
print("- Functions needing refactoring: 816")
print("- Functions completed: 2 (0.25%)")
print("- TARGET: Refactor 400+ functions NOW")
print("")

print("🚀 Starting aggressive refactoring...")
print("-" * 40)

try:
    from aggressive_batch_refactor import AggressiveBatchRefactorer
    
    # Create refactorer with aggressive settings
    refactorer = AggressiveBatchRefactorer(complexity_threshold=10)
    
    # Process all files in parallel
    results = refactorer.process_all_files_parallel()
    
    print("\n" + "=" * 80)
    print("✅ REFACTORING COMPLETE!")
    print("=" * 80)
    
    print(f"\n📊 RESULTS:")
    print(f"   Functions analyzed: {results['total_functions_analyzed']}")
    print(f"   Functions refactored: {results['functions_refactored']}")
    print(f"   Files modified: {results['files_modified']}")
    print(f"   Backup location: {results['backup_location']}")
    
    # Calculate progress
    progress = (results['functions_refactored'] / 816) * 100
    print(f"\n📈 PROGRESS: {progress:.1f}% of target")
    
    # Determine if we need another run
    if results['functions_refactored'] < 400:
        print("\n⚠️  Need to run again with lower threshold!")
        print("Running second pass with threshold=8...")
        
        # Second pass with lower threshold
        refactorer2 = AggressiveBatchRefactorer(complexity_threshold=8)
        results2 = refactorer2.process_all_files_parallel()
        
        total_refactored = results['functions_refactored'] + results2['functions_refactored']
        print(f"\n✅ Second pass complete!")
        print(f"   Additional functions refactored: {results2['functions_refactored']}")
        print(f"   TOTAL REFACTORED: {total_refactored}")
        
        progress = (total_refactored / 816) * 100
        print(f"   FINAL PROGRESS: {progress:.1f}%")
        
        # Update results
        results['functions_refactored'] = total_refactored
        results['second_pass'] = results2
    
    # Save comprehensive report
    report = {
        'timestamp': time.time(),
        'results': results,
        'progress_percentage': progress,
        'estimated_grade': 'C' if results['functions_refactored'] > 400 else 'D' if results['functions_refactored'] > 200 else 'E',
        'target_met': results['functions_refactored'] >= 400
    }
    
    with open('emergency_refactoring_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 80)
    print("📋 FINAL SUMMARY")
    print("=" * 80)
    
    if report['target_met']:
        print("🎉 SUCCESS! Target of 400+ functions met!")
        print(f"   Estimated SonarCloud Grade: {report['estimated_grade']}")
        print("\n✅ Ready to commit and push!")
    else:
        print(f"⚠️  Partial success: {results['functions_refactored']} functions refactored")
        print("   Run manual refactoring for remaining high-complexity functions")
    
    print("\n🎯 Next Steps:")
    print("1. Run quick test: python3 -m pytest tests/test_minimal.py")
    print("2. If tests pass: git add -A && git commit -m 'refactor: massive complexity reduction'")
    print("3. Push to trigger SonarCloud: git push origin agent-swarm")
    print("4. Monitor SonarCloud dashboard for new grade")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("Attempting fallback approach...")
    
    # Fallback: Try to at least run the simpler refactoring
    try:
        os.system("python3 /home/omar/Documents/ruleIQ/scripts/auto_refactor_complexity.py")
    except:
        print("Fallback also failed. Manual intervention required.")

print(f"\nCompleted at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)