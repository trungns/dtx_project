#!/usr/bin/env python3
"""
Verify DTX Product Types (x_dtx_type field)

4 loại:
- device_serial: Thiết bị quản lý theo Serial
- component: Linh kiện / vật tư tiêu hao
- kiosk: Kiosk / Thiết bị hoàn chỉnh
- service: Dịch vụ

Note: Field này được tạo bởi module dtx_product_standards
Script này chỉ verify và hướng dẫn
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.odoo_client import OdooClient


def verify_dtx_product_types(client):
    """Verify DTX product types field exists"""

    print("=" * 80)
    print("VERIFY DTX PRODUCT TYPES")
    print("=" * 80)
    print()

    print("Checking if module dtx_product_standards is installed...")

    try:
        # Try to search products with x_dtx_type field
        products = client.search(
            'product.template',
            [],
            fields=['name', 'x_dtx_type'],
            limit=1
        )

        print("✅ Module dtx_product_standards is installed")
        print("✅ Field x_dtx_type is available")
        print()

        # Show 4 DTX types
        print("=" * 80)
        print("4 DTX PRODUCT TYPES:")
        print("=" * 80)
        print()

        types = [
            {
                'value': 'device_serial',
                'name': 'Thiết bị quản lý theo Serial',
                'description': 'Touch screen, Mini PC, Máy in, Camera, etc.',
                'config': [
                    'Product Type: Storable Product',
                    'Tracking: By Unique Serial Number',
                    'Category Costing: AVCO (Average Cost)',
                    'Can be Purchased: ✓',
                    'Can be Sold: ✓',
                ]
            },
            {
                'value': 'component',
                'name': 'Linh kiện / vật tư tiêu hao',
                'description': 'Cáp mạng, Vít ốc, Dây điện, USB cable, etc.',
                'config': [
                    'Product Type: Storable Product',
                    'Tracking: No Tracking (or By Lots)',
                    'Category Costing: AVCO (Average Cost)',
                    'Can be Purchased: ✓',
                    'Can be Sold: ✗ (thường không bán riêng)',
                ]
            },
            {
                'value': 'kiosk',
                'name': 'Kiosk / Thiết bị hoàn chỉnh',
                'description': 'Self-service Kiosk, Check-in Station, etc.',
                'config': [
                    'Product Type: Storable Product',
                    'Tracking: By Unique Serial Number',
                    'Category Costing: AVCO (Average Cost)',
                    'Can be Purchased: ✗ (sản xuất, không mua)',
                    'Can be Sold: ✓',
                    'Cần có BOM (Bill of Materials)',
                ]
            },
            {
                'value': 'service',
                'name': 'Dịch vụ',
                'description': 'Phí triển khai, Bảo trì, Đào tạo, etc.',
                'config': [
                    'Product Type: Service',
                    'Tracking: No Tracking',
                    'Can be Purchased: ✗',
                    'Can be Sold: ✓',
                ]
            },
        ]

        for i, ptype in enumerate(types, 1):
            print(f"{i}. {ptype['name']} (x_dtx_type = '{ptype['value']}')")
            print(f"   Ví dụ: {ptype['description']}")
            print(f"   Cấu hình khuyến nghị:")
            for config in ptype['config']:
                print(f"   - {config}")
            print()

        print("=" * 80)
        print("HƯỚNG DẪN SỬ DỤNG:")
        print("=" * 80)
        print()
        print("1. Tạo sản phẩm mới:")
        print("   Inventory > DTX – Chuẩn hóa dữ liệu > Sản phẩm DTX > Create")
        print()
        print("2. Chọn 'Loại sản phẩm DTX' (x_dtx_type)")
        print()
        print("3. Áp dụng chuẩn DTX hàng loạt:")
        print("   - Chọn nhiều sản phẩm")
        print("   - Action > 'Áp dụng chuẩn DTX'")
        print("   - Hệ thống tự động cấu hình theo loại DTX")
        print()

        # Count products by type
        print("=" * 80)
        print("CURRENT PRODUCTS BY TYPE:")
        print("=" * 80)
        print()

        for ptype in types:
            count = client.search_count('product.template', [('x_dtx_type', '=', ptype['value'])])
            print(f"{ptype['name']:40} {count:5} products")

        total = client.search_count('product.template', [])
        untyped = client.search_count('product.template', [('x_dtx_type', '=', False)])
        print(f"{'Chưa phân loại':40} {untyped:5} products")
        print(f"{'TỔNG':40} {total:5} products")
        print()

        if untyped > 0:
            print("⚠️  Lưu ý: Có sản phẩm chưa phân loại DTX type")
            print("   Hãy vào Inventory > DTX - Chuẩn hóa dữ liệu > Sản phẩm DTX")
            print("   và phân loại các sản phẩm này")
            print()

        return True

    except Exception as e:
        print("❌ Module dtx_product_standards NOT installed or field not found!")
        print(f"   Error: {e}")
        print()
        print("📝 ACTION REQUIRED:")
        print("   1. Install module: dtx_product_standards")
        print("   2. Apps > Update Apps List > Search 'DTX Product Standards' > Install")
        print("   3. Run this script again")
        print()
        return False


if __name__ == '__main__':
    client = OdooClient()
    client.connect()

    success = verify_dtx_product_types(client)

    if success:
        print("✅ DTX product types verification completed!")
    else:
        print("❌ DTX product types verification failed!")
        sys.exit(1)
