# from typing import Literal, Type

# from openai import AsyncOpenAI, pydantic_function_tool

# from sgr_agent_core.agent_config import AgentConfig
# from sgr_agent_core.base_agent import BaseAgent
# from sgr_agent_core.models import AgentStatesEnum
# from sgr_agent_core.tools import (
#     BaseTool,
#     FinalAnswerTool,
#     ReasoningTool,
# )


# class SGRToolCallingAgent(BaseAgent):
#     """Agent that uses OpenAI native function calling to select and execute
#     tools based on SGR like a reasoning scheme."""

#     name: str = "sgr_tool_calling_agent"

#     def __init__(
#         self,
#         task_messages: list,
#         openai_client: AsyncOpenAI,
#         agent_config: AgentConfig,
#         toolkit: list[Type[BaseTool]],
#         def_name: str | None = None,
#         **kwargs: dict,
#     ):
#         super().__init__(
#             task_messages=task_messages,
#             openai_client=openai_client,
#             agent_config=agent_config,
#             toolkit=toolkit,
#             def_name=def_name,
#             **kwargs,
#         )
#         self.tool_choice: Literal["required"] = "required"
#         print("openai_client.base_url=", getattr(self.openai_client, "base_url", None))

    
#     def _openai_request_kwargs(self) -> dict:
#         # The SDK request methods do NOT accept provider/api_key/base_url.
#         bad_keys = {"provider", "api_key", "base_url"}
#         return {k: v for k, v in self.config.llm.to_openai_client_kwargs().items() if k not in bad_keys}

#     async def _reasoning_phase(self) -> ReasoningTool:
#         # async with self.openai_client.chat.completions.stream(
#         #     messages=await self._prepare_context(),
#         #     tools=[pydantic_function_tool(ReasoningTool, name=ReasoningTool.tool_name)],
#         #     tool_choice={"type": "function", "function": {"name": ReasoningTool.tool_name}},
#         #     **self.config.llm.to_openai_client_kwargs(),
#         # ) as stream:
#         print("openai_client.base_url=", getattr(self.openai_client, "base_url", None))
#         async with self.openai_client.chat.completions.stream(
#             messages=await self._prepare_context(),
#             tools=[pydantic_function_tool(ReasoningTool, name=ReasoningTool.tool_name)],
#             tool_choice={"type": "function", "function": {"name": ReasoningTool.tool_name}},
#             **self._openai_request_kwargs(),
#         ) as stream:
#             async for event in stream:
#                 if event.type == "chunk":
#                     self.streaming_generator.add_chunk(event.chunk)
#             reasoning: ReasoningTool = (
#                 (await stream.get_final_completion()).choices[0].message.tool_calls[0].function.parsed_arguments
#             )
#         self.conversation.append(
#             {
#                 "role": "assistant",
#                 "content": None,
#                 "tool_calls": [
#                     {
#                         "type": "function",
#                         "id": f"{self._context.iteration}-reasoning",
#                         "function": {
#                             "name": reasoning.tool_name,
#                             "arguments": reasoning.model_dump_json(),
#                         },
#                     }
#                 ],
#             }
#         )
#         tool_call_result = await reasoning(self._context)
#         self.streaming_generator.add_tool_call(
#             f"{self._context.iteration}-reasoning", reasoning.tool_name, tool_call_result
#         )
#         self.conversation.append(
#             {"role": "tool", "content": tool_call_result, "tool_call_id": f"{self._context.iteration}-reasoning"}
#         )
#         self._log_reasoning(reasoning)
#         return reasoning

#     async def _select_action_phase(self, reasoning: ReasoningTool) -> BaseTool:
#         # async with self.openai_client.chat.completions.stream(
#         #     messages=await self._prepare_context(),
#         #     tools=await self._prepare_tools(),
#         #     tool_choice=self.tool_choice,
#         #     **self.config.llm.to_openai_client_kwargs(),
#         # ) as stream:
#         async with self.openai_client.chat.completions.stream(
#             messages=await self._prepare_context(),
#             tools=await self._prepare_tools(),
#             tool_choice=self.tool_choice,
#             **self._openai_request_kwargs(),
#         ) as stream:
#             async for event in stream:
#                 if event.type == "chunk":
#                     self.streaming_generator.add_chunk(event.chunk)

#         completion = await stream.get_final_completion()

#         try:
#             tool = completion.choices[0].message.tool_calls[0].function.parsed_arguments
#         except (IndexError, AttributeError, TypeError):
#             # LLM returned a text response instead of a tool call - treat as completion
#             final_content = completion.choices[0].message.content or "Task completed successfully"
#             tool = FinalAnswerTool(
#                 reasoning="Agent decided to complete the task",
#                 completed_steps=[],
#                 answer=final_content,
#                 status=AgentStatesEnum.COMPLETED,
#             )
#         if not isinstance(tool, BaseTool):
#             raise ValueError("Selected tool is not a valid BaseTool instance")
#         self.conversation.append(
#             {
#                 "role": "assistant",
#                 "content": reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completing",
#                 "tool_calls": [
#                     {
#                         "type": "function",
#                         "id": f"{self._context.iteration}-action",
#                         "function": {
#                             "name": tool.tool_name,
#                             "arguments": tool.model_dump_json(),
#                         },
#                     }
#                 ],
#             }
#         )
#         self.streaming_generator.add_tool_call(
#             f"{self._context.iteration}-action", tool.tool_name, tool.model_dump_json()
#         )
#         return tool

