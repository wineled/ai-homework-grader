#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI作业批改师 - 数学作业自动批改工具
基于Claude API的智能作业批改Agent
"""

import os
import sys
import json
import requests
import argparse
from datetime import datetime
from typing import List, Dict, Optional

# ============================================================
# 配置
# ============================================================
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL = "https://api.anthropic.com/v1/messages"

# 默认模型
DEFAULT_MODEL = "claude-sonnet-4-20250514"

# ============================================================
# 系统提示词 - AI作业批改师角色
# ============================================================
SYSTEM_PROMPT = """你身为中国顶尖的数学教师，学生会将完成的题目提交给你，你要对每个作答判断其正确与否。

# 目标任务 #
针对【提交的题目】，判定学生的 Answer 是否正确。

# 工作流程#
1. 题目解答：
   1.1 首先梳理清楚解题思路，明确从哪些角度、运用什么方法来处理题目。
   1.2 依据清晰的思路，一步一步地准确解题，每一步都要保证计算、推理等环节的精确性。
   1.3 从完整的解题过程中提炼出每个作答单元的最终结果，以此作为「参考答案」。

2. 作业批改：
   2.1 若【提交的题目】中没有任何 Answer 内容，直接返回 "未作答"。
   2.2 对照「参考答案」，对【提交的题目】里的各个 Answer 进行批改。将作答内容与「参考答案」进行对比，若两者等价，则该作答返回 "正确"；若两者不等价，则该作答返回 "错误"。

# 输出格式 #
把返回内容整理成 XML 格式的字符串，输出题目要求、参考答案、作答内容以及批改结果。若一道题目包含多个小问或子问题，需分别进行批改并输出。格式如下：
<root>
<item>
<题目要求> xxx </题目要求>
<参考答案> xxx </参考答案>
<作答内容> xxx </作答内容>
<批改结果> xxx </批改结果>
</item>
"""


# ============================================================
# 作业数据类
# ============================================================
class HomeworkItem:
    """作业题目项"""
    def __init__(self, question: str, answer: str = ""):
        self.question = question      # 题目要求
        self.answer = answer          # 学生作答
        self.reference = ""           # 参考答案
        self.result = ""              # 批改结果


class HomeworkSubmission:
    """作业提交"""
    def __init__(self, subject: str = "数学", items: List[HomeworkItem] = None):
        self.subject = subject
        self.items = items or []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_item(self, question: str, answer: str = ""):
        """添加题目"""
        self.items.append(HomeworkItem(question, answer))

    def to_prompt(self) -> str:
        """转换为提示词"""
        prompt = f"【提交的题目】（科目：{self.subject}）\n\n"
        for i, item in enumerate(self.items, 1):
            prompt += f"第{i}题：\n"
            prompt += f"题目要求：{item.question}\n"
            prompt += f"学生作答：{item.answer or '（未作答）'}\n\n"
        return prompt

    def parse_xml_result(self, xml_content: str) -> str:
        """解析XML结果"""
        return xml_content


# ============================================================
# Claude API 调用
# ============================================================
def call_claude_api(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """调用Claude API进行作业批改"""
    if not API_KEY:
        raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    data = {
        "model": model,
        "max_tokens": 4096,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data, timeout=60)
    response.raise_for_status()

    result = response.json()
    return result["content"][0]["text"]


# ============================================================
# 作业批改器
# ============================================================
class HomeworkGrader:
    """作业批改器"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError("需要提供API Key")

    def grade(self, submission: HomeworkSubmission, model: str = DEFAULT_MODEL) -> str:
        """批改作业"""
        prompt = submission.to_prompt()
        return call_claude_api(prompt, model)

    def grade_from_file(self, filepath: str, model: str = DEFAULT_MODEL) -> str:
        """从文件批改作业"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.grade_from_text(content, model)

    def grade_from_text(self, text: str, model: str = DEFAULT_MODEL) -> str:
        """从文本批改作业"""
        submission = HomeworkSubmission()
        # 简单的文本解析（可扩展）
        lines = text.strip().split('\n')
        current_question = ""
        current_answer = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 简单解析格式：题目: xxx | 答案: xxx
            if '题目' in line or '题' in line:
                if current_question:
                    submission.add_item(current_question, current_answer)
                    current_answer = ""
                current_question = line
            elif '答' in line or '学生作答' in line:
                current_answer = line

        if current_question:
            submission.add_item(current_question, current_answer)

        return self.grade(submission, model)

    def grade_json(self, homework_data: Dict, model: str = DEFAULT_MODEL) -> str:
        """从JSON数据批改作业"""
        submission = HomeworkSubmission(
            subject=homework_data.get("subject", "数学")
        )

        for item in homework_data.get("items", []):
            submission.add_item(
                question=item.get("question", ""),
                answer=item.get("answer", "")
            )

        return self.grade(submission, model)


# ============================================================
# 主程序
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="AI作业批改师")
    parser.add_argument("--api-key", "-k", help="Anthropic API Key")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help="使用的模型")
    parser.add_argument("--subject", "-s", default="数学", help="科目")
    parser.add_argument("--file", "-f", help="作业文件路径")
    parser.add_argument("--json", "-j", help="JSON格式的作业数据")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")

    args = parser.parse_args()

    # 获取API Key
    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("错误：需要设置 ANTHROPIC_API_KEY 环境变量或使用 --api-key 参数")
        sys.exit(1)

    grader = HomeworkGrader(api_key)

    if args.interactive:
        # 交互模式
        print("=" * 60)
        print("AI作业批改师 - 交互模式")
        print("=" * 60)
        print("输入题目和作答，输入 'done' 开始批改，输入 'quit' 退出\n")

        submission = HomeworkSubmission(subject=args.subject)

        while True:
            question = input("题目要求（输入done开始批改）：")
            if question.lower() == 'quit':
                break
            if question.lower() == 'done':
                break

            answer = input("学生作答：")
            submission.add_item(question, answer)

            print("-" * 40)

        if submission.items:
            print("\n正在批改，请稍候...\n")
            result = grader.grade(submission, args.model)
            print("\n" + "=" * 60)
            print("批改结果：")
            print("=" * 60)
            print(result)
        else:
            print("没有题目需要批改")

    elif args.file:
        # 文件模式
        print(f"正在批改文件：{args.file}")
        result = grader.grade_from_file(args.file, args.model)
        print("\n" + "=" * 60)
        print("批改结果：")
        print("=" * 60)
        print(result)

    elif args.json:
        # JSON模式
        try:
            data = json.loads(args.json)
            result = grader.grade_json(data, args.model)
            print(result)
        except json.JSONDecodeError:
            print("错误：无效的JSON格式")

    else:
        # 单题模式（从stdin读取）
        print("请输入作业内容（题目和作答），完成后输入 EOF（Ctrl+D）结束：\n")

        content = sys.stdin.read()
        if content.strip():
            result = grader.grade_from_text(content, args.model)
            print("\n" + "=" * 60)
            print("批改结果：")
            print("=" * 60)
            print(result)


if __name__ == "__main__":
    main()
