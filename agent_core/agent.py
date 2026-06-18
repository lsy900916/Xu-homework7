import json
import os
import requests
from typing import List, Dict, Optional, Any
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor

# 尝试导入 openai SDK（用于 DeepSeek）
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class Agent:
    """智能Agent，通过对话自动识别并调用技能"""
    
    def __init__(
        self,
        skill_manager: SkillManager,
        skill_executor: SkillExecutor,
        api_url: Optional[str] = None,
        model: Optional[str] = None,
        use_thought: Optional[bool] = None,
        temperature: Optional[float] = None,
        provider: Optional[str] = None
    ):
        """
        初始化Agent
        
        参数:
        - skill_manager: 技能管理器
        - skill_executor: 技能执行器
        - api_url: 大模型API地址（默认从环境变量 LLM_API_URL 或 DEEPSEEK_API_URL 读取）
        - model: 模型名称（默认从环境变量 LLM_MODEL 或 DEEPSEEK_MODEL 读取）
        - use_thought: 是否使用思考过程（默认从环境变量 LLM_USE_THOUGHT 读取）
        - temperature: 温度参数（默认从环境变量 LLM_TEMPERATURE 读取）
        - provider: 大模型提供商（ollama 或 deepseek，默认从环境变量 LLM_PROVIDER 读取）
        """
        self.skill_manager = skill_manager
        self.skill_executor = skill_executor
        
        # 从环境变量读取 LLM 提供商
        self.provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()
        
        # 根据提供商选择不同的配置
        if self.provider == "deepseek":
            # DeepSeek 配置
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "DeepSeek 需要 openai SDK，请安装：pip install openai"
                )
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "使用 DeepSeek 需要设置 DEEPSEEK_API_KEY 环境变量"
                )
            self.api_url = api_url or os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")
            self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
            
            # 初始化 OpenAI 客户端
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_url
            )
        else:
            # Ollama 配置（默认）
            self.api_url = api_url or os.getenv("LLM_API_URL", "http://localhost:11434/v1/chat/completions")
            self.model = model or os.getenv("LLM_MODEL", "qwen2.5:3b")
            self.client = None
        
        # 处理 use_thought 参数
        if use_thought is None:
            env_value = os.getenv("LLM_USE_THOUGHT", "false").lower()
            self.use_thought = env_value in ["true", "1", "yes"]
        else:
            self.use_thought = use_thought
        
        # 处理 temperature 参数
        if temperature is None:
            self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        else:
            self.temperature = temperature
        
        self.conversation_history: List[Dict[str, str]] = []
        
        # 系统提示词：指导大模型识别技能（延迟构建，确保技能已发现）
        self._system_prompt = None
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词，包含所有可用技能的信息"""
        """构建系统提示词，包含所有可用技能的信息"""
        skills_info = []
        for skill in self.skill_manager.skills.values():
            skill_desc = f"- {skill.name}: {skill.description}\n"
            skill_desc += f"  触发关键词: {', '.join(skill.trigger_keywords)}\n"
            
            # 为 batch-counter-query 添加可用操作类型说明
            if skill.name == "batch-counter-query":
                skill_desc += "  可用操作类型（action参数）:\n"
                skill_desc += "    - page_query: 分页查询原始数据\n"
                skill_desc += "    - date_summary: 按日期统计seq合计\n"
                skill_desc += "    - total_summary: 获取整体汇总统计\n"
                skill_desc += "  注意：必须使用上述三种操作类型之一，不要使用其他名称！\n"
            
            skills_info.append(skill_desc)
        
        prompt = f"""你是一个智能助手，能够识别用户意图并调用相应的技能。

可用技能列表：
{chr(10).join(skills_info)}

识别规则：
1. 分析用户输入，判断是否需要调用技能

2. 【单技能】如果需要调用单个技能，返回JSON格式：
   {{
     "action": "call_skill",
     "skill_name": "技能名称",
     "reason": "调用原因",
     "params": {{"参数名": "参数值"}}
   }}

3. 【技能链】如果需要按顺序调用多个技能，返回JSON格式：
   {{
     "action": "call_skill_chain",
     "skills": [
       {{
         "skill_name": "第一个技能名称",
         "params": {{"参数名": "参数值"}},
         "description": "这个技能的作用"
       }},
       {{
         "skill_name": "第二个技能名称",
         "params": {{"参数名": "参数值"}},
         "description": "这个技能的作用"
       }}
     ],
     "reason": "为什么需要这些技能组合"
   }}