#     async def _action_phase(self, tool: BaseTool) -> str:
#         result = await tool(self._context, self.config)
#         self.conversation.append(
#             {"role": "tool", "content": result, "tool_call_id": f"{self._context.iteration}-action"}
#         )
#         self.streaming_generator.add_chunk_from_str(f"{result}\n")
#         self._log_tool_execution(tool, result)
#         return result

## Non streaming GPT model compatible

# import json
# from typing import Literal, Type

# from openai import AsyncOpenAI, pydantic_function_tool

# from sgr_agent_core.agent_config import AgentConfig
# from sgr_agent_core.base_agent import BaseAgent
# from sgr_agent_core.models import AgentStatesEnum
# from sgr_agent_core.tools import (
#     BaseTool,
#     FinalAnswerTool,
#     ReasoningTool,
# )


# class SGRToolCallingAgent(BaseAgent):
#     """Agent that uses OpenAI native function calling to select and execute
#     tools based on SGR like a reasoning scheme."""

#     name: str = "sgr_tool_calling_agent"

#     def __init__(
#         self,
#         task_messages: list,
#         openai_client: AsyncOpenAI,
#         agent_config: AgentConfig,
#         toolkit: list[Type[BaseTool]],
#         def_name: str | None = None,
#         **kwargs: dict,
#     ):
#         super().__init__(
#             task_messages=task_messages,
#             openai_client=openai_client,
#             agent_config=agent_config,
#             toolkit=toolkit,
#             def_name=def_name,
#             **kwargs,
#         )
#         self.tool_choice: Literal["required"] = "required"
#         self._toolkit = toolkit

#     def _openai_request_kwargs(self) -> dict:
#         """
#         Convert config LLM settings into kwargs that are SAFE to pass into
#         OpenAI SDK request methods (chat.completions.create).

#         Important: The SDK request methods do NOT accept client-construction kwargs
#         like provider/api_key/base_url.
#         """
#         bad_keys = {"provider", "api_key", "base_url"}
#         return {
#             k: v for k, v in self.config.llm.to_openai_client_kwargs().items() if k not in bad_keys
#         }

#     def _parse_tool_call(self, tool_cls: type[BaseTool], msg) -> BaseTool:
#         """
#         Parse the first tool call's function.arguments JSON into the given Pydantic tool class.
#         Works for non-streaming chat.completions.create responses where parsed_arguments is absent.
#         """
#         if not msg.tool_calls:
#             raise ValueError("No tool_calls in model response")

#         fn = msg.tool_calls[0].function
#         args_json = getattr(fn, "arguments", None)

#         if not args_json:
#             # Sometimes arguments can be empty; treat as empty object
#             args = {}
#         else:
#             args = json.loads(args_json)

#         # pydantic v2 style
#         return tool_cls.model_validate(args)


#     def _emit_single_assistant_chunk(self, text: str | None) -> None:
#         """
#         Even when we call the LLM non-streaming, the SGR API may still respond
#         as an SSE stream. To stay compatible, we emit the final text as one chunk.
#         """
#         if text:
#             self.streaming_generator.add_chunk_from_str(text)

#     async def _reasoning_phase(self) -> ReasoningTool:
#         completion = await self.openai_client.chat.completions.create(
#             messages=await self._prepare_context(),
#             tools=[pydantic_function_tool(ReasoningTool, name=ReasoningTool.tool_name)],
#             tool_choice={"type": "function", "function": {"name": ReasoningTool.tool_name}},
#             **self._openai_request_kwargs(),
#         )

#         msg = completion.choices[0].message

#         # In forced-tool mode this is usually empty, but emit if present.
#         self._emit_single_assistant_chunk(msg.content)

#         # Expect a tool call for the ReasoningTool
#         # reasoning: ReasoningTool = msg.tool_calls[0].function.parsed_arguments
#         reasoning: ReasoningTool = self._parse_tool_call(ReasoningTool, msg)  # type: ignore[assignment]

#         # Record the tool call in conversation history
#         self.conversation.append(
#             {
#                 "role": "assistant",
#                 "content": None,
#                 "tool_calls": [
#                     {
#                         "type": "function",
#                         "id": f"{self._context.iteration}-reasoning",
#                         "function": {
#                             "name": reasoning.tool_name,
#                             "arguments": reasoning.model_dump_json(),
#                         },
#                     }
#                 ],
#             }
#         )

