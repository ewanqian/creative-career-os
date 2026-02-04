#!/usr/bin/env python3
"""
Knowledge Block Manager for Creative-Career-OS

This tool manages knowledge blocks with version control, search, and indexing capabilities.
"""

import json
import os
import re
import datetime
import hashlib
import argparse
from typing import List, Dict, Any, Optional

class KnowledgeBlockManager:
    def __init__(self, data_dir: str = "../knowledge_blocks"):
        """Initialize the knowledge block manager."""
        self.data_dir = os.path.abspath(data_dir)
        self.schema_path = os.path.join(os.path.dirname(__file__), "schema.json")
        self._ensure_dirs()
        self._load_schema()
    
    def _ensure_dirs(self):
        """Ensure necessary directories exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Create domain directories
        domains = ["defense", "proactive", "mindset", "efficiency", "relationship"]
        for domain in domains:
            domain_dir = os.path.join(self.data_dir, domain)
            if not os.path.exists(domain_dir):
                os.makedirs(domain_dir)
    
    def _load_schema(self):
        """Load the knowledge block schema."""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
    
    def generate_id(self, title: str) -> str:
        """Generate a unique ID for a knowledge block."""
        # Create a hash based on title and timestamp
        timestamp = datetime.datetime.now().isoformat()
        combined = f"{title}_{timestamp}"
        hash_obj = hashlib.md5(combined.encode('utf-8'))
        short_hash = hash_obj.hexdigest()[:8]
        
        # Create a slug from title
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        slug = slug[:30]  # Limit length
        
        return f"{slug}_{short_hash}"
    
    def create_block(self, block_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new knowledge block."""
        # Generate ID if not provided
        if 'id' not in block_data:
            block_data['id'] = self.generate_id(block_data['title'])
        
        # Add timestamps
        now = datetime.datetime.now().isoformat()
        if 'created_at' not in block_data:
            block_data['created_at'] = now
        block_data['updated_at'] = now
        
        # Set default values
        if 'version' not in block_data:
            block_data['version'] = "1.0"
        if 'usage_count' not in block_data:
            block_data['usage_count'] = 0
        if 'rating' not in block_data:
            block_data['rating'] = 0.0
        if 'feedback' not in block_data:
            block_data['feedback'] = []
        if 'variations' not in block_data:
            block_data['variations'] = []
        if 'examples' not in block_data:
            block_data['examples'] = []
        if 'tags' not in block_data:
            block_data['tags'] = []
        if 'related_blocks' not in block_data:
            block_data['related_blocks'] = []
        
        # Validate against schema
        self._validate_block(block_data)
        
        # Save the block
        self._save_block(block_data)
        
        return block_data
    
    def _validate_block(self, block_data: Dict[str, Any]):
        """Validate a knowledge block against the schema."""
        # Check required fields
        required_fields = self.schema['required']
        for field in required_fields:
            if field not in block_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check field types
        properties = self.schema['properties']
        for field, props in properties.items():
            if field in block_data:
                value = block_data[field]
                if 'type' in props:
                    expected_type = props['type']
                    if expected_type == 'string' and not isinstance(value, str):
                        raise ValueError(f"Field {field} should be a string")
                    elif expected_type == 'number' and not isinstance(value, (int, float)):
                        raise ValueError(f"Field {field} should be a number")
                    elif expected_type == 'integer' and not isinstance(value, int):
                        raise ValueError(f"Field {field} should be an integer")
                    elif expected_type == 'boolean' and not isinstance(value, bool):
                        raise ValueError(f"Field {field} should be a boolean")
                    elif expected_type == 'array' and not isinstance(value, list):
                        raise ValueError(f"Field {field} should be an array")
                    elif expected_type == 'object' and not isinstance(value, dict):
                        raise ValueError(f"Field {field} should be an object")
    
    def _save_block(self, block_data: Dict[str, Any]):
        """Save a knowledge block to disk."""
        domain = block_data['domain']
        block_id = block_data['id']
        file_path = os.path.join(self.data_dir, domain, f"{block_id}.json")
        
        # Save the block
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(block_data, f, ensure_ascii=False, indent=2)
    
    def get_block(self, block_id: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a knowledge block by ID."""
        if domain:
            file_path = os.path.join(self.data_dir, domain, f"{block_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        else:
            # Search all domains
            domains = ["defense", "proactive", "mindset", "efficiency", "relationship"]
            for domain in domains:
                file_path = os.path.join(self.data_dir, domain, f"{block_id}.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
        return None
    
    def update_block(self, block_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a knowledge block."""
        # Find the block
        block = self.get_block(block_id)
        if not block:
            return None
        
        # Update fields
        block.update(updates)
        block['updated_at'] = datetime.datetime.now().isoformat()
        
        # Increment version
        if 'version' in block:
            major, minor = map(int, block['version'].split('.'))
            block['version'] = f"{major}.{minor + 1}"
        
        # Validate and save
        self._validate_block(block)
        self._save_block(block)
        
        return block
    
    def delete_block(self, block_id: str) -> bool:
        """Delete a knowledge block."""
        # Find the block
        block = self.get_block(block_id)
        if not block:
            return False
        
        # Delete the file
        domain = block['domain']
        file_path = os.path.join(self.data_dir, domain, f"{block_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def search_blocks(self, query: str, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search knowledge blocks."""
        results = []
        search_terms = query.lower().split()
        
        if domain:
            domains = [domain]
        else:
            domains = ["defense", "proactive", "mindset", "efficiency", "relationship"]
        
        for domain in domains:
            domain_dir = os.path.join(self.data_dir, domain)
            if not os.path.exists(domain_dir):
                continue
            
            for filename in os.listdir(domain_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(domain_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        block = json.load(f)
                    except json.JSONDecodeError:
                        continue
                
                # Search in title, content, tags
                search_text = f"{block.get('title', '').lower()} {block.get('content', '').lower()} {' '.join(block.get('tags', []))}"
                
                # Check if all search terms are present
                if all(term in search_text for term in search_terms):
                    results.append(block)
        
        return results
    
    def get_blocks_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all knowledge blocks in a domain."""
        results = []
        domain_dir = os.path.join(self.data_dir, domain)
        
        if not os.path.exists(domain_dir):
            return results
        
        for filename in os.listdir(domain_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(domain_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    block = json.load(f)
                    results.append(block)
                except json.JSONDecodeError:
                    continue
        
        return results
    
    def add_feedback(self, block_id: str, feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add feedback to a knowledge block."""
        block = self.get_block(block_id)
        if not block:
            return None
        
        # Add feedback
        feedback_id = self.generate_id(f"feedback_{block_id}")
        feedback['id'] = feedback_id
        feedback['date'] = datetime.datetime.now().isoformat()
        
        if 'feedback' not in block:
            block['feedback'] = []
        block['feedback'].append(feedback)
        
        # Update rating
        ratings = [f['rating'] for f in block['feedback'] if 'rating' in f]
        if ratings:
            block['rating'] = sum(ratings) / len(ratings)
        
        # Save updated block
        self._save_block(block)
        return block
    
    def increment_usage(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Increment usage count for a knowledge block."""
        block = self.get_block(block_id)
        if not block:
            return None
        
        block['usage_count'] = block.get('usage_count', 0) + 1
        self._save_block(block)
        return block
    
    def export_blocks(self, format: str = 'json') -> str:
        """Export all knowledge blocks."""
        all_blocks = []
        domains = ["defense", "proactive", "mindset", "efficiency", "relationship"]
        
        for domain in domains:
            domain_dir = os.path.join(self.data_dir, domain)
            if not os.path.exists(domain_dir):
                continue
            
            for filename in os.listdir(domain_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(domain_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        block = json.load(f)
                        all_blocks.append(block)
                    except json.JSONDecodeError:
                        continue
        
        if format == 'json':
            return json.dumps(all_blocks, ensure_ascii=False, indent=2)
        elif format == 'markdown':
            # Generate markdown
            markdown = "# Creative-Career-OS Knowledge Blocks\n\n"
            for block in all_blocks:
                markdown += f"## {block.get('title', 'Untitled')}\n"
                markdown += f"ID: {block.get('id', 'N/A')}\n"
                markdown += f"Domain: {block.get('domain', 'N/A')}\n"
                markdown += f"Type: {block.get('type', 'N/A')}\n"
                markdown += f"Rating: {block.get('rating', 'N/A')}\n"
                markdown += f"Usage: {block.get('usage_count', 0)}\n\n"
                markdown += f"{block.get('content', 'No content')}\n\n"
                markdown += "---\n\n"
            return markdown
        else:
            raise ValueError(f"Unsupported format: {format}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Knowledge Block Manager for Creative-Career-OS")
    parser.add_argument('command', choices=['create', 'get', 'update', 'delete', 'search', 'list', 'export'],
                        help='Command to execute')
    parser.add_argument('--title', help='Title for creating a block')
    parser.add_argument('--domain', choices=['defense', 'proactive', 'mindset', 'efficiency', 'relationship'],
                        help='Domain for the block')
    parser.add_argument('--type', choices=['case', 'module', 'guide', 'tool', 'case_study'],
                        help='Type of the block')
    parser.add_argument('--content', help='Content for the block')
    parser.add_argument('--id', help='Block ID for get/update/delete')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json',
                        help='Format for export')
    
    args = parser.parse_args()
    manager = KnowledgeBlockManager()
    
    if args.command == 'create':
        if not all([args.title, args.domain, args.type, args.content]):
            parser.error('Create command requires --title, --domain, --type, and --content')
        
        block_data = {
            'title': args.title,
            'domain': args.domain,
            'type': args.type,
            'content': args.content
        }
        block = manager.create_block(block_data)
        print(f"Created block: {block['id']}")
        print(json.dumps(block, ensure_ascii=False, indent=2))
    
    elif args.command == 'get':
        if not args.id:
            parser.error('Get command requires --id')
        block = manager.get_block(args.id)
        if block:
            print(json.dumps(block, ensure_ascii=False, indent=2))
        else:
            print(f"Block not found: {args.id}")
    
    elif args.command == 'update':
        if not args.id:
            parser.error('Update command requires --id')
        # For simplicity, we'll just increment usage for now
        block = manager.increment_usage(args.id)
        if block:
            print(f"Updated block: {args.id}")
            print(json.dumps(block, ensure_ascii=False, indent=2))
        else:
            print(f"Block not found: {args.id}")
    
    elif args.command == 'delete':
        if not args.id:
            parser.error('Delete command requires --id')
        success = manager.delete_block(args.id)
        if success:
            print(f"Deleted block: {args.id}")
        else:
            print(f"Block not found: {args.id}")
    
    elif args.command == 'search':
        if not args.query:
            parser.error('Search command requires --query')
        results = manager.search_blocks(args.query, args.domain)
        print(f"Found {len(results)} results:")
        for block in results:
            print(f"- {block.get('title', 'Untitled')} (ID: {block.get('id', 'N/A')})")
    
    elif args.command == 'list':
        blocks = manager.get_blocks_by_domain(args.domain)
        print(f"Blocks in {args.domain}:")
        for block in blocks:
            print(f"- {block.get('title', 'Untitled')} (ID: {block.get('id', 'N/A')})")
    
    elif args.command == 'export':
        export_data = manager.export_blocks(args.format)
        print(export_data)
