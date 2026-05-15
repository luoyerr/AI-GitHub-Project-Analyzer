"""
上下文文件读取器 - 安全文件读取模块。

负责安全地读取文件内容，处理编码问题、大文件限制、二进制文件检测等。
确保在读取过程中不会引发异常或安全风险。

本模块仅负责文件读取，不包含：
- 文件筛选逻辑
- 文件排序逻辑
- Token 计算
- 裁剪逻辑
- AI 分析
"""

from pathlib import Path
from typing import Optional

from loguru import logger

from .models import FileReadResult


# 二进制文件扩展名白名单（禁止读取）
BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".zip",
    ".exe",
    ".dll",
    ".jar",
    ".woff",
    ".so",
}

# 支持的文件编码列表（按优先级排序）
SUPPORTED_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "gbk",
    "gb2312",
    "gb18030",
    "big5",
    "latin1",
    "cp1252",
]

# 文件大小限制：500KB
MAX_FILE_SIZE_NORMAL = 500 * 1024  # 500KB

# 最大读取行数限制
MAX_LINES_LIMIT = 300


class ContextFileReader:
    """
    上下文文件读取器 - 安全文件读取。

    职责：
        安全地读取文件内容，处理各种边界情况和异常。
        支持编码检测、大文件限制、二进制文件过滤等功能。

    安全特性：
        1. UTF-8 编码优先，支持多种编码自动检测
        2. 大文件限制（默认最大 500KB）
        3. 二进制文件检测和过滤
        4. 乱码处理和容错
        5. 路径安全检查

    使用示例：
        >>> reader = ContextFileReader()
        >>> result = reader.read(Path("example.py"))
        >>> if result:
        ...     print(result.content)
    """

    def __init__(self, max_file_size: int = MAX_FILE_SIZE_NORMAL) -> None:
        """
        初始化上下文文件读取器。

        参数：
            max_file_size: 单个文件最大读取字节数，默认 500KB
        """
        self.max_file_size = max_file_size
        logger.debug("初始化 ContextFileReader，最大文件大小: {} KB", max_file_size // 1024)

    def read(self, file_path: Path) -> Optional[FileReadResult]:
        """
        读取单个文件的总入口方法。

        流程：
            1. 检查文件是否存在
            2. 验证文件大小
            3. 检测是否为二进制文件
            4. 自动检测文件编码
            5. 安全读取文件内容
            6. 返回 FileReadResult 或 None

        参数：
            file_path: 要读取的文件路径

        返回：
            FileReadResult 对象，包含文件内容和元数据；
            如果读取失败或文件不安全，返回 None

        注意：
            此方法只负责编排流程，不执行具体读取逻辑。
            所有异常都会被捕获并记录日志，不会抛出异常。
        """
        try:
            # 步骤 1: 检查文件是否存在
            if not file_path.exists():
                logger.warning("文件不存在: {}", file_path)
                return None

            if not file_path.is_file():
                logger.warning("路径不是文件: {}", file_path)
                return None

            # 步骤 2: 验证文件大小
            size_validation = self._validate_size(file_path)
            if size_validation is None:
                logger.warning("文件大小验证失败: {}", file_path)
                return None

            file_size, is_limited_mode = size_validation

            # 步骤 3: 检测是否为二进制文件
            if self._is_binary_file(file_path):
                logger.info("跳过二进制文件: {}", file_path)
                return None

            # 步骤 4: 读取文本内容（包含编码检测和安全读取）
            read_result = self._read_text(file_path, is_limited_mode)

            if read_result is None:
                logger.warning("读取文件失败: {}", file_path)
                return None

            logger.success(
                "读取文件成功: {}, 编码: {}, 大小: {} bytes, 截断: {}",
                file_path,
                read_result.encoding,
                read_result.size,
                read_result.is_truncated,
            )

            return read_result

        except Exception as e:
            logger.error("读取文件时发生未预期错误: {}, 错误: {}", file_path, e)
            return None

    def _detect_encoding(self, file_path: Path) -> str:
        """
        自动检测文件编码。

        策略：
            1. 优先使用 charset-normalizer 库进行智能检测
            2. 如果检测失败，依次尝试支持的编码列表
            3. 最终回退到 utf-8

        支持的编码：
            - utf-8
            - utf-8-sig
            - gbk
            - gb2312
            - gb18030
            - big5
            - latin1
            - cp1252

        参数：
            file_path: 要检测编码的文件路径

        返回：
            检测到的文件编码字符串，默认为 utf-8

        注意：
            此方法不会抛出异常，任何错误都会导致返回默认编码 utf-8。
        """
        try:
            # 尝试使用 charset-normalizer 进行智能检测
            try:
                import charset_normalizer  # type: ignore[import-not-found]

                matches = charset_normalizer.from_path(file_path)
                best_match = matches.best()

                if best_match:
                    detected_encoding = str(best_match.encoding)
                    logger.debug("charset-normalizer 检测到编码: {}", detected_encoding)

                    # 验证检测到的编码是否在支持列表中
                    if detected_encoding.lower() in [
                        enc.lower() for enc in SUPPORTED_ENCODINGS
                    ]:
                        return detected_encoding

            except ImportError:
                logger.debug("charset-normalizer 未安装，使用回退策略")
            except Exception as e:
                logger.debug("charset-normalizer 检测失败: {}", e)

            # 回退策略：依次尝试支持的编码
            logger.debug("使用回退策略检测编码: {}", file_path)

            # 读取少量字节用于编码测试
            sample_bytes = file_path.read_bytes()[:4096]

            for encoding in SUPPORTED_ENCODINGS:
                try:
                    sample_bytes.decode(encoding)
                    logger.debug("成功使用编码: {}", encoding)
                    return encoding
                except (UnicodeDecodeError, LookupError):
                    continue

            # 所有编码都失败，返回默认编码
            logger.warning("无法检测文件编码，使用默认编码 utf-8: {}", file_path)
            return "utf-8"

        except Exception as e:
            logger.error("编码检测过程出错: {}, 错误: {}", file_path, e)
            return "utf-8"

    def _safe_read(
        self, file_path: Path, encoding: str, is_limited_mode: bool = False
    ) -> Optional[str]:
        """
        安全读取文件内容。

        特性：
            1. 使用 errors="replace" 避免 UnicodeDecodeError
            2. 大文件保护：限制模式只读取前 300 行
            3. 逐行读取，避免一次性加载大文件到内存
            4. 自动处理各种编码错误

        参数：
            file_path: 要读取的文件路径
            encoding: 文件编码
            is_limited_mode: 是否启用限制模式（大文件时启用）

        返回：
            文件文本内容，读取失败返回 None

        注意：
            此方法不会抛出异常，所有错误都会被捕获并返回 None。
        """
        try:
            content_lines = []
            line_count = 0

            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                for line in f:
                    # 限制模式下最多读取 300 行
                    if is_limited_mode and line_count >= MAX_LINES_LIMIT:
                        logger.info(
                            "大文件限制模式，已读取 {} 行，停止读取: {}",
                            MAX_LINES_LIMIT,
                            file_path,
                        )
                        break

                    content_lines.append(line)
                    line_count += 1

                    # 非限制模式也设置一个安全上限，防止极端情况
                    if not is_limited_mode and line_count > 10000:
                        logger.warning(
                            "文件行数过多，已读取 {} 行，强制停止: {}",
                            line_count,
                            file_path,
                        )
                        break

            content = "".join(content_lines)
            logger.debug("安全读取完成: {}, 行数: {}", file_path, line_count)
            return content

        except Exception as e:
            logger.error("安全读取文件失败: {}, 错误: {}", file_path, e)
            return None

    def _read_text(
        self, file_path: Path, is_limited_mode: bool = False
    ) -> Optional[FileReadResult]:
        """
        统一文本读取方法。

        封装了编码检测和安全读取的完整流程：
            1. 获取文件大小
            2. 检测文件编码
            3. 安全读取内容
            4. 构建 FileReadResult 对象

        参数：
            file_path: 要读取的文件路径
            is_limited_mode: 是否启用限制模式（大文件时启用）

        返回：
            FileReadResult 对象，包含文件内容、编码、截断状态等信息；
            读取失败返回 None

        注意：
            此方法是 _detect_encoding 和 _safe_read 的统一封装。
        """
        try:
            # 获取文件大小
            file_size = file_path.stat().st_size

            # 检测编码
            encoding = self._detect_encoding(file_path)
            logger.debug("文件编码检测结果: {}, 编码: {}", file_path, encoding)

            # 安全读取内容
            content = self._safe_read(file_path, encoding, is_limited_mode)

            if content is None:
                logger.warning("读取文件内容为空: {}", file_path)
                return None

            # 判断是否被截断
            is_truncated = is_limited_mode
            truncated_reason = None

            if is_limited_mode:
                truncated_reason = f"文件大小超过 {self.max_file_size // 1024}KB 限制，仅读取前 {MAX_LINES_LIMIT} 行"

            # 构建返回结果
            result = FileReadResult(
                content=content,
                encoding=encoding,
                is_truncated=is_truncated,
                truncated_reason=truncated_reason,
                size=file_size,
            )

            logger.debug(
                "构建 FileReadResult 成功: {}, 编码: {}, 截断: {}",
                file_path,
                encoding,
                is_truncated,
            )

            return result

        except Exception as e:
            logger.error("统一文本读取失败: {}, 错误: {}", file_path, e)
            return None

    def _is_binary_file(self, file_path: Path) -> bool:
        """
        检测文件是否为二进制文件。

        检测方法：
            1. 检查文件扩展名是否在二进制白名单中
            2. 对于未知扩展名的文件，通过读取文件头部字节判断

        禁止读取的二进制类型：
            - 图片: png, jpg, jpeg, gif
            - 文档: pdf
            - 压缩: zip
            - 可执行: exe, dll, jar, so
            - 字体: woff

        参数：
            file_path: 要检测的文件路径

        返回：
            True 表示是二进制文件（应跳过），False 表示是文本文件（可读取）

        注意：
            此方法不会抛出异常，任何错误都会返回 False（允许读取）。
        """
        try:
            # 方法 1: 检查文件扩展名
            suffix = file_path.suffix.lower()
            if suffix in BINARY_EXTENSIONS:
                logger.debug("检测到二进制文件扩展名: {}", suffix)
                return True

            # 方法 2: 对于没有扩展名或未知扩展名的文件，检查文件头部
            # 读取前 8192 字节进行检测
            try:
                with open(file_path, "rb") as f:
                    chunk = f.read(8192)

                if not chunk:
                    # 空文件视为文本文件
                    return False

                # 检查是否包含 null 字节（二进制文件的典型特征）
                if b"\x00" in chunk:
                    logger.debug("检测到 null 字节，判定为二进制文件: {}", file_path)
                    return True

                # 尝试使用多种编码解码，如果任一成功则视为文本文件
                for encoding in ["utf-8", "gbk", "latin1"]:
                    try:
                        chunk.decode(encoding)
                        logger.debug(
                            "成功使用 {} 解码，判定为文本文件: {}",
                            encoding,
                            file_path,
                        )
                        return False
                    except UnicodeDecodeError:
                        continue

                # 所有编码都失败，进一步检查：计算可打印字符比例
                text_chars = sum(
                    1 for byte in chunk if 32 <= byte <= 126 or byte in (9, 10, 13)
                )
                printable_ratio = text_chars / len(chunk)

                # 如果可打印字符比例低于 30%，判定为二进制
                # 降低阈值以避免误判编码文件
                if printable_ratio < 0.3:
                    logger.debug(
                        "可打印字符比例过低 ({:.2%})，判定为二进制文件: {}",
                        printable_ratio,
                        file_path,
                    )
                    return True

                # 否则视为文本文件
                logger.debug(
                    "可打印字符比例 {:.2%}，判定为文本文件: {}",
                    printable_ratio,
                    file_path,
                )
                return False

            except Exception as e:
                logger.debug("二进制检测过程出错，保守处理: {}, 错误: {}", file_path, e)
                # 检测出错时，保守地认为是文本文件
                return False

            return False

        except Exception as e:
            logger.error("二进制文件检测失败: {}, 错误: {}", file_path, e)
            # 检测失败时，允许读取（保守策略）
            return False

    def _validate_size(self, file_path: Path) -> Optional[tuple[int, bool]]:
        """
        验证文件大小并确定读取模式。

        规则：
            - 文件大小 <= 500KB: 正常模式，读取全部内容
            - 文件大小 > 500KB: 限制模式，仅读取前 300 行

        参数：
            file_path: 要验证的文件路径

        返回：
            元组 (file_size, is_limited_mode)：
                - file_size: 文件实际大小（字节）
                - is_limited_mode: 是否启用限制模式
            如果文件不存在或无法访问，返回 None

        注意：
            此方法不会抛出异常，任何错误都会返回 None。
        """
        try:
            # 获取文件大小
            file_size = file_path.stat().st_size

            # 检查文件大小
            if file_size == 0:
                logger.debug("文件大小为 0: {}", file_path)
                return (0, False)

            # 判断是否超过限制
            is_limited_mode = file_size > self.max_file_size

            if is_limited_mode:
                logger.info(
                    "文件大小 {} KB 超过限制 {} KB，启用限制模式: {}",
                    file_size // 1024,
                    self.max_file_size // 1024,
                    file_path,
                )
            else:
                logger.debug(
                    "文件大小 {} KB 在限制范围内: {}",
                    file_size // 1024,
                    file_path,
                )

            return (file_size, is_limited_mode)

        except FileNotFoundError:
            logger.warning("文件不存在，无法验证大小: {}", file_path)
            return None
        except PermissionError:
            logger.warning("没有权限访问文件: {}", file_path)
            return None
        except Exception as e:
            logger.error("文件大小验证失败: {}, 错误: {}", file_path, e)
            return None