#         # Execute the reasoning tool
#         tool_call_result = await reasoning(self._context)

#         # Stream tool call result event (SGR internal streaming)
#         self.streaming_generator.add_tool_call(
#             f"{self._context.iteration}-reasoning",
#             reasoning.tool_name,
#             tool_call_result,
#         )

#         # Record tool output in conversation history
#         self.conversation.append(
#             {
#                 "role": "tool",
#                 "content": tool_call_result,
#                 "tool_call_id": f"{self._context.iteration}-reasoning",
#             }
#         )

#         self._log_reasoning(reasoning)
#         return reasoning

#     async def _select_action_phase(self, reasoning: ReasoningTool) -> BaseTool:
#         completion = await self.openai_client.chat.completions.create(
#             messages=await self._prepare_context(),
#             tools=await self._prepare_tools(),
#             tool_choice=self.tool_choice,
#             **self._openai_request_kwargs(),
#         )

#         msg = completion.choices[0].message

#         # If model produced visible text, emit once (optional)
#         self._emit_single_assistant_chunk(msg.content)

#         # ---- Case 1: Model returned a tool call (expected) ----
#         if msg.tool_calls and len(msg.tool_calls) > 0:
#             tc = msg.tool_calls[0]
#             tool_name = (tc.function.name or "").lower()
#             args_json = tc.function.arguments or "{}"

#             # Find tool class by tool_name
#             tool_cls: type[BaseTool] | None = None
#             # for t in self._context.toolkit:
#             for t in self._toolkit:
#                 if getattr(t, "tool_name", "").lower() == tool_name:
#                     tool_cls = t
#                     break

#             if tool_cls is None:
#                 raise ValueError(f"Unknown tool selected by model: {tc.function.name}")

#             try:
#                 args = json.loads(args_json)
#             except json.JSONDecodeError as e:
#                 raise ValueError(f"Tool arguments were not valid JSON: {args_json}") from e

#             tool = tool_cls.model_validate(args)

#         # ---- Case 2: No tool call, but model gave text -> wrap as FinalAnswerTool ----
#         else:
#             final_content = msg.content or "Task completed successfully"
#             step = reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completed"
#             tool = FinalAnswerTool(
#                 reasoning="Agent decided to complete the task",
#                 completed_steps=[step],   # must be non-empty
#                 answer=final_content,
#                 status=AgentStatesEnum.COMPLETED,
#             )

#         if not isinstance(tool, BaseTool):
#             raise ValueError("Selected tool is not a valid BaseTool instance")

#         # Record tool call
#         self.conversation.append(
#             {
#                 "role": "assistant",
#                 "content": reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completing",
#                 "tool_calls": [
#                     {
#                         "type": "function",
#                         "id": f"{self._context.iteration}-action",
#                         "function": {
#                             "name": tool.tool_name,
#                             "arguments": tool.model_dump_json(),
#                         },
#                     }
#                 ],
#             }
#         )

#         self.streaming_generator.add_tool_call(
#             f"{self._context.iteration}-action", tool.tool_name, tool.model_dump_json()
#         )

#         return tool


#     async def _action_phase(self, tool: BaseTool) -> str:
#         result = await tool(self._context, self.config)

#         # Record tool output in conversation history
#         self.conversation.append(
#             {"role": "tool", "content": result, "tool_call_id": f"{self._context.iteration}-action"}
#         )

#         # Emit tool result as part of SSE stream (single chunk)
#         self.streaming_generator.add_chunk_from_str(f"{result}\n")

#         self._log_tool_execution(tool, result)
#         return result


## Non streaming llm queue api compatible (via shim service)

# from __future__ import annotations

# import json
# import re
# from typing import Any, Dict, Literal, Optional, Type

# from openai import AsyncOpenAI
# from pydantic import BaseModel, Field

# from sgr_agent_core.agent_config import AgentConfig
# from sgr_agent_core.base_agent import BaseAgent
# from sgr_agent_core.models import AgentStatesEnum
# from sgr_agent_core.tools import BaseTool, FinalAnswerTool, ReasoningTool


# class ToolSelection(BaseModel):
#     """
#     Schema-constrained tool selection output from the local model.

#     The local model (via your queue) should return JSON like:
#       {
#         "tool_name": "finalanswertool",
#         "tool_args": { ... args for that tool ... }
#       }
#     """
#     tool_name: str = Field(..., description="Name of the tool to execute (must match BaseTool.tool_name).")
#     tool_args: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool as a JSON object.")


# class SGRToolCallingAgent(BaseAgent):
#     """
#     Replacement agent that DOES NOT rely on OpenAI native tool calling.

#     Instead it uses schema-constrained JSON outputs (response_format/json_schema) from your
#     OpenAI-compatible shim -> queue -> local model.

#     Assumption (per your note):
#       - The queue returns structured output in result.text as a JSON string
#       - Your shim returns that JSON string as the assistant 'content' in /v1/chat/completions
#     """