4. 如果只是普通对话，返回JSON格式：
   {{
     "action": "chat",
     "response": "你的回复内容"
   }}

5. 如果用户输入不明确，需要更多信息，返回：
   {{
     "action": "ask_clarification",
     "question": "需要澄清的问题"
   }}

注意：
- 仔细分析用户意图，准确匹配技能
- 从用户输入中提取技能所需的参数

【技能链识别指南】
以下情况应该使用技能链（call_skill_chain）：
1. 显式连接词："先...然后..."、"...之后..."、"接着"、"再"、"第一步...第二步"
2. 暗示性需求："看看数据，最好有个报告"、"查询一下，然后分析"、"获取数据并生成文档"
3. 多步骤任务："导入Excel并分析"、"查询数据后导出"、"登录并查询"
4. 组合动词："查询并生成"、"导入后分析"、"获取和报告"

【判断标准】
- 如果用户提到的需求需要多个技能配合完成 → 使用技能链
- 如果"看看数据"+"报告/文档/分析" → 技能链（查询 + 文档生成）
- 如果"导入"+"分析/处理" → 技能链（导入 + 分析）
- 保持友好和专业的回复风格

示例1 - 单技能：
用户: "帮我查询批次数据"
助手: {{
  "action": "call_skill",
  "skill_name": "batch-counter-query",
  "reason": "用户需要查询批次数据",
  "params": {{"action": "page_query"}}
}}

示例2 - 技能链：
用户: "先查询批次数据，然后生成一份技术文档"
助手: {{
  "action": "call_skill_chain",
  "skills": [
    {{"skill_name": "batch-counter-query", "params": {{"action": "page_query"}}, "description": "查询批次数据"}},
    {{"skill_name": "technical-writing", "params": {{"title": "批次数据报告", "content": "基于查询结果生成文档"}}, "description": "生成技术文档"}}
  ],
  "reason": "用户需要先查询数据再生成文档"
}}

