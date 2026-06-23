import os
import re
import yaml
import markdown
from typing import Dict, List, Optional

# 技能对象：存储技能的元数据、完整指令、资源路径
class Skill:
    def __init__(self):
        self.name: str = ""          # 技能名（唯一标识）
        self.description: str = ""   # 技能描述（用于意图匹配）
        self.trigger_keywords: List[str] = [] # 触发关键词（自动触发用）
        self.instructions: str = ""  # 技能完整指令（SKILL.md 解析后）
        self.path: str = ""          # 技能目录路径
        self.scripts_path: str = ""  # 脚本路径
        self.assets_path: str = ""   # 资源路径

class SkillManager:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir  # 技能仓库根目录
        self.skills: Dict[str, Skill] = {}  # 已加载技能缓存（name: Skill）
        self._init_skills_dir()       # 初始化技能目录

    # 初始化技能仓库目录（不存在则创建）
    def _init_skills_dir(self):
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            print(f"创建技能仓库目录：{self.skills_dir}")

    # 【第一层：发现阶段】扫描所有技能，仅加载元数据（name/description/trigger_keywords）
    def discover_skills(self) -> Dict[str, Skill]:
        print("=== 开始发现技能（仅加载元数据）===")
        # 扫描skills目录下的所有子目录（每个子目录是一个技能）
        for skill_folder in os.listdir(self.skills_dir):
            skill_path = os.path.join(self.skills_dir, skill_folder)
            if not os.path.isdir(skill_path):
                continue
            # 读取SKILL.md（核心必需文件）
            skill_md_path = os.path.join(skill_path, "SKILL.md")
            if not os.path.exists(skill_md_path):
                print(f"跳过{skill_folder}：缺少SKILL.md文件")
                continue
            # 解析SKILL.md中的元数据（YAML前端部分）
            with open(skill_md_path, "r", encoding="utf-8") as f:
                content = f.read()
            # 匹配YAML元数据块（---开头，---结尾）
            yaml_pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
            yaml_match = yaml_pattern.search(content)
            if not yaml_match:
                print(f"跳过{skill_folder}：SKILL.md缺少YAML元数据")
                continue
            # 解析YAML元数据
            try:
                meta = yaml.safe_load(yaml_match.group(1))
            except Exception as e:
                print(f"跳过{skill_folder}：YAML元数据解析失败：{e}")
                continue
            # 初始化技能对象，仅赋值元数据
            skill = Skill()
            skill.name = meta.get("name", skill_folder)
            skill.description = meta.get("description", "")
            skill.trigger_keywords = meta.get("trigger_keywords", [])
            skill.path = skill_path
            skill.scripts_path = os.path.join(skill_path, "scripts")
            skill.assets_path = os.path.join(skill_path, "assets")
            # 缓存技能
            self.skills[skill.name] = skill
            print(f"发现技能：{skill.name} - {skill.description}")
        print(f"=== 技能发现完成，共加载{len(self.skills)}个技能元数据===\n")
        return self.skills

    # 【第二层：激活阶段】根据技能名，加载完整指令（解析SKILL.md的Markdown内容）
    def activate_skill(self, skill_name: str) -> Optional[Skill]:
        if skill_name not in self.skills:
            print(f"技能{skill_name}不存在，激活失败")
            return None
        skill = self.skills[skill_name]
        if skill.instructions:  # 已激活则直接返回
            return skill
        print(f"=== 激活技能：{skill_name}（加载完整指令）===")
        skill_md_path = os.path.join(skill.path, "SKILL.md")
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 移除YAML元数据块，仅保留Markdown指令部分
        yaml_pattern = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
        instructions_content = yaml_pattern.sub("", content)
        # 解析Markdown为HTML（也可直接保留纯文本，按需选择）
        skill.instructions = markdown.markdown(instructions_content)
        print(f"技能{skill_name}激活完成\n")
        return skill

    # 【第三层：执行阶段】获取技能的资源/脚本路径（按需访问，不提前加载）
    def get_skill_resources(self, skill_name: str) -> Optional[Dict]:
        skill = self.activate_skill(skill_name)
        if not skill:
            return None
        print(f"=== 加载技能{skill_name}资源路径（执行阶段）===")
        resources = {
            "scripts_path": skill.scripts_path if os.path.exists(skill.scripts_path) else None,
            "assets_path": skill.assets_path if os.path.exists(skill.assets_path) else None,
            "instructions": skill.instructions
        }
        print(f"资源加载完成\n")
        return resources

    # 根据关键词匹配技能（实现自动触发的基础）
    def match_skill_by_keyword(self, query: str) -> Optional[Skill]:
        query_lower = query.lower()
        matched_skills = []
        for skill in self.skills.values():
            # 关键词匹配（技能名/描述/触发关键词中包含任意一个）
            name_match = skill.name.lower() in query_lower
            desc_match = skill.description.lower() in query_lower
            # 检查完整关键词匹配
            keyword_match = any(k.lower() in query_lower for k in skill.trigger_keywords)
            # 改进：对于多字关键词，如果关键词的主要部分都出现在查询中，也认为匹配
            # 例如："Excel分析" 可以匹配包含 "Excel" 和 "分析" 的查询
            keyword_partial_match = False
            if not keyword_match:
                for keyword in skill.trigger_keywords:
                    keyword_lower = keyword.lower()
                    # 对于混合中英文关键词，分别检查英文单词和中文部分
                    import re
                    # 提取英文单词
                    english_words = re.findall(r'[a-z]+', keyword_lower)
                    # 提取中文字符
                    chinese_chars = re.findall(r'[\u4e00-\u9fff]', keyword_lower)
                    # 检查所有英文单词是否都在查询中
                    english_match = all(word in query_lower for word in english_words) if english_words else True
                    # 检查所有中文字符是否都在查询中
                    chinese_match = all(char in query_lower for char in chinese_chars) if chinese_chars else True
                    # 如果英文和中文都匹配，则认为部分匹配成功
                    if english_match and chinese_match and (english_words or chinese_chars):
                        keyword_partial_match = True
                        break
            
            if name_match or desc_match or keyword_match or keyword_partial_match:
                matched_skills.append(skill)
        # 简单匹配：返回第一个匹配的技能（可扩展为相似度排序）
        if matched_skills:
            return matched_skills[0]
        return None
