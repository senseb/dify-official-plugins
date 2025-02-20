from collections.abc import Generator
from typing import Optional, Union
from dify_plugin import OAICompatLargeLanguageModel
from dify_plugin.entities.model import ModelFeature
from dify_plugin.entities.model.llm import LLMMode, LLMResult
from dify_plugin.entities.model.message import PromptMessage, PromptMessageTool


class GiteeAILargeLanguageModel(OAICompatLargeLanguageModel):
    MODEL_TO_IDENTITY: dict[str, str] = {
        "Yi-1.5-34B-Chat": "Yi-34B-Chat",
        "deepseek-coder-33B-instruct-completions": "deepseek-coder-33B-instruct",
        "deepseek-coder-33B-instruct-chat": "deepseek-coder-33B-instruct",
    }

    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator]:
        self._add_custom_parameters(credentials, model, model_parameters)
        return super()._invoke(model, credentials, prompt_messages, model_parameters, tools, stop, stream, user)

    def validate_credentials(self, model: str, credentials: dict) -> None:
        self._add_custom_parameters(credentials, model, None)
        super().validate_credentials(model, credentials)

    def _add_custom_parameters(self, credentials: dict, model: str, model_parameters: dict) -> None:
        if model is None:
            model = "bge-large-zh-v1.5"
        model_identity = GiteeAILargeLanguageModel.MODEL_TO_IDENTITY.get(model, model)
        credentials["endpoint_url"] = f"https://ai.gitee.com/api/serverless/{model_identity}/"
        if model.endswith("completions"):
            credentials["mode"] = LLMMode.COMPLETION.value
        else:
            credentials["mode"] = LLMMode.CHAT.value
        schema = self.get_model_schema(model, credentials)
        if ModelFeature.TOOL_CALL in schema.features or ModelFeature.MULTI_TOOL_CALL in schema.features:
            credentials["function_calling_type"] = "tool_call"