#     name: str = "sgr_tool_calling_agent"

#     def __init__(
#         self,
#         task_messages: list,
#         openai_client: AsyncOpenAI,
#         agent_config: AgentConfig,
#         toolkit: list[Type[BaseTool]],
#         def_name: str | None = None,
#         **kwargs: dict,
#     ):
#         super().__init__(
#             task_messages=task_messages,
#             openai_client=openai_client,
#             agent_config=agent_config,
#             toolkit=toolkit,
#             def_name=def_name,
#             **kwargs,
#         )
#         # Keep the toolkit on the instance for name->class mapping
#         self._toolkit: list[Type[BaseTool]] = toolkit

#         # Require a tool selection every time (we still allow fallback if model returns plain text)
#         self.tool_choice: Literal["required"] = "required"

#         # Build a lookup map for tool_name -> class (case-insensitive)
#         self._tool_by_name: dict[str, Type[BaseTool]] = {}
#         for t in self._toolkit:
#             name = getattr(t, "tool_name", None)
#             if isinstance(name, str) and name.strip():
#                 self._tool_by_name[name.strip().lower()] = t

#         # Ensure core tools are also resolvable (in case they aren't in toolkit list)
#         self._tool_by_name.setdefault(ReasoningTool.tool_name.lower(), ReasoningTool)  # type: ignore[arg-type]
#         self._tool_by_name.setdefault(FinalAnswerTool.tool_name.lower(), FinalAnswerTool)  # type: ignore[arg-type]

#     # -----------------------------
#     # Helpers
#     # -----------------------------
#     def _openai_request_kwargs(self) -> dict:
#         """
#         Convert config LLM settings into kwargs that are SAFE to pass into
#         OpenAI SDK request methods (chat.completions.create).

#         Important: The SDK request methods do NOT accept client-construction kwargs
#         like provider/api_key/base_url.
#         """
#         bad_keys = {"provider", "api_key", "base_url", "tools", "tool_choice"}
#         return {k: v for k, v in self.config.llm.to_openai_client_kwargs().items() if k not in bad_keys}

#     def _emit_single_assistant_chunk(self, text: str | None) -> None:
#         """
#         Even when the underlying model call is non-streaming, the SGR API may
#         respond as SSE. Emit final text as one chunk (optional).
#         """
#         if text:
#             self.streaming_generator.add_chunk_from_str(text)

#     @staticmethod
#     def _strip_code_fences(text: str) -> str:
#         """
#         If model returns ```json ... ``` or ``` ... ```, extract inner content.
#         """
#         t = text.strip()
#         # ```json\n...\n```
#         m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, flags=re.DOTALL | re.IGNORECASE)
#         return m.group(1).strip() if m else t

#     @staticmethod
#     def _best_effort_json_load(text: str) -> Any:
#         """
#         Parses JSON robustly from a model string:
#           - strips code fences
#           - tries json.loads directly
#           - if that fails, extracts the largest {...} block and tries again
#         """
#         t = SGRToolCallingAgent._strip_code_fences(text)

#         try:
#             return json.loads(t)
#         except Exception:
#             pass

#         # Best-effort: find the first '{' and last '}' and retry
#         start = t.find("{")
#         end = t.rfind("}")
#         if start != -1 and end != -1 and end > start:
#             candidate = t[start : end + 1]
#             return json.loads(candidate)

#         # If still failing, raise the original error shape
#         raise ValueError(f"Model did not return valid JSON. Raw text: {text[:500]}")

#     async def _model_json(
#         self,
#         *,
#         messages: list[dict[str, Any]],
#         json_schema: dict[str, Any],
#         schema_name: str,
#     ) -> Any:
#         """
#         Call the OpenAI-compatible shim and request schema-constrained JSON.

#         We pass response_format as a JSON schema. Your shim already forwards
#         response_format to your queue.
#         """
#         # completion = await self.openai_client.chat.completions.create(
#         #     messages=messages,
#         #     # IMPORTANT: do NOT pass tools/tool_choice; we're not using OpenAI tool calling
#         #     response_format={
#         #         "type": "json_schema",
#         #         "json_schema": {
#         #             "name": schema_name,
#         #             "schema": json_schema,
#         #             "strict": True,
#         #         },
#         #     },
#         #     **self._openai_request_kwargs(),
#         # )
#         schema_payload = {
#             "type": "json_schema",
#             "json_schema": {
#                 "name": schema_name,
#                 "schema": json_schema,
#                 "strict": True,
#             },
#         }

#         completion = await self.openai_client.chat.completions.create(
#             messages=messages,
#             extra_body={"response_format": schema_payload},
#             **self._openai_request_kwargs(),
#         )


#         msg = completion.choices[0].message
#         content = msg.content or ""
#         # content is expected to be JSON text (per your queue behavior)
#         return self._best_effort_json_load(content)

