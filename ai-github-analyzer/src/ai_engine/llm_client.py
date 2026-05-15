"""
LLM 客户端。

负责与大语言模型进行交互，发送请求并接收响应。
"""

from typing import Optional, Dict, Any, List
from loguru import logger

from ..models import PromptResult, PromptExecutionConfig


class LLMClient:
    """
    LLM 客户端。
    
    职责：
    - 发送 Prompt 到 LLM
    - 接收和解析响应
    - 处理超时和错误
    - 记录调用指标
    
    支持多种后端：
    - OpenAI API
    - Ollama（本地模型）
    - 其他兼容接口
    """
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None) -> None:
        """
        初始化 LLM 客户端。
        
        Args:
            model_name: 模型名称
            api_key: API 密钥（可选）
        """
        self.model_name: str = model_name
        self.api_key: Optional[str] = api_key
        self._initialized: bool = False
    
    def initialize(self) -> None:
        """
        初始化客户端连接。
        
        建立与 LLM 服务的连接，验证认证信息。
        """
        pass
    
    def send_prompt(
        self,
        prompt: str,
        config: Optional[PromptExecutionConfig] = None
    ) -> PromptResult:
        """
        发送 Prompt 并获取响应。
        
        Args:
            prompt: 要发送的 Prompt 文本
            config: 执行配置（可选）
            
        Returns:
            PromptResult: Prompt 执行结果
            
        Raises:
            ConnectionError: 当无法连接到 LLM 服务时
            TimeoutError: 当请求超时时
        """
        pass
    
    def send_with_retry(
        self,
        prompt: str,
        config: Optional[PromptExecutionConfig] = None
    ) -> PromptResult:
        """
        发送 Prompt 并在失败时自动重试。
        
        Args:
            prompt: 要发送的 Prompt 文本
            config: 执行配置（可选）
            
        Returns:
            PromptResult: Prompt 执行结果
        """
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量。
        
        Args:
            text: 要估算的文本
            
        Returns:
            int: 估算的 token 数量
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型的信息。
        
        Returns:
            Dict[str, Any]: 模型信息
        """
        pass
    
    def set_model(self, model_name: str) -> None:
        """
        切换使用的模型。
        
        Args:
            model_name: 新的模型名称
        """
        pass
    
    def close(self) -> None:
        """
        关闭客户端连接，释放资源。
        """
        pass
