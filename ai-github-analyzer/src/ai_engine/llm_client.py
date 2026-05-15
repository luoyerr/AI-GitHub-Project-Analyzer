"""
LLM 客户端。

负责与大语言模型进行交互，发送请求并接收响应。
当前阶段仅支持通过 OpenRouter 调用 Qwen 免费模型。
"""

import os
import time
from typing import Optional, List
from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv

# 使用绝对导入
from src.models import LLMResponse

# 加载 .env 文件中的环境变量
load_dotenv()


class LLMClient:
    """
    LLM 客户端。
    
    职责：
    - 发送 Prompt 到 LLM
    - 接收和解析响应
    - 处理超时和错误
    - 记录调用指标
    
    当前仅支持：
    - OpenAI Compatible API（通过 OpenRouter 调用 Qwen 免费模型）
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> None:
        """
        初始化 LLM 客户端。
        
        Args:
            provider: AI 提供商（当前仅支持 openai_compatible）
            model: 模型名称（例如 qwen/qwen3-coder:free）
            api_key: API 密钥
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
        """
        # 从环境变量读取配置，如果未提供参数
        self.provider: str = provider or os.getenv("AI_PROVIDER") or "openai_compatible"
        self.model: str = model or os.getenv("AI_MODEL") or "qwen/qwen3-coder:free"
        self.api_key: str = api_key or os.getenv("AI_API_KEY") or ""
        self.base_url: str = base_url or os.getenv("AI_BASE_URL") or "https://openrouter.ai/api/v1"
        self.timeout: int = timeout or int(os.getenv("AGENT_TIMEOUT", "60"))
        
        # 初始化 OpenAI 客户端（兼容模式）
        self.client: OpenAI = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        self._initialized: bool = True
        logger.info(f"LLM 客户端初始化完成 - 模型: {self.model}, 提供商: {self.provider}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """
        生成 LLM 响应。
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（0-1）
            max_tokens: 最大 token 数（可选）
            
        Returns:
            LLMResponse: LLM 响应对象
        """
        start_time = time.time()
        
        try:
            # 构建消息列表
            messages: List[ChatCompletionMessageParam] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # 调用 OpenAI Compatible API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout
            )
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            # 提取响应内容
            content = response.choices[0].message.content if response.choices else None
            
            # 提取 Token 使用统计
            token_usage = None
            if response.usage:
                token_usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            # 记录成功日志
            logger.info(
                f"LLM 调用成功 - 模型: {self.model}, "
                f"耗时: {elapsed_time:.2f}s, "
                f"Token: {token_usage['total_tokens'] if token_usage else 'N/A'}"
            )
            
            return LLMResponse(
                success=True,
                content=content,
                model=self.model,
                token_usage=token_usage,
                elapsed_time=elapsed_time,
                error_message=None
            )
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = str(e)
            
            # 记录错误日志
            logger.error(
                f"LLM 调用失败 - 模型: {self.model}, "
                f"耗时: {elapsed_time:.2f}s, "
                f"错误: {error_msg}"
            )
            
            # 统一返回失败响应，不抛出异常
            return LLMResponse(
                success=False,
                content=None,
                model=self.model,
                token_usage=None,
                elapsed_time=elapsed_time,
                error_message=error_msg
            )
    
    def validate_connection(self) -> LLMResponse:
        """
        验证 LLM 连接是否正常。
        
        发送一个简单的测试请求，用于 doctor 命令验证配置是否正确。
        
        Returns:
            LLMResponse: 验证结果
        """
        test_prompt = "请回复：hello"
        
        logger.info("开始验证 LLM 连接...")
        response = self.generate(prompt=test_prompt, temperature=0.1)
        
        if response.success:
            logger.info(f"LLM 连接验证成功 - 响应: {response.content}")
        else:
            logger.error(f"LLM 连接验证失败 - 错误: {response.error_message}")
        
        return response
