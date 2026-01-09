#!/usr/bin/env python3
"""
Run All Setup Scripts

Chạy tất cả setup scripts theo thứ tự:
1. Taxes
2. Product Categories
3. DTX Product Types (verify)
4. Payment Terms
5. Locations
"""

import sys
from pathlib import Path
import importlib.util


def run_script(script_path):
    """Run a Python script dynamically"""
    print("\n")
    print("█" * 80)
    print(f"Running: {script_path.name}")
    print("█" * 80)
    print()

    # Load module
    spec = importlib.util.spec_from_file_location("setup_module", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["setup_module"] = module

    try:
        spec.loader.exec_module(module)
        return True
    except Exception as e:
        print(f"\n❌ Error running {script_path.name}: {e}")
        return False


def main():
    """Main function"""
    scripts_dir = Path(__file__).parent / 'setup'

    # Setup scripts in order
    scripts = [
        '01_setup_taxes.py',
        '02_setup_product_categories.py',
        '03_setup_dtx_product_types.py',
        '04_setup_payment_terms.py',
        '05_setup_locations.py',
    ]

    print("=" * 80)
    print("DTX ODOO 16 - AUTO SETUP")
    print("=" * 80)
    print()
    print(f"Running {len(scripts)} setup scripts...")
    print()

    success_count = 0
    failed_count = 0

    for script_name in scripts:
        script_path = scripts_dir / script_name

        if not script_path.exists():
            print(f"❌ Script not found: {script_name}")
            failed_count += 1
            continue

        if run_script(script_path):
            success_count += 1
        else:
            failed_count += 1

    # Summary
    print("\n")
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print()
    print(f"✅ Success: {success_count}/{len(scripts)}")
    print(f"❌ Failed:  {failed_count}/{len(scripts)}")
    print()

    if failed_count == 0:
        print("🎉 ALL SETUP SCRIPTS COMPLETED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("1. Verify setup: python3 utils/verify_setup.py")
        print("2. Start using Odoo DTX modules")
        print("3. Read documentation: /PRODUCTION_DOCS/")
        print()
        return 0
    else:
        print("⚠️  Some scripts failed. Please check errors above.")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
