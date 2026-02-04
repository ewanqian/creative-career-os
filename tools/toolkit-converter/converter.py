#!/usr/bin/env python3
"""
工具包转换脚本
将现有的工具包转换为标准化的知识块格式
"""

import os
import json
import re
import datetime
import uuid
from pathlib import Path

# 工具包目录 (相对于脚本所在目录)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TOOLKITS_DIR = PROJECT_ROOT / "toolkits"
# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "knowledge_blocks"

# 领域映射
domain_map = {
    "主动": "proactive",
    "关系": "relationship",
    "合同": "defense",
    "心智": "mindset",
    "报价": "defense",
    "效率": "efficiency",
    "沟通": "defense"
}

# 类型映射
type_map = {
    "个人品牌建设": "module",
    "从执行到顾问": "guide",
    "价值定价策略": "tool",
    "内容营销策略": "module",
    "客户开发策略": "module",
    "同行网络建设": "module",
    "长期客户维护": "module",
    "付款节点设置": "tool",
    "修改次数限制": "tool",
    "著作权归属界定": "tool",
    "违约责任界定": "tool",
    "内在动力建设": "module",
    "决策框架": "tool",
    "成长型思维": "module",
    "抗压能力与职业倦怠预防": "module",
    "低价竞争应对": "tool",
    "应对无预算试探": "tool",
    "紧急项目加价": "tool",
    "工作流程标准化": "module",
    "时间管理与精力分配": "module",
    "客户拖延付款": "tool",
    "应对免费试稿": "tool",
    "项目范围蔓延": "tool"
}

def generate_id(title: str) -> str:
    """生成知识块ID"""
    # 生成基于时间戳和标题的唯一ID
    timestamp = datetime.datetime.now().timestamp()
    unique_id = str(uuid.uuid4())[:8]
    title_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:20]
    return f"{title_slug}_{unique_id}"

def parse_toolkit(file_path: Path) -> dict:
    """解析工具包文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    title_match = re.search(r'^#\s*(.+?)\s*v\d+\.\d+', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled"
    
    # 提取元信息
    meta_info = {}
    meta_match = re.search(r'## 元信息\n(- \*\*[^\*]+\*\*: .+\n)+', content, re.MULTILINE)
    if meta_match:
        meta_text = meta_match.group(0)
        for line in meta_text.split('\n'):
            if '- **' in line:
                key, value = line.split(': ', 1)
                key = key.strip('- **').strip('**')
                meta_info[key] = value.strip()
    
    # 提取核心内容
    core_content = re.sub(r'## 元信息\n(- \*\*[^\*]+\*\*: .+\n)+', '', content)
    core_content = re.sub(r'^#\s*.+?v\d+\.\d+\n\n', '', core_content)
    
    # 提取领域和类型
    domain_key = title.split('-')[0].strip()
    type_key = title.split('-')[1].strip()
    domain = domain_map.get(domain_key, "defense")
    type_ = type_map.get(type_key, "module")
    
    # 构建知识块
    block = {
        "id": generate_id(title),
        "title": title,
        "type": type_,
        "domain": domain,
        "subdomain": type_key,
        "content": core_content,
        "context": meta_info.get("适用场景", ""),
        "variations": [],
        "examples": [],
        "tags": [domain_key, type_key],
        "related_blocks": [],
        "skill_tree": {},
        "version": "1.0",
        "usage_count": 0,
        "rating": 0.0,
        "feedback": [],
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    return block

def main():
    """主函数"""
    print(f"工具包目录: {TOOLKITS_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 检查工具包目录是否存在
    if not TOOLKITS_DIR.exists():
        print(f"工具包目录不存在: {TOOLKITS_DIR}")
        return
    
    # 列出工具包文件
    toolkit_files = list(TOOLKITS_DIR.glob("*.md"))
    print(f"找到 {len(toolkit_files)} 个工具包文件")
    for file_path in toolkit_files:
        print(f"  - {file_path.name}")
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"创建输出目录: {OUTPUT_DIR}")
    
    for domain in domain_map.values():
        domain_dir = OUTPUT_DIR / domain
        domain_dir.mkdir(exist_ok=True)
        print(f"创建领域目录: {domain_dir}")
    
    # 遍历工具包目录
    for file_path in toolkit_files:
        print(f"\n转换工具包: {file_path.name}")
        try:
            # 解析工具包
            block = parse_toolkit(file_path)
            print(f"  解析成功，标题: {block['title']}")
            print(f"  领域: {block['domain']}")
            print(f"  类型: {block['type']}")
            
            # 保存为JSON文件
            output_file = OUTPUT_DIR / block["domain"] / f"{block['id']}.json"
            print(f"  保存到: {output_file}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(block, f, ensure_ascii=False, indent=2)
            
            print(f"  转换成功!")
        except Exception as e:
            print(f"  转换失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n转换完成!")

if __name__ == "__main__":
    main()
