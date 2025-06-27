import sys
import os
import subprocess
from datetime import datetime

sys.path.append('src')

def run_demo():
    print("Linux Device Driver Evaluation System - Demo")
    print("=" * 60)
    print(f"Demo started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Create test samples
    print("Step 1: Creating test driver samples...")
    subprocess.run([sys.executable, "create_test_suite.py"])
    print()
    
    # 2. Test individual evaluation
    print("Step 2: Evaluating individual drivers...")
    test_files = [
        ("test_samples/excellent_driver.c", "Should score 90+"),
        ("test_samples/average_driver.c", "Should score 50-70"),  
        ("test_samples/poor_driver.c", "Should score 0-30")
    ]
    
    for filename, expected in test_files:
        if os.path.exists(filename):
            print(f"\nEvaluating {filename} ({expected})")
            subprocess.run([
                sys.executable, "cli_evaluator.py", 
                "--file", filename, 
                "--model", "demo_test"
            ])
    
    # 3. Run benchmark suite
    print("\n" + "="*60)
    print("Step 3: Running AI benchmark suite...")
    subprocess.run([sys.executable, "ai_evaluation_pipeline.py", "--benchmark"])
    
    # 4. Show results
    print("\n" + "="*60)
    print("Step 4: Generated files and reports:")
    
    if os.path.exists("results"):
        for file in os.listdir("results"):
            if file.endswith(".json"):
                print(f"  - results/{file}")
    
    print("\nDemo completed successfully!")
    print("The system can now evaluate AI-generated Linux device driver code.")

if __name__ == "__main__":
    run_demo()
