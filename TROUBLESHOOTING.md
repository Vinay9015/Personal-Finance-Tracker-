# Troubleshooting Guide

## Java Version Issues

### Problem: Java 23 Compatibility Error

**Error Message:**
```
java.lang.UnsupportedOperationException: getSubject is supported only if a security manager is allowed
```

**Cause:**
Java 23 removed the Security Manager feature that Apache Spark depends on.

**Solution:**
The application has been updated to work with Java 23 by adding necessary JVM options. However, if you still encounter issues, consider these options:

#### Option 1: Use the Updated Code (Recommended)
The latest version includes Java 23 compatibility fixes. Simply pull the latest changes and run the application.

#### Option 2: Downgrade to Java 17 (Most Stable)
Java 17 LTS is the recommended version for Apache Spark:

**On macOS (using Homebrew):**
```bash
# Install Java 17
brew install openjdk@17

# Set JAVA_HOME
export JAVA_HOME=$(/usr/libexec/java_home -v 17)

# Verify
java -version
```

**On Ubuntu/Debian:**
```bash
# Install Java 17
sudo apt install openjdk-17-jdk

# Set as default
sudo update-alternatives --config java

# Verify
java -version
```

**On Windows:**
1. Download Java 17 from [Adoptium](https://adoptium.net/)
2. Install and set JAVA_HOME environment variable
3. Verify with `java -version`

#### Option 3: Use Java 11 LTS
```bash
# macOS
brew install openjdk@11
export JAVA_HOME=$(/usr/libexec/java_home -v 11)

# Ubuntu/Debian
sudo apt install openjdk-11-jdk
```

### Checking Your Java Version

```bash
java -version
```

**Recommended versions:**
- Java 17 LTS (Best compatibility)
- Java 11 LTS (Also works well)
- Java 8 (Older but stable)

**Supported with workarounds:**
- Java 21+ (May require additional configuration)
- Java 23 (Works with our updated configuration)

## PySpark Installation Issues

### Problem: PySpark fails to install

**Solution:**
```bash
# Ensure you have the latest pip
pip install --upgrade pip

# Install PySpark with specific version
pip install pyspark==3.5.0

# If still failing, try:
pip install pyspark==3.4.1
```

### Problem: "No module named pyspark"

**Solution:**
Make sure you're using the correct Python environment:
```bash
# Activate your virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall requirements
pip install -r requirements.txt
```

## Matplotlib Issues

### Problem: Matplotlib backend errors

**Solution:**
The application uses the 'Agg' backend (non-interactive) by default. If you encounter issues:

```python
# In src/visualizer.py, the backend is already set:
import matplotlib
matplotlib.use('Agg')
```

### Problem: Can't save visualizations

**Solution:**
Ensure the visualizations directory is writable:
```bash
mkdir -p visualizations
chmod 755 visualizations
```

## Data Storage Issues

### Problem: Permission denied when saving data

**Solution:**
```bash
# Create data directories with proper permissions
mkdir -p data/transactions
mkdir -p exports
mkdir -p visualizations

chmod 755 data exports visualizations
```

### Problem: Parquet files corrupted

**Solution:**
```bash
# Backup existing data
cp -r data/transactions data/transactions.backup

# Remove corrupted files
rm -rf data/transactions/*

# Restart the application (it will create a fresh database)
python main.py
```

## Memory Issues

### Problem: Java heap space errors

**Solution:**
Edit `src/spark_backend.py` and increase memory:

```python
.config("spark.driver.memory", "4g")  # Increase from 2g to 4g
```

### Problem: Application runs slowly with large datasets

**Solution:**
```python
# In spark_backend.py, add these configurations:
.config("spark.sql.shuffle.partitions", "8")
.config("spark.default.parallelism", "4")
```

## Common Runtime Errors

### Problem: Transaction ID not found when removing

**Cause:**
The ID shown is truncated (shows first 8 characters + "...")

**Solution:**
When listing transactions, copy the full ID from the data file or use search first:
```bash
# In Python code, you can get full ID:
df = backend.get_all_transactions()
df.select("transaction_id").show(truncate=False)
```

### Problem: CSV export creates empty files

**Cause:**
No data matches the filter criteria

**Solution:**
1. Check if you have any transactions: Choose option 3 (List Transactions)
2. Verify the date range or category name is correct
3. Try exporting all transactions first (option 1 in export menu)

## Platform-Specific Issues

### macOS: "xcrun: error: invalid active developer path"

**Solution:**
```bash
xcode-select --install
```

### Windows: "Access denied" errors

**Solution:**
Run Command Prompt as Administrator or adjust folder permissions

### Linux: libpython errors

**Solution:**
```bash
# Install Python development headers
sudo apt-get install python3-dev

# Or on Fedora/RHEL
sudo dnf install python3-devel
```

## Getting Help

If you encounter issues not covered here:

1. Check the error message carefully
2. Verify all prerequisites are installed
3. Try running with verbose logging:
   ```python
   # In main.py, change:
   backend.spark.sparkContext.setLogLevel("INFO")  # or "DEBUG"
   ```
4. Open an issue on GitHub with:
   - Your Java version (`java -version`)
   - Your Python version (`python --version`)
   - Your OS and version
   - Complete error message
   - Steps to reproduce

## Quick Diagnostic Script

Save this as `check_environment.py` and run it:

```python
#!/usr/bin/env python3
import sys
import subprocess

print("=== Environment Check ===\n")

# Python version
print(f"Python: {sys.version}")

# Java version
try:
    java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
    print(f"\nJava: {java_version.decode()}")
except:
    print("\n⚠ Java not found!")

# Check required packages
packages = ['pyspark', 'pandas', 'matplotlib', 'tabulate', 'colorama']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✓ {pkg} installed")
    except ImportError:
        print(f"✗ {pkg} NOT installed")
```

Run with: `python check_environment.py`
