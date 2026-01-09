#!/usr/bin/env python3
"""
Setup Product Categories với AVCO (Average Cost)

Cấu trúc:
- DTX Products (root)
  - DTX Hardware (AVCO)
    - DTX Components (AVCO)
    - DTX Finished Products (AVCO)
    - DTX Accessories (AVCO)
  - DTX Services
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.odoo_client import OdooClient


def setup_categories(client, skip_existing=True):
    """Setup product categories with AVCO costing"""

    print("=" * 80)
    print("SETUP PRODUCT CATEGORIES (WITH AVCO)")
    print("=" * 80)
    print()

    # Category structure
    categories = [
        # Root
        {
            'name': 'DTX Products',
            'parent_id': None,
            'property_cost_method': 'average',  # AVCO
        },
        # Hardware (level 1)
        {
            'name': 'DTX Hardware',
            'parent_name': 'DTX Products',
            'property_cost_method': 'average',  # AVCO
        },
        # Components (level 2)
        {
            'name': 'DTX Components',
            'parent_name': 'DTX Hardware',
            'property_cost_method': 'average',  # AVCO
        },
        # Finished Products (level 2)
        {
            'name': 'DTX Finished Products',
            'parent_name': 'DTX Hardware',
            'property_cost_method': 'average',  # AVCO
        },
        # Accessories (level 2)
        {
            'name': 'DTX Accessories',
            'parent_name': 'DTX Hardware',
            'property_cost_method': 'average',  # AVCO
        },
        # Services (level 1)
        {
            'name': 'DTX Services',
            'parent_name': 'DTX Products',
            'property_cost_method': 'standard',  # Services không cần AVCO
        },
    ]

    created_count = 0
    skipped_count = 0
    category_cache = {}  # Cache để lưu parent_id

    for cat_data in categories:
        name = cat_data['name']
        parent_name = cat_data.pop('parent_name', None)

        # Get parent_id if needed
        if parent_name:
            if parent_name in category_cache:
                parent_id = category_cache[parent_name]
            else:
                parent = client.search('product.category', [('name', '=', parent_name)], limit=1)
                if parent:
                    parent_id = parent[0]['id']
                    category_cache[parent_name] = parent_id
                else:
                    print(f"⚠️  Warning: Parent '{parent_name}' not found for '{name}', skipping...")
                    continue

            cat_data['parent_id'] = parent_id

        # Check if exists
        domain = [('name', '=', name)]
        if parent_name:
            domain.append(('parent_id', '=', parent_id))

        cat_id, created = client.get_or_create(
            'product.category',
            domain,
            cat_data,
            skip_existing=skip_existing
        )

        # Cache this category
        category_cache[name] = cat_id

        if created:
            method = cat_data.get('property_cost_method', 'standard')
            print(f"✅ Created: {name} (Costing: {method.upper()})")
            created_count += 1
        else:
            print(f"⏭️  Skipped: {name} (already exists)")
            skipped_count += 1

    print()
    print("=" * 80)
    print(f"SUMMARY: {created_count} created, {skipped_count} skipped")
    print("=" * 80)
    print()

    return created_count, skipped_count


if __name__ == '__main__':
    client = OdooClient()
    client.connect()

    skip_existing = client.config.getboolean('setup', 'skip_existing', fallback=True)

    setup_categories(client, skip_existing=skip_existing)

    print("✅ Product category setup completed!")
