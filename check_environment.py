#!/usr/bin/env python3
"""
Environment Check Script
Verifies that all prerequisites are installed correctly
"""

import sys
import subprocess
import platform


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def check_python():
    """Check Python version"""
    print("Python Version:")
    print(f"  {sys.version}")

    version_info = sys.version_info
    if version_info >= (3, 8):
        print("  ✓ Python version is compatible (3.8+)")
    else:
        print("  ✗ Python version is too old (need 3.8+)")
        return False
    return True


def check_java():
    """Check Java installation and version"""
    print("\nJava Version:")
    try:
        result = subprocess.run(
            ['java', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Java version output goes to stderr
        output = result.stderr if result.stderr else result.stdout
        print(f"  {output.strip()}")

        # Parse version
        if 'version "1.8' in output or 'version "8' in output:
            print("  ✓ Java 8 detected (compatible)")
        elif 'version "11' in output:
            print("  ✓ Java 11 LTS detected (compatible)")
        elif 'version "17' in output:
            print("  ✓ Java 17 LTS detected (recommended)")
        elif 'version "21' in output:
            print("  ⚠ Java 21 detected (may need compatibility fixes)")
        elif 'version "23' in output:
            print("  ⚠ Java 23 detected (compatibility fixes included)")
        else:
            print("  ⚠ Java version detected but compatibility unknown")

        return True
    except FileNotFoundError:
        print("  ✗ Java not found!")
        print("  Please install Java 17 LTS")
        print("  Download from: https://adoptium.net/")
        return False
    except subprocess.TimeoutExpired:
        print("  ✗ Java check timed out")
        return False
    except Exception as e:
        print(f"  ✗ Error checking Java: {e}")
        return False


def check_packages():
    """Check required Python packages"""
    print("\nRequired Python Packages:")

    packages = {
        'pyspark': 'Apache Spark for Python',
        'pandas': 'Data manipulation',
        'matplotlib': 'Data visualization',
        'tabulate': 'Table formatting',
        'colorama': 'Colored terminal output',
        'dateutil': 'Date utilities'
    }

    all_installed = True
    for pkg, description in packages.items():
        try:
            if pkg == 'dateutil':
                __import__('dateutil')
            else:
                __import__(pkg)
            print(f"  ✓ {pkg:12} - {description}")
        except ImportError:
            print(f"  ✗ {pkg:12} - {description} (NOT INSTALLED)")
            all_installed = False

    if not all_installed:
        print("\n  Install missing packages with:")
        print("  pip install -r requirements.txt")

    return all_installed


def check_system():
    """Check system information"""
    print("\nSystem Information:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Processor: {platform.processor()}")


def check_spark_connection():
    """Try to initialize Spark"""
    print("\nSpark Connection Test:")
    try:
        from pyspark.sql import SparkSession
        print("  Initializing Spark session...")

        spark = SparkSession.builder \
            .appName("EnvironmentTest") \
            .config("spark.driver.memory", "1g") \
            .getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")

        # Create a simple test DataFrame
        test_data = [("test", 1), ("data", 2)]
        df = spark.createDataFrame(test_data, ["col1", "col2"])
        count = df.count()

        spark.stop()

        print(f"  ✓ Spark initialized successfully!")
        print(f"  ✓ Test DataFrame created with {count} rows")
        return True
    except Exception as e:
        print(f"  ✗ Failed to initialize Spark: {e}")
        print("\n  This is likely a Java compatibility issue.")
        print("  See TROUBLESHOOTING.md for solutions.")
        return False


def main():
    """Run all checks"""
    print_header("PERSONAL FINANCE TRACKER - ENVIRONMENT CHECK")

    results = {
        'python': check_python(),
        'java': check_java(),
        'packages': check_packages(),
    }

    check_system()

    # Only test Spark if other checks passed
    if all(results.values()):
        results['spark'] = check_spark_connection()
    else:
        print("\n⚠ Skipping Spark test due to failed prerequisites")
        results['spark'] = False

    # Summary
    print_header("SUMMARY")

    passed = sum(results.values())
    total = len(results)

    for component, status in results.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"  {component.capitalize():12} - {status_str}")

    print(f"\n  Result: {passed}/{total} checks passed")

    if passed == total:
        print("\n  🎉 All checks passed! You're ready to use the application.")
        print("  Run: python main.py")
    else:
        print("\n  ⚠ Some checks failed. Please review the errors above.")
        print("  See TROUBLESHOOTING.md for help.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
