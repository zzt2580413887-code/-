from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict

from backend.app.services.cancellation import OperationCancelledError, cancellation_service
from backend.app.services.document import document_service
from backend.app.services.search import search_service

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parents[3]
METADATA_FILE = ROOT_DIR / "backend" / "data" / "metadata.json"


class Message(BaseModel):
    role: str
    content: str
    model_config = ConfigDict(protected_namespaces=())

class ChatService:
    def __init__(self) -> None:
        default_api_key = os.getenv("OPENAI_API_KEY", "")
        default_base_url = os.getenv("OPENAI_BASE_URL", "")
        self.default_api_key = default_api_key
        self.default_base_url = default_base_url
        self.cloud_client = AsyncOpenAI(api_key=default_api_key, base_url=default_base_url)

        # DashScope配置（用于Qwen模型）
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.dashscope_base_url = os.getenv("DASHSCOPE_BASE_URL", "")

        self.model_settings: Dict[str, Dict[str, Any]] = {
            "qwen": {
                "model": "qwen-max-latest",
                "supports_web_search": True,
                "api_key": self.dashscope_api_key,
                "base_url": self.dashscope_base_url,
            },
            "gpt": {
                "model": "gpt-4o",
                "api_key": os.getenv("GPT_API_KEY", ""),
                "base_url": os.getenv("GPT_BASE_URL", ""),
            },
            "gemini": {"model": "gemini-2.5-pro"},
            "grok": {"model": "grok-4-0709"},
            "custom": {"model": "", "supports_web_search": False},
        }
        self.base_system_prompt = (
            "你是由山东大学政治学与公共管理学院团队打造的城市治理研究助手。"
            "你的回答应简洁流畅，语言规范严谨；不确定时请如实说明。"
        )
        self._reset_history()

    def _reset_history(self) -> None:
        self.conversation_history: List[Message] = [
            Message(role="system", content=self.base_system_prompt)
        ]

    def _trim_history(self, max_rounds: int = 10) -> None:
        max_messages = 1 + max_rounds * 2
        if len(self.conversation_history) > max_messages:
            self.conversation_history = [
                self.conversation_history[0],
                *self.conversation_history[-(max_messages - 1):],
            ]

    def _resolve_runtime_client(self, cloud_config: Optional[Dict[str, Any]]) -> AsyncOpenAI:
        """
        Build an AsyncOpenAI client using runtime configuration, falling back to the
        default client when no overrides are provided.
        """
        api_key = (cloud_config or {}).get("api_key") or getattr(
            self.cloud_client, "api_key", None
        )
        base_url = (cloud_config or {}).get("base_url") or getattr(
            self.cloud_client, "base_url", None
        )

        if not api_key or not base_url:
            raise ValueError("云端模型缺少 API KEY 或 Base URL，请先完成配置。")

        if (
            api_key == getattr(self.cloud_client, "api_key", None)
            and base_url == getattr(self.cloud_client, "base_url", None)
        ):
            return self.cloud_client

        return AsyncOpenAI(api_key=api_key, base_url=base_url)

    @staticmethod
    def _load_document_metadata(library_type: str = "public") -> Dict[str, Dict[str, Any]]:
        """
        加载文档metadata

        Args:
            library_type: "public" 或 "private"
        """
        if library_type == "public":
            metadata_file = ROOT_DIR / "backend" / "data" / "public" / "metadata.json"
        else:
            metadata_file = ROOT_DIR / "backend" / "data" / "private" / "metadata.json"

        if not metadata_file.exists():
            return {}

        try:
            with open(metadata_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            # 私人库的metadata结构包含knowledge_groups和documents
            if library_type == "private":
                documents = data.get("documents", {})
            else:
                # 公共库的metadata可能是旧格式或新格式
                if isinstance(data, dict) and "documents" in data:
                    documents = data["documents"]
                else:
                    documents = data  # 兼容旧格式

            return documents if isinstance(documents, dict) else {}

        except Exception as exc:  # pragma: no cover - 仅日志
            LOGGER.error("读取 %s metadata.json 失败: %s", library_type, exc)
            return {}

    async def get_response(
        self,
        message: str,
        llm_type: Literal["qwen", "gpt", "gemini", "grok", "custom", "local"] = "qwen",
        enable_rag: bool = False,
        enable_web_search: bool = False,
        cancel_tokens: Optional[List[Optional[str]]] = None,
        cloud_config: Optional[Dict[str, Any]] = None,
        library_type: Optional[str] = None,
        knowledge_group_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        cancel_tokens = [token for token in (cancel_tokens or []) if token]
        try:
            llm_choice = (llm_type or "qwen").lower()
            if llm_choice == "local":
                LOGGER.warning("微调模型(测试)已禁用，忽略此次请求")
                raise ValueError("微调模型(测试)暂不可用，请选择其他模型。")

            if llm_choice not in self.model_settings:
                LOGGER.warning("未识别的模型类型 %s，默认使用 qwen", llm_choice)
                llm_choice = "qwen"

            model_info = self.model_settings[llm_choice]
            override_model = (cloud_config or {}).get("general_model")
            selected_model = override_model or model_info.get("model", "")
            if not selected_model:
                raise ValueError("请提供用于对话的通用模型名称。")

            supports_web_search = bool(model_info.get("supports_web_search", False))
            runtime_config = dict(cloud_config or {})
            if not runtime_config.get("api_key") and model_info.get("api_key"):
                runtime_config["api_key"] = model_info["api_key"]
            if not runtime_config.get("base_url") and model_info.get("base_url"):
                runtime_config["base_url"] = model_info["base_url"]

            client_config = runtime_config if runtime_config else None
            client = self._resolve_runtime_client(client_config)

            await cancellation_service.raise_if_cancelled(*cancel_tokens)

            LOGGER.info(
                "开始处理请求: llm_type=%s, model=%s, enable_web_search=%s",
                llm_choice,
                selected_model,
                enable_web_search,
            )

            # 文档检索
            relevant_texts: List[Any] = []
            if enable_rag and len(message.strip()) > 10:
                LOGGER.info("开始文档检索: library_type=%s, groups=%s", library_type, knowledge_group_ids)
                await cancellation_service.raise_if_cancelled(*cancel_tokens)
                try:
                    relevant_texts = await cancellation_service.wait_or_cancel(
                        document_service.search_similar_texts(
                            query=message,
                            k=3,
                            library_type=library_type,
                            knowledge_group_ids=knowledge_group_ids
                        ),
                        cancel_tokens
                    )
                    relevant_texts = list(relevant_texts or [])[:3]
                    LOGGER.info("文档检索完成，检索到 %d 条相关文档片段", len(relevant_texts))
                except Exception as exc:
                    LOGGER.error("文档检索失败: %s", exc, exc_info=True)
                    # 文档检索失败不应该中断整个流程
                    relevant_texts = []

            # 网页搜索
            web_search_results: List[Dict[str, Any]] = []
            if enable_web_search:
                LOGGER.info("开始网页搜索")
                await cancellation_service.raise_if_cancelled(*cancel_tokens)
                try:
                    search_response = await cancellation_service.wait_or_cancel(
                        search_service.search(message),
                        cancel_tokens
                    )
                    organic = search_response.get("organic") or []
                    LOGGER.info("网页搜索返回 %d 条原始结果", len(organic))
                    for item in organic[:3]:  # 取前3条结果
                        title = (item.get("title") or "").strip() or "未命名结果"
                        snippet = (
                            item.get("snippet")
                            or item.get("description")
                            or item.get("summary")
                            or ""
                        ).strip()
                        url = (item.get("link") or item.get("url") or "").strip()
                        summary = f"{title}: {snippet}" if snippet else title
                        web_search_results.append({
                            "title": title,
                            "content": summary,
                            "url": url or title,
                            "type": "web_search",
                        })
                    LOGGER.info("网页搜索完成，整理后 %d 条结果", len(web_search_results))
                except Exception as exc:
                    LOGGER.error("网页搜索失败: %s", exc, exc_info=True)
                    # 网页搜索失败不应该中断整个流程
                    web_search_results = []

            system_prompt = self.base_system_prompt + ("")
            self.conversation_history[0].content = system_prompt

            # 构建用户消息，包含搜索结果上下文
            user_content = message
            context_parts = []

            # 添加文档检索上下文
            if relevant_texts:
                doc_context = "【知识库检索结果】\n"
                for idx, item in enumerate(relevant_texts, 1):
                    if isinstance(item, dict):
                        content = item.get("content", "")
                        source = item.get("source", "未知来源")
                    else:
                        content = str(item)
                        source = "未知来源"
                    doc_context += f"{idx}. 来源：{source}\n{content}\n\n"
                context_parts.append(doc_context.strip())

            # 添加网页搜索上下文
            if web_search_results:
                web_context = "【网页搜索结果】\n"
                for idx, result in enumerate(web_search_results, 1):
                    title = result.get("title", "")
                    url = result.get("url", "")
                    content = result.get("content", "")
                    web_context += f"{idx}. 标题：{title}\n链接：{url}\n摘要：{content}\n\n"
                context_parts.append(web_context.strip())

            # 如果有上下文，将其添加到用户消息前面
            if context_parts:
                full_context = "\n\n".join(context_parts)
                user_content = f"{full_context}\n\n【用户问题】\n{message}"

            user_message = Message(role="user", content=user_content)
            self.conversation_history.append(user_message)

            request_kwargs: Dict[str, Any] = {
                "model": selected_model,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in self.conversation_history
                ],
            }

            # 同时启用模型内置搜索和系统搜索，获得更全面的信息
            # 系统搜索结果已添加到上下文中，模型可以在此基础上补充更多信息
            if enable_web_search and supports_web_search:
                request_kwargs["extra_body"] = {"enable_search": True, "forced_search": True}
                LOGGER.info("已启用模型内置搜索功能")

            completion = await cancellation_service.wait_or_cancel(
                client.chat.completions.create(**request_kwargs),
                cancel_tokens,
            )
            response_text = completion.choices[0].message.content.strip()

            LOGGER.info("云端模型生成回复完成")
            assistant_message = Message(role="assistant", content=response_text)
            self.conversation_history.append(assistant_message)
            self._trim_history()

            # 合并文档引用和网页搜索结果
            references: Optional[List[Dict[str, Any]]] = None
            all_references: List[Dict[str, Any]] = []

            # 添加文档引用
            if relevant_texts:
                # 加载公共库和私人库的metadata
                public_metadata = self._load_document_metadata("public")
                private_metadata = self._load_document_metadata("private")

                for idx, item in enumerate(relevant_texts):
                    if isinstance(item, dict):
                        filename = item.get("source")
                        snippet = item.get("content", "")
                        chunk_index = item.get("chunk_index")
                        item_library_type = item.get("library_type")
                    else:
                        filename = None
                        snippet = str(item)
                        chunk_index = None
                        item_library_type = "public"

                    # 根据library_type从对应的metadata中获取
                    if item_library_type == "private":
                        meta = private_metadata.get(filename or "", {}) if filename else {}
                    else:
                        meta = public_metadata.get(filename or "", {}) if filename else {}

                    title = meta.get("title") or filename or f"参考资料 {idx + 1}"

                    # 构建reference，包含所有可能的metadata字段
                    reference = {
                        "title": title,
                        "content": snippet,
                        "filename": filename,
                        "category": meta.get("category"),
                        "tags": meta.get("tags"),
                        "size": meta.get("size"),
                        "upload_time": meta.get("upload_time"),
                        "chunk_index": chunk_index,
                        "library_type": item.get("library_type"),
                        "knowledge_group_id": item.get("knowledge_group_id"),
                        "knowledge_group_name": item.get("knowledge_group_name"),
                        "score": item.get("score"),  # 相似度分数
                    }

                    # 添加分类特定字段
                    if meta.get("category") == "政策":
                        reference["effectiveness_level"] = meta.get("effectiveness_level")
                        reference["document_type"] = meta.get("document_type")
                    elif meta.get("category") == "论文":
                        reference["discipline"] = meta.get("discipline")
                        reference["main_topic"] = meta.get("main_topic")
                    elif meta.get("category") == "案例":
                        reference["region"] = meta.get("region")
                        reference["main_topic"] = meta.get("main_topic")

                    all_references.append(reference)

            # 添加网页搜索结果
            if web_search_results:
                all_references.extend(web_search_results)

            if all_references:
                references = all_references

            return {
                "response": response_text,
                "references": references,
            }

        except OperationCancelledError:
            if self.conversation_history and self.conversation_history[-1].role == "user":
                self.conversation_history.pop()
            LOGGER.info("对话请求被用户取消")
            raise
        except Exception as exc:
            if self.conversation_history and self.conversation_history[-1].role == "user":
                self.conversation_history.pop()
            LOGGER.error("获取回复失败: %s", exc, exc_info=True)
            raise Exception(f"获取回复失败: {str(exc)}") from exc

    def clear_history(self) -> None:
        self._reset_history()


chat_service = ChatService()
