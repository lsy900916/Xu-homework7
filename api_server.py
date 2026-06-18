#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Skill API服务器启动脚本
按照Controller -> Skill -> Repository架构设计
"""
from agent_core.skill_manager import SkillManager
from agent_core.skill_executor import SkillExecutor
from api.controller import SkillController
from repository.sqlite_user_repository import SqliteUserRepository

def main():
    print("="*60)
    print("初始化Skill系统...")
    print("="*60)
    
    # 初始化认证库
    SqliteUserRepository().init_auth_db()

    # 初始化技能系统
    skill_manager = SkillManager()
    skill_executor = SkillExecutor(skill_manager)
    
    # 发现技能
    skill_manager.discover_skills()
    
    print("\n已发现的技能：")
    for skill in skill_manager.skills.values():
        print(f"  - {skill.name}: {skill.description}")
    
    # 创建API控制器
    print("\n" + "="*60)
    print("创建API控制器...")
    print("="*60)
    
    controller = SkillController(skill_manager, skill_executor)
    
    # 启动API服务器
    print("\n" + "="*60)
    print("启动API服务器...")
    print("="*60)
    print("\nAPI接口列表：")
    print("  GET  /health                    - 健康检查")
    print("  POST /api/auth/login            - 用户登录并获取token")
    print("  GET  /api/skills                - 获取所有技能列表")
    print("  POST /api/skills/<name>/execute - 执行指定技能（通用接口）")
    print("\n技术文档写作接口：")
    print("  POST /api/writing/generate      - 生成技术文档")
    print("\n批次计数器查询接口：")
    print("  GET  /api/batch-counter/page          - 分页查询batch_counter数据")
    print("  GET  /api/batch-counter/date-summary   - 按日期统计seq合计（分页）")
    print("  GET  /api/batch-counter/total-summary  - 获取整体汇总统计")
    print("  POST /api/batch-counter/query          - 通用查询接口")
    print("\n" + "="*60)
    
    controller.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