#     # -----------------------------
#     # Phases
#     # -----------------------------
#     async def _reasoning_phase(self) -> ReasoningTool:
#         """
#         Ask the model for ReasoningTool arguments as strict JSON, then execute ReasoningTool.
#         """
#         messages = await self._prepare_context()

#         reasoning_dict = await self._model_json(
#             messages=messages,
#             json_schema=ReasoningTool.model_json_schema(),
#             schema_name="ReasoningTool",
#         )

#         reasoning: ReasoningTool = ReasoningTool.model_validate(reasoning_dict)

#         # Record as a tool call (OpenAI-ish) for SGR streaming output compatibility
#         self.conversation.append(
#             {
#                 "role": "assistant",
#                 "content": None,
#                 "tool_calls": [
#                     {
#                         "type": "function",
#                         "id": f"{self._context.iteration}-reasoning",
#                         "function": {
#                             "name": reasoning.tool_name,
#                             "arguments": reasoning.model_dump_json(),
#                         },
#                     }
#                 ],
#             }
#         )

#         tool_call_result = await reasoning(self._context)

#         # Emit tool call event
#         self.streaming_generator.add_tool_call(
#             f"{self._context.iteration}-reasoning",
#             reasoning.tool_name,
#             tool_call_result,
#         )

#         # Record tool output
#         self.conversation.append(
#             {"role": "tool", "content": tool_call_result, "tool_call_id": f"{self._context.iteration}-reasoning"}
#         )

#         self._log_reasoning(reasoning)
#         return reasoning

#     async def _select_action_phase(self, reasoning: ReasoningTool) -> BaseTool:
#         """
#         Ask the model to select exactly one tool and its args using ToolSelection schema.
#         Then instantiate that tool and return it.
#         """
#         messages = await self._prepare_context()

#         selection_dict = await self._model_json(
#             messages=messages,
#             json_schema=ToolSelection.model_json_schema(),
#             schema_name="ToolSelection",
#         )

#         selection = ToolSelection.model_validate(selection_dict)
#         tool_name_key = (selection.tool_name or "").strip().lower()

#         tool_cls = self._tool_by_name.get(tool_name_key)
#         if tool_cls is None:
#             # If the model returns an unknown tool name, convert to a safe FinalAnswerTool
#             step = reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completed"
#             tool = FinalAnswerTool(
#                 reasoning=f"Model selected unknown tool '{selection.tool_name}'. Completing safely.",
#                 completed_steps=[step],
#                 answer="I couldn't map the selected tool to a known tool. Please check tool_name.",
#                 status=AgentStatesEnum.COMPLETED,
#             )
#         else:
#             try:
#                 tool = tool_cls.model_validate(selection.tool_args)
#             except Exception as e:
#                 # If args don't validate, again safely complete rather than crashing
#                 step = reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completed"
#                 tool = FinalAnswerTool(
#                     reasoning=f"Tool args validation failed for '{selection.tool_name}'. Completing safely.",
#                     completed_steps=[step],
#                     answer=f"Tool arguments were invalid: {e}",
#                     status=AgentStatesEnum.COMPLETED,
#                 )

#         if not isinstance(tool, BaseTool):
#             raise ValueError("Selected tool is not a valid BaseTool instance")

#         # Record selected action tool call (OpenAI-ish)
#         self.conversation.append(
#             {
#                 "role": "assistant",
#                 "content": reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completing",
#                 "tool_calls": [
#                     {
#                         "type": "function",
#                         "id": f"{self._context.iteration}-action",
#                         "function": {
#                             "name": tool.tool_name,
#                             "arguments": tool.model_dump_json(),
#                         },
#                     }
#                 ],
#             }
#         )

#         # Emit tool call event
#         self.streaming_generator.add_tool_call(
#             f"{self._context.iteration}-action",
#             tool.tool_name,
#             tool.model_dump_json(),
#         )
#         return tool

#     async def _action_phase(self, tool: BaseTool) -> str:
#         result = await tool(self._context, self.config)

#         # Record tool output
#         self.conversation.append(
#             {"role": "tool", "content": result, "tool_call_id": f"{self._context.iteration}-action"}
#         )

#         # Emit tool result as a chunk so clients see something in SSE
#         self.streaming_generator.add_chunk_from_str(f"{result}\n")

#         self._log_tool_execution(tool, result)
#         return result


from __future__ import annotations

import json
import re
from typing import Any, Dict, Literal, Optional, Type

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from sgr_agent_core.agent_config import AgentConfig
from sgr_agent_core.base_agent import BaseAgent
from sgr_agent_core.models import AgentStatesEnum
from sgr_agent_core.tools import BaseTool, FinalAnswerTool, ReasoningTool


collection_name=getattr(self.config.global_config, "default_memory_collection", "default")

