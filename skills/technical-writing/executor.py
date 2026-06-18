"""
技术文档写作技能执行器
"""
import os
from typing import Any
from agent_core.skill_executor_base import SkillExecutorBase
from agent_core.skill_manager import Skill


class TechnicalWritingExecutor(SkillExecutorBase):
    """技术文档写作技能执行器"""
    
    @property
    def skill_name(self) -> str:
        return "technical-writing"
    
    def execute(self, skill: Skill, resources: dict, **kwargs) -> Any:
        """执行技术文档写作技能"""
        title = kwargs.get("title", "默认技术文档标题")
        content = kwargs.get("content", "默认技术文档内容")
        
        # 读取技能的资源模板（如果有）
        template_path = os.path.join(resources["assets_path"], "tech_doc_template.md") if resources["assets_path"] else None
        template = "# {title}\n\n{content}\n\n## 参考规范\n- 采用Markdown格式\n- 包含目录和代码块标注\n- 增加实例和图表"
        
        if template_path and os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
        
        # 渲染模板
        doc = template.format(title=title, content=content)
        
        # 【修改】默认保存文档到 output 目录
        save = kwargs.get("save", True)  # 默认保存
        if save:
            # 创建 output 目录（如果不存在）
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成安全的文件名（替换非法字符）
            safe_title = title.replace("/", "_").replace("\\", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_")
            filename = f"{safe_title}.md"
            filepath = os.path.join(output_dir, filename)
            
            # 保存文档
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(doc)
            
            return f"文档已生成并保存到：{filepath}\n内容预览：{doc[:200]}..."
        
        return f"文档生成完成，内容预览：{doc[:200]}..."
