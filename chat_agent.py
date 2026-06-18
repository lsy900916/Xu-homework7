#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
交互式Agent对话程序
通过对话自动识别并调用技能
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from agent_core.agent import Agent

def main():
    print("="*60)
    print("智能Agent对话系统")
    print("="*60)
    print("\n正在初始化技能系统...")
    
    # 初始化技能系统
    skill_manager = SkillManager()
    skill_executor = SkillExecutor(skill_manager)
    
    # 发现技能
    skill_manager.discover_skills()
    
    print("\n可用技能：")
    for skill in skill_manager.skills.values():
        print(f"  - {skill.name}: {skill.description}")
    
    # 初始化Agent（从环境变量读取配置）
    print("\n正在初始化Agent...")
    provider = os.getenv('LLM_PROVIDER', 'ollama')
    
    if provider == 'deepseek':
        api_url = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com')
        model = os.getenv('DEEPSEEK_MODEL', 'deepseek-v4-pro')
        print(f"提供商: DeepSeek")
        print(f"API地址: {api_url}")
        print(f"模型名称: {model}")
    else:
        api_url = os.getenv('LLM_API_URL', 'http://localhost:11434/v1/chat/completions')
        model = os.getenv('LLM_MODEL', 'qwen2.5:3b')
        print(f"提供商: Ollama")
        print(f"API地址: {api_url}")
        print(f"模型名称: {model}")
    
    agent = Agent(
        skill_manager=skill_manager,
        skill_executor=skill_executor
        # 其他参数从环境变量自动读取
    )
    
    print("\n" + "="*60)
    print("Agent已就绪！开始对话（输入'quit'或'exit'退出）")
    print("="*60 + "\n")
    
    # 对话循环
    while True:
        try:
            # 获取用户输入
            user_input = input("你: ").strip()
            
            if not user_input:
                continue
            
            # 退出命令
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("\n再见！")
                break
            
            # 处理用户消息
            response = agent.chat(user_input)
            
            # 显示回复
            print(f"\nAgent: {response}\n")
            print("-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误：{str(e)}\n")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
