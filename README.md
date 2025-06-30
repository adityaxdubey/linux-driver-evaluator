# Linux Driver Code Evaluation System

A command-line tool designed to evaluate the quality of Linux device driver code. It uses a multi-layered approach, combining professional static analysis with semantic checks to provide a comprehensive quality score.

This system is particularly useful for benchmarking AI-generated code, but can be used to assess any C-based kernel module.

## Key Features

- **Professional Static Analysis**: Integrates Clang-Tidy to find bugs, style violations, and performance issues using industry-standard checks.
- **Runtime Compilation Testing**: Verifies that the driver code actually compiles as a kernel module.
- **Security Vulnerability Scanning**: Identifies common security anti-patterns and potential vulnerabilities.
- **Runtime**: Measures real execution time and can detect memory leaks or misuse (optionally with `valgrind`).
- **Performance & Complexity Analysis**: Analyzes code for nested loops, complex functions, and inefficient patterns.
- **AI Model Benchmarking**: A built-in pipeline to generate code from AI models (Gemini, OpenAI, or a mock) and evaluate it automatically.
- **Unified Command-Line Interface**: A single, clean entry point (`main.py`) for all functionality.

## Installation

1.  **Clone the repository**
    ```
    git clone https://github.com/adityaxdubey/linux-driver-evaluator.git
    cd linux-driver-evaluator
    ```

2.  **Set up Python environment**
    ```
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up Clang-Tidy**
    This script will check if `clang-tidy` is installed and offer to install it if missing. This may require `sudo`.
    ```
    python setup_clang.py
    ```

## Usage

The primary entry point is `main.py`, which has two main commands: `evaluate` and `ai-benchmark`.

#### 1. Evaluate a Local Driver File

To run a comprehensive evaluation on a driver file you have locally:
```
python main.py evaluate test_driver.c --kernel-headers /usr/src/linux-headers-$(uname -r)
```
To see a more detailed, line-by-line report:
python main.py evaluate test_driver.c --detailed

#### 2. Run an AI Benchmark

To generate code from an AI model and immediately evaluate it, use the `ai-benchmark` command.

**Using the Mock AI (for testing, no API key needed):**
```
python main.py ai-benchmark --model mock
```

**Using Google Gemini:**
It's best to set your API key as an environment variable
export GEMINI_API_KEY="your-api-key-here"
```
python main.py ai-benchmark --model gemini
```

the web interface is included in your project as web_dashboard.py. While it is not integrated into the main CLI (main.py), it serves as a separate optional front-end to interact with your evaluation system through a browser.

## Technical Approach

The system uses a modular architecture with several distinct analysis stages:

1.  **Clang-Tidy Analysis**: Provides the primary static analysis score, checking against a curated list of rules relevant to kernel development.
2.  **Runtime Compilation**: A simple `make` process is simulated to ensure the code is buildable as a kernel module. This is a pass/fail check.
3.  **Security Scan**: A custom regex-based scanner looks for common C-language vulnerabilities (e.g., unsafe string functions).
4.  **Performance Profiling**: The code is scanned for patterns that indicate performance issues, like deeply nested loops.

These individual results are combined into a final, weighted score. This ensures that critical issues like compilation failures and security vulnerabilities have a higher impact on the final score than minor style issues.

For a detailed breakdown of how AI was used as a learning and development accelerator, please see the `AI_Usage.md` file.