class ToolSelection(BaseModel):
    """
    Schema-constrained tool selection output from the local model.

    Expected JSON (returned as text):
      {
        "tool_name": "finalanswertool",
        "tool_args": { ... }
      }
    """
    tool_name: str = Field(..., description="Name of the tool to execute (must match BaseTool.tool_name).")
    tool_args: Dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool as a JSON object.")


class SGRToolCallingAgent(BaseAgent):
    """
    Tool-calling agent that DOES NOT use OpenAI native tool calling.

    Instead it uses schema-constrained JSON outputs (response_format) routed through
    your OpenAI-compatible shim -> queue -> local model, where the queue returns the
    structured output in result.text as a JSON string.

    Key additions in this version:
      - Uses extra_body={"response_format": ...} so the shim actually receives response_format
      - Reduces context size aggressively (windowing + tool truncation + char budget)
      - Avoids sending tools/tool_choice to the shim (these just bloat payloads)
    """

    name: str = "sgr_tool_calling_agent"

    # ---- Context controls (tune these) ----
    _KEEP_LAST_NON_SYSTEM: int = 2         # keep last N user/assistant/tool messages (after filtering)
    _TOOL_MAX_CHARS: int = 800            # truncate each tool message content to this many chars
    _CHAR_BUDGET: int = 20_000             # total content chars budget (rough proxy for tokens)

    def __init__(
        self,
        task_messages: list,
        openai_client: AsyncOpenAI,
        agent_config: AgentConfig,
        toolkit: list[Type[BaseTool]],
        def_name: str | None = None,
        **kwargs: dict,
    ):
        super().__init__(
            task_messages=task_messages,
            openai_client=openai_client,
            agent_config=agent_config,
            toolkit=toolkit,
            def_name=def_name,
            **kwargs,
        )

        self._toolkit: list[Type[BaseTool]] = toolkit

        # Build a lookup map for tool_name -> class (case-insensitive)
        self._tool_by_name: dict[str, Type[BaseTool]] = {}
        for t in self._toolkit:
            name = getattr(t, "tool_name", None)
            if isinstance(name, str) and name.strip():
                self._tool_by_name[name.strip().lower()] = t

        # Ensure core tools always resolvable
        self._tool_by_name.setdefault(ReasoningTool.tool_name.lower(), ReasoningTool)       # type: ignore[arg-type]
        self._tool_by_name.setdefault(FinalAnswerTool.tool_name.lower(), FinalAnswerTool)   # type: ignore[arg-type]


    # -----------------------------
    # OpenAI request kwargs hygiene
    # -----------------------------
    def _openai_request_kwargs(self) -> dict:
        """
        Convert config LLM settings into kwargs safe for OpenAI SDK request methods.

        The SDK request methods do NOT accept client-construction kwargs like
        provider/api_key/base_url, and we also strip tools/tool_choice because
        this agent doesn't use OpenAI-native tool calling and these bloat the request.
        """
        bad_keys = {"provider", "api_key", "base_url", "tools", "tool_choice", "response_format"}
        raw = self.config.llm.to_openai_client_kwargs()
        return {k: v for k, v in raw.items() if k not in bad_keys}

    # -----------------------------
    # Context reduction helpers
    # -----------------------------
    def _trim_messages_window(self, messages: list[dict], keep_last_non_system: int) -> list[dict]:
        system = [m for m in messages if m.get("role") == "system"]
        non_system = [m for m in messages if m.get("role") != "system"]
        return system + non_system[-keep_last_non_system:]

    def _truncate_tool_messages(self, messages: list[dict], tool_max_chars: int) -> list[dict]:
        out: list[dict] = []
        for m in messages:
            if m.get("role") == "tool":
                content = m.get("content") or ""
                if isinstance(content, str) and len(content) > tool_max_chars:
                    m2 = dict(m)
                    m2["content"] = content[:tool_max_chars] + "\n...[tool output truncated]..."
                    out.append(m2)
                else:
                    out.append(m)
            else:
                out.append(m)
        return out

    def _clip_to_char_budget(self, messages: list[dict], budget_chars: int) -> list[dict]:
        """
        Approximate token budgeting by limiting total content characters.

        Keeps all system messages, then adds most recent non-system messages until budget is met.
        """
        system = [m for m in messages if m.get("role") == "system"]
        rest = [m for m in messages if m.get("role") != "system"]

        def clen(x: dict) -> int:
            c = x.get("content") or ""
            return len(c) if isinstance(c, str) else 0

        out_system = list(system)
        total = sum(clen(m) for m in out_system)

        kept_rest_rev: list[dict] = []
        for m in reversed(rest):
            c = m.get("content") or ""
            c_len = len(c) if isinstance(c, str) else 0
            if total + c_len <= budget_chars:
                kept_rest_rev.append(m)
                total += c_len
            else:
                # If nothing fits (rare), keep a clipped tail of the newest message
                if not kept_rest_rev and isinstance(c, str) and c:
                    m2 = dict(m)
                    # Keep last portion; often latest message is most important
                    tail = c[-max(1000, budget_chars - total) :]
                    m2["content"] = tail
                    kept_rest_rev.append(m2)
                break

        kept_rest = list(reversed(kept_rest_rev))
        return out_system + kept_rest

    async def _prepare_small_context(self) -> list[dict]:
        """
        Pull context from BaseAgent, then aggressively shrink it to avoid context overflow.
        """
        messages = await self._prepare_context()

        # 1) Truncate tool outputs (often huge)
        messages = self._truncate_tool_messages(messages, self._TOOL_MAX_CHARS)

        # 2) Window to the last N turns (plus all system messages)
        messages = self._trim_messages_window(messages, self._KEEP_LAST_NON_SYSTEM)

        # 3) Enforce a global budget (rough proxy for tokens)
        messages = self._clip_to_char_budget(messages, self._CHAR_BUDGET)

        # # Inject memory at the end (so it stays in-window)
        # messages = await self._maybe_inject_memory(messages)

        # messages = self._clip_to_char_budget(messages, self._CHAR_BUDGET)

        return messages

    # -----------------------------
    # JSON parsing helpers
    # -----------------------------
    @staticmethod
    def _strip_code_fences(text: str) -> str:
        t = text.strip()
        m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, flags=re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else t

    @staticmethod
    def _best_effort_json_load(text: str) -> Any:
        t = SGRToolCallingAgent._strip_code_fences(text)

        try:
            return json.loads(t)
        except Exception:
            pass

        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(t[start : end + 1])

        raise ValueError(f"Model did not return valid JSON. Raw text (head): {text[:500]}")

    # -----------------------------
    # Memory Tool Helpers
    # -----------------------------

    def _format_memory_context(self, memory_json_str: str, *, top_k: int = 3, per_chunk_chars: int = 900) -> str:
        """
        Convert MemoryTool JSON string output into a compact context block.
        """
        try:
            payload = json.loads(memory_json_str)
        except Exception:
            return "MEMORY RESULTS (unparseable)\n" + (memory_json_str[:1500] if memory_json_str else "")

        if not payload.get("ok"):
            # Keep errors small
            return f"MEMORY RESULTS (error): {payload.get('error_type')} - {payload.get('detail', '')}"

        chunks = payload.get("fulltext_chunks") or []
        if not isinstance(chunks, list) or not chunks:
            return "MEMORY RESULTS: (no fulltext chunks found)"

        # Already sorted by score in the tool; still guard
        chosen = chunks[:top_k]

        lines = []
        lines.append("MEMORY CONTEXT (retrieved fulltext chunks):")
        for i, c in enumerate(chosen, start=1):
            doc_id = (c.get("doc_id") or "").strip()
            title = (c.get("title") or "").strip()
            score = c.get("score", None)
            text = c.get("text") or ""
            if isinstance(text, str) and len(text) > per_chunk_chars:
                text = text[:per_chunk_chars] + "…"

            header_bits = []
            if title:
                header_bits.append(f"title={title}")
            if doc_id and doc_id != title:
                header_bits.append(f"doc_id={doc_id}")
            if isinstance(score, (int, float)):
                header_bits.append(f"score={score:.3f}")

            header = "; ".join(header_bits) if header_bits else "chunk"
            lines.append(f"\n[Chunk {i}] {header}\n{text}")

        return "\n".join(lines)

    async def _maybe_inject_memory(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Calls memory_tool and injects its fulltext chunks into the context window.
        """
        # If MemoryTool isn't available, skip
        mem_cls = self._tool_by_name.get("memory_tool")
        if mem_cls is None:
            return messages

        # Use the latest user message as the query prompt
        last_user = None
        for m in reversed(messages):
            if m.get("role") == "user" and isinstance(m.get("content"), str) and m["content"].strip():
                last_user = m["content"].strip()
                break
        if not last_user:
            return messages

        # Instantiate and call tool
        mem_tool = mem_cls(
            collection_name=getattr(self.config.global_config, "default_memory_collection", "default"),
            user_prompt=last_user,
            user_id=getattr(self._context, "user_id", "") or "",
            n_results=5,
            doc_id="",
            subgraph_method="5_3",
            max_text_chars=1200,
        )

        mem_result = await mem_tool(self._context, self.config)

        # Inject as a SYSTEM message so the model treats it as authoritative context
        mem_block = self._format_memory_context(mem_result, top_k=3, per_chunk_chars=900)
        injected = messages + [
            {
                "role": "system",
                "content": mem_block,
            }
        ]
        return injected



    # -----------------------------
    # Model call: schema JSON via extra_body
    # -----------------------------
    async def _model_json(
        self,
        *,
        messages: list[dict[str, Any]],
        json_schema: dict[str, Any],
        schema_name: str,
    ) -> Any:
        """
        Call the OpenAI-compatible shim and request schema-constrained JSON.

        IMPORTANT: We send response_format via extra_body so it actually appears
        in the HTTP JSON payload to your shim (your shim confirmed response_format was null).
        """
        # schema_payload = {
        #     "type": "json_schema",
        #     "json_schema": {
        #         "name": schema_name,
        #         "schema": json_schema,
        #         "strict": True,
        #     },
        # }

        schema_payload = {
                "name": schema_name,
                "schema": json_schema,
                # "strict": True,
        }

        completion = await self.openai_client.chat.completions.create(
            messages=messages,
            extra_body={"response_format": schema_payload},
            **self._openai_request_kwargs(),
        )

        msg = completion.choices[0].message
        content = msg.content or ""
        return self._best_effort_json_load(content)

    # -----------------------------
    # Phases
    # -----------------------------
    async def _reasoning_phase(self) -> ReasoningTool:
        """
        Ask the model for ReasoningTool as strict JSON, then execute it.
        """
        messages = await self._prepare_small_context()

        reasoning_dict = await self._model_json(
            messages=messages,
            json_schema=ReasoningTool.model_json_schema(),
            schema_name="ReasoningTool",
        )
        reasoning: ReasoningTool = ReasoningTool.model_validate(reasoning_dict)

        # Record as an OpenAI-ish tool call for downstream compatibility
        self.conversation.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "type": "function",
                        "id": f"{self._context.iteration}-reasoning",
                        "function": {
                            "name": reasoning.tool_name,
                            "arguments": reasoning.model_dump_json(),
                        },
                    }
                ],
            }
        )

        tool_call_result = await reasoning(self._context)

        self.streaming_generator.add_tool_call(
            f"{self._context.iteration}-reasoning",
            reasoning.tool_name,
            tool_call_result,
        )

        self.conversation.append(
            {"role": "tool", "content": tool_call_result, "tool_call_id": f"{self._context.iteration}-reasoning"}
        )

        self._log_reasoning(reasoning)
        return reasoning

    async def _select_action_phase(self, reasoning: ReasoningTool) -> BaseTool:
        """
        Ask the model to select exactly one tool and its args using ToolSelection schema.
        """
        messages = await self._prepare_small_context()

        selection_dict = await self._model_json(
            messages=messages,
            json_schema=ToolSelection.model_json_schema(),
            schema_name="ToolSelection",
        )
        selection = ToolSelection.model_validate(selection_dict)

        tool_name_key = (selection.tool_name or "").strip().lower()
        tool_cls = self._tool_by_name.get(tool_name_key)

        if tool_cls is None:
            # Unknown tool: fail safe
            step = reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completed"
            tool = FinalAnswerTool(
                reasoning=f"Model selected unknown tool '{selection.tool_name}'. Completing safely.",
                completed_steps=[step],
                answer="I couldn't map the selected tool to a known tool. Please check tool_name.",
                status=AgentStatesEnum.COMPLETED,
            )
        else:
            tool_args_dict = await self._model_json(
            messages=messages + [
                {
                    "role": "system",
                    "content": (
                        f"You selected tool '{tool_cls.tool_name}'. "
                        "Now output ONLY the JSON arguments object for this tool, "
                        "matching the provided schema exactly."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(selection.tool_args, ensure_ascii=False),
                },
            ],
            json_schema=tool_cls.model_json_schema(),   # <-- enforce tool schema here
            schema_name=f"{tool_cls.tool_name}_Args",
            )
            try:
                # tool = tool_cls.model_validate(selection.tool_args)
                tool = tool_cls.model_validate(tool_args_dict)
            except Exception as e:
                step = reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completed"
                tool = FinalAnswerTool(
                    reasoning=f"Tool args validation failed for '{selection.tool_name}'. Completing safely.",
                    completed_steps=[step],
                    answer=f"Tool arguments were invalid: {e}",
                    status=AgentStatesEnum.COMPLETED,
                )

        if not isinstance(tool, BaseTool):
            raise ValueError("Selected tool is not a valid BaseTool instance")

        # Record selected tool call (OpenAI-ish)
        self.conversation.append(
            {
                "role": "assistant",
                "content": reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completing",
                "tool_calls": [
                    {
                        "type": "function",
                        "id": f"{self._context.iteration}-action",
                        "function": {
                            "name": tool.tool_name,
                            "arguments": tool.model_dump_json(),
                        },
                    }
                ],
            }
        )

        self.streaming_generator.add_tool_call(
            f"{self._context.iteration}-action",
            tool.tool_name,
            tool.model_dump_json(),
        )

        return tool

    async def _action_phase(self, tool: BaseTool) -> str:
        result = await tool(self._context, self.config)

        self.conversation.append(
            {"role": "tool", "content": result, "tool_call_id": f"{self._context.iteration}-action"}
        )

        # Even if local model is non-streaming, SGR endpoint may stream SSE—emit once.
        self.streaming_generator.add_chunk_from_str(f"{result}\n")

        self._log_tool_execution(tool, result)
        return result
