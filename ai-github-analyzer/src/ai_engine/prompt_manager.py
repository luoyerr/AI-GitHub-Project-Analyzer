"""
Prompt 管理器。

负责加载、管理和渲染 Prompt 模板。
支持模板版本管理、变量注入、校验和预览功能。
"""

from typing import Dict, Optional, Any, List, Set
from pathlib import Path
import re
from loguru import logger


class PromptManager:
    """
    Prompt 管理器。
    
    职责：
    - 加载 Prompt 模板文件（UTF-8 编码）
    - 管理模板版本和元数据
    - 渲染模板（Jinja2 风格变量注入）
    - 校验模板完整性和变量缺失
    - 提供调试预览功能
    
    设计原则：
    - Prompt 与业务逻辑完全解耦
    - 模板可替换，支持 A/B 测试
    - 禁止将 Prompt 写死在 Python 代码中
    - 支持后续扩展和版本迭代
    
    使用示例：
        >>> manager = PromptManager()
        >>> prompt = manager.build_prompt(
        ...     task_name="tech_stack",
        ...     variables={"repo_name": "my-project", "context": "..."}
        ... )
        >>> manager.preview_prompt(prompt)
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None) -> None:
        """
        初始化 Prompt 管理器。
        
        Args:
            prompts_dir: Prompt 模板目录路径，默认为项目根目录下的 prompts/ 文件夹
        """
        self.prompts_dir: Path = prompts_dir or Path(__file__).parent.parent.parent / "prompts"
        self.templates: Dict[str, str] = {}  # 模板名称 -> 模板内容
        self.template_versions: Dict[str, str] = {}  # 模板名称 -> 版本号
        self._loaded: bool = False
        
        # 验证 prompts 目录是否存在
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts 目录不存在: {self.prompts_dir}")
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"已创建 Prompts 目录: {self.prompts_dir}")
    
    def load_template(self, template_name: str) -> str:
        """
        读取并加载指定的 Prompt 模板文件。
        
        支持 UTF-8 编码，自动处理异常。
        模板文件命名规范：{template_name}.md
        
        Args:
            template_name: 模板名称（不含 .md 扩展名），例如 "tech_stack"
            
        Returns:
            str: 模板内容字符串
            
        Raises:
            FileNotFoundError: 当模板文件不存在时
            UnicodeDecodeError: 当文件编码不是 UTF-8 时
            IOError: 当文件读取失败时
            
        Examples:
            >>> content = manager.load_template("tech_stack")
            >>> print(content[:100])
        """
        template_file = self.prompts_dir / f"{template_name}.md"
        
        # 检查文件是否存在
        if not template_file.exists():
            error_msg = f"模板文件不存在: {template_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            # 使用 UTF-8 编码读取文件
            content = template_file.read_text(encoding="utf-8")
            
            # 缓存模板内容
            self.templates[template_name] = content
            
            # 记录加载日志
            logger.debug(f"成功加载模板: {template_name} ({len(content)} 字符)")
            
            return content
            
        except UnicodeDecodeError as e:
            error_msg = f"模板文件编码错误（需要 UTF-8）: {template_file} - {str(e)}"
            logger.error(error_msg)
            raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, error_msg)
            
        except IOError as e:
            error_msg = f"读取模板文件失败: {template_file} - {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg)
    
    def get_system_prompt(self) -> str:
        """
        获取系统级 Prompt 模板。
        
        读取 system_prompt.md 文件，该文件定义 AI 助手的角色、职责和约束。
        
        Returns:
            str: 系统 Prompt 内容
            
        Raises:
            FileNotFoundError: 当 system_prompt.md 不存在时
            
        Examples:
            >>> system_prompt = manager.get_system_prompt()
            >>> print(system_prompt)
        """
        return self.load_template("system_prompt")
    
    def build_prompt(
        self,
        task_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        构建最终的 Prompt 字符串。
        
        流程：
        1. 加载指定任务的模板
        2. 注入变量（支持 Jinja2 风格 {{ variable }} 语法）
        3. 返回渲染后的完整 Prompt
        
        支持的变量语法：
        - {{ repo_name }}: 仓库名称
        - {{ context }}: 项目上下文
        - {{ tech_stack }}: 技术栈信息
        - 任意自定义变量
        
        Args:
            task_name: 任务名称，对应模板文件名（不含 .md）
            variables: 要注入的变量字典，键为变量名，值为变量值
            
        Returns:
            str: 渲染后的最终 Prompt 字符串
            
        Raises:
            FileNotFoundError: 当模板文件不存在时
            KeyError: 当模板中存在未提供的必需变量时
            
        Examples:
            >>> prompt = manager.build_prompt(
            ...     task_name="tech_stack",
            ...     variables={
            ...         "repo_name": "my-project",
            ...         "context": "这是一个 Python Web 项目...",
            ...         "tech_stack": "Python, FastAPI, PostgreSQL"
            ...     }
            ... )
            >>> print(prompt)
        """
        # 加载模板
        template_content = self.load_template(task_name)
        
        # 如果没有变量，直接返回原始模板
        if not variables:
            logger.debug(f"未提供变量，返回原始模板: {task_name}")
            return template_content
        
        # 提取模板中的所有变量占位符
        required_vars = self._extract_variables(template_content)
        
        # 检查是否有缺失的必需变量
        missing_vars = required_vars - set(variables.keys())
        if missing_vars:
            warning_msg = f"模板 '{task_name}' 缺少变量: {', '.join(missing_vars)}"
            logger.warning(warning_msg)
            # 注意：这里不抛出异常，允许部分变量缺失，保持灵活性
        
        # 执行变量替换（Jinja2 风格）
        rendered_prompt = template_content
        for var_name, var_value in variables.items():
            # 将变量值转换为字符串
            var_str = str(var_value) if var_value is not None else ""
            # 替换 {{ var_name }} 格式的占位符
            pattern = r"\{\{\s*" + re.escape(var_name) + r"\s*\}\}"
            # rendered_prompt = re.sub(pattern, var_str, rendered_prompt)
            rendered_prompt = re.sub(pattern, lambda m: var_str, rendered_prompt)
        logger.debug(f"成功渲染模板: {task_name} (注入 {len(variables)} 个变量)")
        
        return rendered_prompt
    
    def validate_prompt(
        self,
        task_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        校验 Prompt 的完整性和正确性。
        
        校验项：
        1. 模板文件是否存在
        2. 模板内容是否为空
        3. 必需变量是否全部提供
        4. 变量类型是否合理
        
        Args:
            task_name: 任务名称
            variables: 要校验的变量字典
            
        Returns:
            Dict[str, Any]: 校验结果，包含以下字段：
                - valid (bool): 是否通过校验
                - errors (List[str]): 错误列表
                - warnings (List[str]): 警告列表
                - missing_vars (List[str]): 缺失的变量列表
                - template_exists (bool): 模板是否存在
                - template_empty (bool): 模板是否为空
                
        Examples:
            >>> result = manager.validate_prompt(
            ...     task_name="tech_stack",
            ...     variables={"repo_name": "my-project"}
            ... )
            >>> if not result["valid"]:
            ...     print(result["errors"])
        """
        result: Dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_vars": [],
            "template_exists": False,
            "template_empty": False,
        }
        
        # 1. 检查模板是否存在
        template_file = self.prompts_dir / f"{task_name}.md"
        if not template_file.exists():
            result["valid"] = False
            result["template_exists"] = False
            error_msg = f"模板文件不存在: {template_file}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
            return result
        
        result["template_exists"] = True
        
        # 2. 加载模板并检查是否为空
        try:
            template_content = self.load_template(task_name)
            if not template_content.strip():
                result["valid"] = False
                result["template_empty"] = True
                error_msg = f"模板内容为空: {task_name}"
                result["errors"].append(error_msg)
                logger.error(error_msg)
                return result
        except Exception as e:
            result["valid"] = False
            error_msg = f"加载模板失败: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(error_msg)
            return result
        
        # 3. 检查变量是否缺失
        if variables:
            required_vars = self._extract_variables(template_content)
            provided_vars = set(variables.keys())
            missing_vars = required_vars - provided_vars
            
            if missing_vars:
                result["missing_vars"] = list(missing_vars)
                warning_msg = f"缺少变量: {', '.join(missing_vars)}"
                result["warnings"].append(warning_msg)
                logger.warning(warning_msg)
                # 变量缺失不算致命错误，仅警告
        
        # 4. 检查变量类型（可选扩展）
        if variables:
            for var_name, var_value in variables.items():
                if var_value is None:
                    warning_msg = f"变量 '{var_name}' 的值为 None"
                    result["warnings"].append(warning_msg)
                    logger.debug(warning_msg)
        
        logger.info(f"Prompt 校验完成: {task_name} - 有效: {result['valid']}")
        
        return result
    
    def preview_prompt(
        self,
        task_name: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        预览最终生成的 Prompt（用于调试）。
        
        打印渲染后的完整 Prompt 到控制台，方便开发者调试和验证。
        
        Args:
            task_name: 任务名称
            variables: 要注入的变量字典
            
        Examples:
            >>> manager.preview_prompt(
            ...     task_name="tech_stack",
            ...     variables={"repo_name": "my-project"}
            ... )
        """
        try:
            # 构建 Prompt
            final_prompt = self.build_prompt(task_name, variables)
            
            # 打印分隔线
            logger.info("=" * 80)
            logger.info(f"Prompt 预览: {task_name}")
            logger.info("=" * 80)
            
            # 打印变量信息
            if variables:
                logger.info(f"注入变量: {list(variables.keys())}")
                logger.info("-" * 80)
            
            # 打印 Prompt 内容
            print(final_prompt)
            
            # 打印统计信息
            logger.info("-" * 80)
            logger.info(f"Prompt 长度: {len(final_prompt)} 字符")
            logger.info(f"预估 Token 数: {len(final_prompt) // 4} (粗略估算)")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"预览 Prompt 失败: {str(e)}")
            raise
    
    def _extract_variables(self, template_content: str) -> Set[str]:
        """
        从模板内容中提取所有变量占位符。
        
        支持 Jinja2 风格的变量语法：{{ variable_name }}
        
        Args:
            template_content: 模板内容字符串
            
        Returns:
            Set[str]: 变量名称集合
            
        Examples:
            >>> vars = manager._extract_variables("Hello {{ name }}, welcome to {{ place }}")
            >>> print(vars)  # {'name', 'place'}
        """
        # 正则表达式匹配 {{ variable_name }} 格式
        pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"
        matches = re.findall(pattern, template_content)
        return set(matches)
    
    def list_available_templates(self) -> List[str]:
        """
        列出所有可用的 Prompt 模板。
        
        扫描 prompts 目录，返回所有 .md 文件的名称（不含扩展名）。
        
        Returns:
            List[str]: 模板名称列表，按字母顺序排序
            
        Examples:
            >>> templates = manager.list_available_templates()
            >>> print(templates)
            ['architecture_diagram', 'config_analysis', 'core_modules', ...]
        """
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts 目录不存在: {self.prompts_dir}")
            return []
        
        # 查找所有 .md 文件
        template_files = list(self.prompts_dir.glob("*.md"))
        
        # 提取文件名（不含扩展名）并排序
        template_names = sorted([f.stem for f in template_files])
        
        logger.debug(f"找到 {len(template_names)} 个模板: {template_names}")
        
        return template_names
    
    def get_template_metadata(self, template_name: str) -> Dict[str, Any]:
        """
        获取模板的元数据信息。
        
        包括：
        - 文件路径
        - 文件大小
        - 最后修改时间
        - 变量列表
        - 版本号（如果定义了）
        
        Args:
            template_name: 模板名称
            
        Returns:
            Dict[str, Any]: 元数据字典，包含：
                - name (str): 模板名称
                - path (Path): 文件路径
                - size (int): 文件大小（字节）
                - exists (bool): 文件是否存在
                - variables (List[str]): 变量列表
                - version (str): 版本号（如果有）
                
        Examples:
            >>> metadata = manager.get_template_metadata("tech_stack")
            >>> print(metadata["size"])
        """
        template_file = self.prompts_dir / f"{template_name}.md"
        
        metadata: Dict[str, Any] = {
            "name": template_name,
            "path": template_file,
            "exists": template_file.exists(),
            "size": 0,
            "variables": [],
            "version": self.template_versions.get(template_name, "1.0.0"),
        }
        
        if template_file.exists():
            # 获取文件大小
            metadata["size"] = template_file.stat().st_size
            
            # 读取内容并提取变量
            try:
                content = template_file.read_text(encoding="utf-8")
                metadata["variables"] = list(self._extract_variables(content))
            except Exception as e:
                logger.warning(f"读取模板元数据失败: {str(e)}")
        
        return metadata
    
    def reload_template(self, template_name: str) -> None:
        """
        重新加载指定模板（清除缓存）。
        
        用于模板文件更新后，强制重新读取最新内容。
        
        Args:
            template_name: 模板名称
            
        Examples:
            >>> manager.reload_template("tech_stack")
        """
        # 从缓存中移除
        if template_name in self.templates:
            del self.templates[template_name]
            logger.debug(f"已清除模板缓存: {template_name}")
        
        # 重新加载
        self.load_template(template_name)
        logger.info(f"已重新加载模板: {template_name}")
    
    def validate_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        批量校验所有模板。
        
        Returns:
            Dict[str, Dict[str, Any]]: 每个模板的校验结果
            
        Examples:
            >>> results = manager.validate_all_templates()
            >>> for name, result in results.items():
            ...     print(f"{name}: {result['valid']}")
        """
        template_names = self.list_available_templates()
        results: Dict[str, Dict[str, Any]] = {}
        
        for template_name in template_names:
            results[template_name] = self.validate_prompt(template_name)
        
        # 统计结果
        valid_count = sum(1 for r in results.values() if r["valid"])
        total_count = len(results)
        
        logger.info(f"模板批量校验完成: {valid_count}/{total_count} 有效")
        
        return results
