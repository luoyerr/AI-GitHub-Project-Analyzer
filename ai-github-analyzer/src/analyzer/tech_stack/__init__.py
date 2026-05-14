"""
技术栈分析模块

职责：
负责识别和分析项目的技术栈组成，包括编程语言、框架、库等。

当前状态：
已实现确定性技术栈检测器（TechStackDetector）和技术栈分析器（TechStackAnalyzer）。

导出：
- TechStackAnalyzer: 技术栈分析器（统一入口）
- TechStackDetector: 技术栈检测器（内部使用）
- TECH_STACK_RULES: 技术栈规则配置
"""

from src.analyzer.tech_stack.analyzer import TechStackAnalyzer
from src.analyzer.tech_stack.detector import TechStackDetector
from src.analyzer.tech_stack.rules import TECH_STACK_RULES

__all__ = ["TechStackAnalyzer", "TechStackDetector", "TECH_STACK_RULES"]