示例3 - 暗示性技能链：
用户: "我想看看最近的数据情况，最好能有个报告"
助手: {{
  "action": "call_skill_chain",
  "skills": [
    {{"skill_name": "batch-counter-query", "params": {{"action": "page_query"}}, "description": "查询最近的数据"}},
    {{"skill_name": "technical-writing", "params": {{"title": "数据报告", "content": "基于查询结果生成报告"}}, "description": "生成数据报告"}}
  ],
  "reason": "用户想查看数据并生成报告，需要查询和文档生成两个技能配合"
}}
"""
        self._system_prompt = prompt
        return prompt
    
    def _call_llm(self, user_message: str) -> str:
        """
        调用大模型API
        
        参数:
        - user_message: 用户消息
        
        返回:
        - 模型回复
        """
        # 构建消息列表
        messages = []
        print("------------------user_message--------------" + str(user_message) + "--------------------------------")
        print("------------------conversation_history--------------" + str(self.conversation_history) + "--------------------------------")
        print("------------------system_prompt--------------" + str(self.system_prompt) + "--------------------------------")
        
        # 延迟构建系统提示词，确保技能已发现
        system_prompt = self.system_prompt
        
        # 判断是否是第一次对话：检查对话历史中是否有assistant的回复
        # 注意：conversation_history中可能已经有当前用户消息，但还没有assistant回复
        has_assistant_reply = any(msg.get("role") == "assistant" for msg in self.conversation_history)
        
        # 添加系统提示词（作为第一条用户消息，因为很多API不支持system role）
        if not has_assistant_reply:
            # 第一次对话，添加完整系统提示词
            # 注意：conversation_history中已经有当前用户消息，所以需要找到它并合并
            messages.append({
                "role": "user",
                "content": f"{system_prompt}\n\n用户消息：{user_message}"
            })
        else:
            # 后续对话：先添加系统提示词（确保模型知道可用技能），再添加历史对话
            messages.append({
                "role": "user",
                "content": system_prompt
            })
            # 添加历史对话（只保留最近5轮，避免上下文过长）
            for msg in self.conversation_history[-5:]:
                messages.append(msg)
            # 当前用户消息已经在conversation_history中，不需要重复添加
        
        # print("------------------messages--------------" + str(messages) + "--------------------------------")
        
        try:
            # 根据提供商选择不同的调用方式
            if self.provider == "deepseek":
                return self._call_deepseek(messages)
            else:
                return self._call_ollama(messages)
        except Exception as e:
            return f"调用大模型时出错：{str(e)}"
    
    def _call_ollama(self, messages: List[Dict[str, str]]) -> str:
        """
        调用 Ollama API
        
        参数:
        - messages: 消息列表
        
        返回:
        - 模型回复
        """
        # 构建请求参数
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": self.temperature
        }
        
        # 根据是否使用思考过程设置参数
        if not self.use_thought:
            payload["skip_thought"] = True
        
        try:
            # print("------------------payload--------------" + str(payload) + "--------------------------------")
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120  # 增加到120秒，给模型加载留出足够时间
            )
            response.raise_for_status()
            result = response.json()
            
            # 提取回复内容
            if "message" in result:
                content = result["message"].get("content", "")
            elif "content" in result:
                content = result["content"]
            else:
                content = str(result)
            
            return content.strip()
        except requests.exceptions.Timeout:
            return f"API调用超时：Ollama响应时间过长（超过120秒）。\n建议：\n1. 检查Ollama服务是否正常运行\n2. 首次使用模型需要加载，请耐心等待\n3. 尝试使用更小的模型（如qwen2.5:0.5b）"
        except requests.exceptions.ConnectionError:
            return f"无法连接到Ollama服务：{self.api_url}\n请确保Ollama服务正在运行（执行 'ollama serve'）"
        except requests.exceptions.RequestException as e:
            return f"Ollama API调用失败：{str(e)}"
    
    def _call_deepseek(self, messages: List[Dict[str, str]]) -> str:
        """
        调用 DeepSeek API
        
        参数:
        - messages: 消息列表
        
        返回:
        - 模型回复
        """
        try:
            # 构建请求参数
            kwargs = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "temperature": self.temperature
            }
            
            # 如果启用思考过程，添加 reasoning_effort 参数
            if self.use_thought:
                kwargs["reasoning_effort"] = "high"
                kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
            
            # 调用 DeepSeek API
            response = self.client.chat.completions.create(**kwargs)
            
            # 提取回复内容
            content = response.choices[0].message.content
            return content.strip()
        
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return f"DeepSeek API密钥验证失败：请检查 DEEPSEEK_API_KEY 是否正确"
            elif "timeout" in error_msg.lower():
                return f"DeepSeek API调用超时：请检查网络连接"
            elif "rate limit" in error_msg.lower():
                return f"DeepSeek API调用频率超限：请稍后再试"
            else:
                return f"DeepSeek API调用失败：{error_msg}"
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        解析大模型的回复，提取JSON格式的指令
        
        参数:
        - response: 模型回复
        
        返回:
        - 解析后的指令字典
        """
        # 尝试从回复中提取JSON
        import re
        
        # 方法1: 查找完整的JSON对象（支持嵌套）
        try:
            # 查找最外层的JSON对象
            brace_count = 0
            start_idx = -1
            for i, char in enumerate(response):
                if char == '{':
                    if start_idx == -1:
                        start_idx = i
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0 and start_idx != -1:
                        json_str = response[start_idx:i+1]
                        result = json.loads(json_str)
                        if "action" in result:
                            return result
                        start_idx = -1
            # 如果找到了开始但没有结束，尝试解析到末尾
            if start_idx != -1:
                json_str = response[start_idx:]
                result = json.loads(json_str)
                if "action" in result:
                    return result
        except:
            pass
        
        # 方法2: 查找包含"action"的JSON代码块（使用更精确的正则）
        try:
            # 先尝试匹配 markdown 代码块
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if code_block_match:
                json_str = code_block_match.group(1)
                result = json.loads(json_str)
                if isinstance(result, dict) and "action" in result:
                    return result
        except:
            pass
        
        # 方法3: 尝试直接解析整个回复
        try:
            result = json.loads(response)
            if isinstance(result, dict) and "action" in result:
                return result
        except:
            pass
        
        # 如果都失败，尝试智能识别（基于关键词）
        response_lower = response.lower()
        if "call_skill" in response_lower or "技能" in response:
            # 尝试提取技能名称
            for skill in self.skill_manager.skills.values():
                if skill.name in response or any(kw in response for kw in skill.trigger_keywords):
                    return {
                        "action": "call_skill",
                        "skill_name": skill.name,
                        "reason": "根据回复内容识别",
                        "params": {}
                    }
        
        # 如果都失败，返回普通对话
        return {
            "action": "chat",
            "response": response
        }
    
    @property
    def system_prompt(self) -> str:
        """获取系统提示词（延迟构建）"""
        if self._system_prompt is None:
            self._system_prompt = self._build_system_prompt()
        return self._system_prompt
    
    def _execute_skill_chain(self, instruction: Dict[str, Any]) -> str:
        """
        执行技能链
        
        参数:
        - instruction: AI返回的指令，包含skills列表
        
        返回:
        - 执行结果字符串
        """
        skills = instruction.get("skills", [])
        reason = instruction.get("reason", "")
        
        if not skills:
            return "错误：技能链为空"
        
        print(f"[技能链执行] 准备执行 {len(skills)} 个技能")
        print(f"[原因] {reason}")
        
        # 【修复】逐个执行技能，每个技能使用自己的参数
        results = []
        for i, skill_info in enumerate(skills):
            skill_name = skill_info["skill_name"]
            params = skill_info.get("params", {})
            description = skill_info.get("description", "")
            
            print(f"\n[技能链-{i+1}] 执行: {skill_name}")
            print(f"[参数] {params}")
            
            # 验证 batch-counter-query 的 action 参数
            if skill_name == "batch-counter-query":
                action = params.get("action")
                valid_actions = ["page_query", "date_summary", "total_summary"]
                if action and action not in valid_actions:
                    error_msg = f"错误：batch-counter-query 不支持的操作类型 '{action}'\n"
                    error_msg += f"可用的操作类型：{', '.join(valid_actions)}"
                    print(f"[错误] {error_msg}")
                    results.append({"success": False, "error": error_msg})
                    continue
            
            # 执行单个技能
            try:
                result = self.skill_executor.call_skill(skill_name, **params)
                results.append(result)
                print(f"[完成] {skill_name} 执行成功")
            except Exception as e:
                error_result = {"success": False, "error": str(e)}
                results.append(error_result)
                print(f"[错误] {skill_name} 执行失败: {e}")
        
        # 格式化结果
        response_parts = []
        response_parts.append(f"已为您执行技能链（{len(skills)}个技能）：\n")
        
        for i, (skill_info, result) in enumerate(zip(skills, results)):
            skill_name = skill_info["skill_name"]
            description = skill_info.get("description", "")
            
            # 检查是否执行成功
            if isinstance(result, dict) and not result.get("success", True):
                response_parts.append(f"{i+1}. ❌ {skill_name}: {description}")
                error_msg = result.get("error", "未知错误")
                response_parts.append(f"   错误: {error_msg}")
            else:
                response_parts.append(f"{i+1}. ✅ {skill_name}: {description}")
                if result:
                    # 只显示结果的摘要
                    result_str = str(result)[:200]
                    response_parts.append(f"   结果: {result_str}...")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _extract_skill_params(self, user_message: str, skill_name: str) -> Dict[str, Any]:
        """
        从用户消息中提取技能参数
        
        参数:
        - user_message: 用户消息
        - skill_name: 技能名称
        
        返回:
        - 参数字典
        """
        import re
        params = {}
        
        # 根据技能名称提取特定参数
        if skill_name == "batch-counter-query":
            # 提取年份（如：2024年）
            year_match = re.search(r'(\d{4})年', user_message)
            if year_match:
                year = year_match.group(1)
                params["start_date"] = f"{year}-01-01"
                params["end_date"] = f"{year}-12-31"
            
            # 提取日期范围（如：2024-01-01到2024-12-31）
            date_range_match = re.search(r'(\d{4}-\d{2}-\d{2})\s*[到至]\s*(\d{4}-\d{2}-\d{2})', user_message)
            if date_range_match:
                params["start_date"] = date_range_match.group(1)
                params["end_date"] = date_range_match.group(2)
            
            # 提取单个日期
            elif re.search(r'\d{4}-\d{2}-\d{2}', user_message):
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', user_message)
                if date_match:
                    params["start_date"] = date_match.group(1)
                    params["end_date"] = date_match.group(1)
            
            # 提取页码
            page_match = re.search(r'第?(\d+)页', user_message)
            if page_match:
                params["page"] = int(page_match.group(1))
            
            # 提取每页数量
            page_size_match = re.search(r'(\d+)条', user_message)
            if page_size_match:
                params["page_size"] = int(page_size_match.group(1))
        
        elif skill_name == "overtime-calculation":
            # 提取文件路径
            file_patterns = [
                r'[A-Za-z]:[\\/][^\s]+\.xlsx',
                r'[^\s]+\.xlsx',
                r'考勤[^\s]*\.xlsx',
                r'attendance[^\s]*\.xlsx'
            ]
            for pattern in file_patterns:
                match = re.search(pattern, user_message)
                if match:
                    params["data_path"] = match.group(0)
                    break
            
            # 提取其他参数（如果提到）
            if "每小时" in user_message or "时薪" in user_message:
                rate_match = re.search(r'(\d+(?:\.\d+)?)\s*元', user_message)
                if rate_match:
                    params["hourly_rate"] = float(rate_match.group(1))
        
        elif skill_name == "data-analysis":
            # 提取文件路径
            import re
            file_patterns = [
                r'[A-Za-z]:[\\/][^\s]+\.(xlsx|csv)',
                r'[^\s]+\.(xlsx|csv)',
                r'数据[^\s]*\.(xlsx|csv)',
                r'data[^\s]*\.(xlsx|csv)'
            ]
            for pattern in file_patterns:
                match = re.search(pattern, user_message)
                if match:
                    params["data_path"] = match.group(0)
                    break
        
        elif skill_name == "technical-writing":
            # 提取标题和内容
            if "标题" in user_message or "题目" in user_message:
                import re
                title_match = re.search(r'标题[：:]\s*([^\n]+)|题目[：:]\s*([^\n]+)', user_message)
                if title_match:
                    params["title"] = title_match.group(1) or title_match.group(2)
            
            if "内容" in user_message:
                import re
                content_match = re.search(r'内容[：:]\s*([^\n]+)', user_message)
                if content_match:
                    params["content"] = content_match.group(1)
        print(params)
        print("--------------------------------")
        return params
    
    def chat(self, user_message: str) -> str:
        """
        处理用户消息，自动识别技能并执行
        
        参数:
        - user_message: 用户消息
        
        返回:
        - Agent的回复
        """
        # 记录用户消息
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # 【优化】所有请求都先通过LLM进行意图识别，确保准确性
        print("[AI分析] 正在分析用户意图...")
        llm_response = self._call_llm(user_message)
        print(f"[AI回复] {llm_response[:200]}...")
        
        # 解析大模型的回复
        instruction = self._parse_llm_response(llm_response)
        
        print("------------------instruction--------------" + str(instruction) + "--------------------------------")
        action = instruction.get("action", "chat")
        print("------------------action--------------" + str(action) + "--------------------------------")
        print("--------------------------------")
        
        if action == "call_skill_chain":
            # 【新增】处理技能链
            return self._execute_skill_chain(instruction)
        
        elif action == "call_skill":
            # 调用技能
            skill_name = instruction.get("skill_name", "")
            reason = instruction.get("reason", "")
            skill_params = instruction.get("params", {})
            
            # 合并从用户消息中提取的参数
            extracted_params = self._extract_skill_params(user_message, skill_name)
            skill_params.update(extracted_params)
            
            print(f"[技能调用] {skill_name} - {reason}")
            result = self.skill_executor.call_skill(skill_name, **skill_params)
            
            if result:
                response = f"已为您执行技能「{skill_name}」：\n{str(result)[:500]}"
            else:
                response = f"执行技能「{skill_name}」时出现问题，请检查参数是否正确。"
            
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        elif action == "ask_clarification":
            # 需要澄清
            question = instruction.get("question", "请提供更多信息")
            response = f"需要更多信息：{question}"
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        else:
            # 普通对话
            response = instruction.get("response", llm_response)
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
    
    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history = []
