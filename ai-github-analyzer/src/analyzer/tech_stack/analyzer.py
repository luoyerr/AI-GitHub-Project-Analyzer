"""
技术栈分析器

职责：
作为技术栈分析的统一入口，协调检测器执行确定性技术栈分析。

设计原则：
1. 统一入口 - 所有技术栈分析必须通过此分析器
2. 异常安全 - 分析失败不影响主流程
3. 中文日志 - 所有日志使用中文
4. 可扩展性 - 预留 AI 推理和质量检查的扩展点

当前阶段：
仅支持确定性技术栈分析（基于规则匹配）。

未来扩展：
- ai_reasoner() - AI 推理增强
- quality_check() - 质量检查
"""

from loguru import logger

from models import ProjectTechStack
from scanner import RepositorySnapshot
from ..base import BaseAnalyzer
from .detector import TechStackDetector


class TechStackAnalyzer(BaseAnalyzer):
    """技术栈分析器。
    
    继承自基础分析器，作为技术栈分析的统一入口。
    内部调用 TechStackDetector 执行确定性检测。
    
    示例用法：
        analyzer = TechStackAnalyzer()
        result = analyzer.analyze(scan_result)
    """
    
    def __init__(self):
        """初始化技术栈分析器。"""
        self.detector = TechStackDetector()
        logger.info("技术栈分析器已初始化")
    
    def analyze(self, scan_result: RepositorySnapshot) -> ProjectTechStack:
        """执行技术栈分析。
        
        这是技术栈分析的统一入口，内部调用检测器执行分析。
        
        Args:
            scan_result: 仓库扫描结果
            
        Returns:
            项目技术栈模型
            
        Raises:
            Exception: 分析过程中发生的任何异常都会向上传播
                      （由调用方决定如何处理）
        """
        logger.info("开始技术栈分析")
        
        # 调用检测器执行确定性分析
        result: ProjectTechStack = self.detector.detect(scan_result)
        
        logger.info("技术栈分析完成")
        
        return result
