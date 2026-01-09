#!/usr/bin/env python3
"""
Odoo XML-RPC Client Helper
"""

import xmlrpc.client
import configparser
import sys
from pathlib import Path


class OdooClient:
    """Odoo XML-RPC Client với helper methods"""

    def __init__(self, config_file='config.ini'):
        """Initialize client from config file"""
        self.config = self._load_config(config_file)

        self.url = self.config['odoo']['url']
        self.db = self.config['odoo']['database']
        self.username = self.config['odoo']['username']
        self.password = self.config['odoo']['password']

        self.common = None
        self.uid = None
        self.models = None

    def _load_config(self, config_file):
        """Load configuration from ini file"""
        config_path = Path(__file__).parent.parent / config_file

        if not config_path.exists():
            print(f"❌ Config file not found: {config_path}")
            print(f"   Please copy config.example.ini to config.ini and update settings")
            sys.exit(1)

        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def connect(self):
        """Connect to Odoo"""
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if not self.uid:
                print(f"❌ Authentication failed")
                print(f"   URL: {self.url}")
                print(f"   Database: {self.db}")
                print(f"   Username: {self.username}")
                sys.exit(1)

            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

            print(f"✅ Connected to Odoo")
            print(f"   URL: {self.url}")
            print(f"   Database: {self.db}")
            print(f"   User: {self.username} (uid={self.uid})")
            print()

            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print(f"   Make sure Odoo is running at {self.url}")
            sys.exit(1)

    def search(self, model, domain, fields=None, limit=None):
        """Search records"""
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if limit:
            kwargs['limit'] = limit

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_read',
            [domain],
            kwargs
        )

    def create(self, model, values):
        """Create record"""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'create',
            [values]
        )

    def write(self, model, ids, values):
        """Update records"""
        if not isinstance(ids, list):
            ids = [ids]

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'write',
            [ids, values]
        )

    def unlink(self, model, ids):
        """Delete records"""
        if not isinstance(ids, list):
            ids = [ids]

        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'unlink',
            [ids]
        )

    def search_count(self, model, domain):
        """Count records"""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_count',
            [domain]
        )

    def execute(self, model, method, *args, **kwargs):
        """Execute custom method"""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method,
            args,
            kwargs
        )

    def get_or_create(self, model, domain, values, skip_existing=True):
        """Get existing record or create new one"""
        existing = self.search(model, domain, limit=1)

        if existing:
            if skip_existing:
                return existing[0]['id'], False  # id, created
            else:
                # Update existing
                self.write(model, existing[0]['id'], values)
                return existing[0]['id'], False
        else:
            # Create new
            new_id = self.create(model, values)
            return new_id, True  # id, created


if __name__ == '__main__':
    # Test connection
    client = OdooClient()
    client.connect()

    # Test search
    print("Testing search...")
    users = client.search('res.users', [('id', '=', client.uid)], fields=['name', 'login'])
    print(f"Current user: {users[0]['name']} ({users[0]['login']})")

    print("\n✅ Client test successful!")
