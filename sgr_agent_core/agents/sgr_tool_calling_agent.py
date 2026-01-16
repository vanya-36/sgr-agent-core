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

import json
from typing import Literal, Type

from openai import AsyncOpenAI, pydantic_function_tool

from sgr_agent_core.agent_config import AgentConfig
from sgr_agent_core.base_agent import BaseAgent
from sgr_agent_core.models import AgentStatesEnum
from sgr_agent_core.tools import (
    BaseTool,
    FinalAnswerTool,
    ReasoningTool,
)


class SGRToolCallingAgent(BaseAgent):
    """Agent that uses OpenAI native function calling to select and execute
    tools based on SGR like a reasoning scheme."""

    name: str = "sgr_tool_calling_agent"

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
        self.tool_choice: Literal["required"] = "required"
        self._toolkit = toolkit

    def _openai_request_kwargs(self) -> dict:
        """
        Convert config LLM settings into kwargs that are SAFE to pass into
        OpenAI SDK request methods (chat.completions.create).

        Important: The SDK request methods do NOT accept client-construction kwargs
        like provider/api_key/base_url.
        """
        bad_keys = {"provider", "api_key", "base_url"}
        return {
            k: v for k, v in self.config.llm.to_openai_client_kwargs().items() if k not in bad_keys
        }

    def _parse_tool_call(self, tool_cls: type[BaseTool], msg) -> BaseTool:
        """
        Parse the first tool call's function.arguments JSON into the given Pydantic tool class.
        Works for non-streaming chat.completions.create responses where parsed_arguments is absent.
        """
        if not msg.tool_calls:
            raise ValueError("No tool_calls in model response")

        fn = msg.tool_calls[0].function
        args_json = getattr(fn, "arguments", None)

        if not args_json:
            # Sometimes arguments can be empty; treat as empty object
            args = {}
        else:
            args = json.loads(args_json)

        # pydantic v2 style
        return tool_cls.model_validate(args)


    def _emit_single_assistant_chunk(self, text: str | None) -> None:
        """
        Even when we call the LLM non-streaming, the SGR API may still respond
        as an SSE stream. To stay compatible, we emit the final text as one chunk.
        """
        if text:
            self.streaming_generator.add_chunk_from_str(text)

    async def _reasoning_phase(self) -> ReasoningTool:
        completion = await self.openai_client.chat.completions.create(
            messages=await self._prepare_context(),
            tools=[pydantic_function_tool(ReasoningTool, name=ReasoningTool.tool_name)],
            tool_choice={"type": "function", "function": {"name": ReasoningTool.tool_name}},
            **self._openai_request_kwargs(),
        )

        msg = completion.choices[0].message

        # In forced-tool mode this is usually empty, but emit if present.
        self._emit_single_assistant_chunk(msg.content)

        # Expect a tool call for the ReasoningTool
        # reasoning: ReasoningTool = msg.tool_calls[0].function.parsed_arguments
        reasoning: ReasoningTool = self._parse_tool_call(ReasoningTool, msg)  # type: ignore[assignment]

        # Record the tool call in conversation history
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

        # Execute the reasoning tool
        tool_call_result = await reasoning(self._context)

        # Stream tool call result event (SGR internal streaming)
        self.streaming_generator.add_tool_call(
            f"{self._context.iteration}-reasoning",
            reasoning.tool_name,
            tool_call_result,
        )

        # Record tool output in conversation history
        self.conversation.append(
            {
                "role": "tool",
                "content": tool_call_result,
                "tool_call_id": f"{self._context.iteration}-reasoning",
            }
        )

        self._log_reasoning(reasoning)
        return reasoning

    # async def _select_action_phase(self, reasoning: ReasoningTool) -> BaseTool:
    #     completion = await self.openai_client.chat.completions.create(
    #         messages=await self._prepare_context(),
    #         tools=await self._prepare_tools(),
    #         tool_choice=self.tool_choice,
    #         **self._openai_request_kwargs(),
    #     )

    #     msg = completion.choices[0].message
    #     self._emit_single_assistant_chunk(msg.content)

    #     try:
    #         # tool = msg.tool_calls[0].function.parsed_arguments
    #         # Determine which tool class was chosen by name, then parse arguments into that class
    #         tc = msg.tool_calls[0]
    #         tool_name = tc.function.name

    #         tool_cls = None
    #         for t in self._context.toolkit:
    #             if getattr(t, "tool_name", "").lower() == (tool_name or "").lower():
    #                 tool_cls = t
    #                 break

    #         if tool_cls is None:
    #             raise ValueError(f"Unknown tool selected by model: {tool_name}")

    #         tool = self._parse_tool_call(tool_cls, msg)

    #     except (IndexError, AttributeError, TypeError):
    #         # LLM returned text (or malformed tool call) -> treat as final answer
    #         final_content = msg.content or "Task completed successfully"
    #         # tool = FinalAnswerTool(
    #         #     reasoning="Agent decided to complete the task",
    #         #     completed_steps=[],
    #         #     answer=final_content,
    #         #     status=AgentStatesEnum.COMPLETED,
    #         # )
    #         step = reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completed"
    #         tool = FinalAnswerTool(
    #             reasoning="Agent decided to complete the task",
    #             completed_steps=[step],
    #             answer=final_content,
    #             status=AgentStatesEnum.COMPLETED,
    #         )


    #     if not isinstance(tool, BaseTool):
    #         raise ValueError("Selected tool is not a valid BaseTool instance")

    #     # Record selected action tool call in conversation history
    #     self.conversation.append(
    #         {
    #             "role": "assistant",
    #             "content": reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completing",
    #             "tool_calls": [
    #                 {
    #                     "type": "function",
    #                     "id": f"{self._context.iteration}-action",
    #                     "function": {
    #                         "name": tool.tool_name,
    #                         "arguments": tool.model_dump_json(),
    #                     },
    #                 }
    #             ],
    #         }
    #     )

    #     # Emit tool call event (SGR internal streaming)
    #     self.streaming_generator.add_tool_call(
    #         f"{self._context.iteration}-action",
    #         tool.tool_name,
    #         tool.model_dump_json(),
    #     )

    #     return tool

    import json

    async def _select_action_phase(self, reasoning: ReasoningTool) -> BaseTool:
        completion = await self.openai_client.chat.completions.create(
            messages=await self._prepare_context(),
            tools=await self._prepare_tools(),
            tool_choice=self.tool_choice,
            **self._openai_request_kwargs(),
        )

        msg = completion.choices[0].message

        # If model produced visible text, emit once (optional)
        self._emit_single_assistant_chunk(msg.content)

        # ---- Case 1: Model returned a tool call (expected) ----
        if msg.tool_calls and len(msg.tool_calls) > 0:
            tc = msg.tool_calls[0]
            tool_name = (tc.function.name or "").lower()
            args_json = tc.function.arguments or "{}"

            # Find tool class by tool_name
            tool_cls: type[BaseTool] | None = None
            # for t in self._context.toolkit:
            for t in self._toolkit:
                if getattr(t, "tool_name", "").lower() == tool_name:
                    tool_cls = t
                    break

            if tool_cls is None:
                raise ValueError(f"Unknown tool selected by model: {tc.function.name}")

            try:
                args = json.loads(args_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Tool arguments were not valid JSON: {args_json}") from e

            tool = tool_cls.model_validate(args)

        # ---- Case 2: No tool call, but model gave text -> wrap as FinalAnswerTool ----
        else:
            final_content = msg.content or "Task completed successfully"
            step = reasoning.remaining_steps[0] if reasoning.remaining_steps else "Completed"
            tool = FinalAnswerTool(
                reasoning="Agent decided to complete the task",
                completed_steps=[step],   # must be non-empty
                answer=final_content,
                status=AgentStatesEnum.COMPLETED,
            )

        if not isinstance(tool, BaseTool):
            raise ValueError("Selected tool is not a valid BaseTool instance")

        # Record tool call
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
            f"{self._context.iteration}-action", tool.tool_name, tool.model_dump_json()
        )

        return tool


    async def _action_phase(self, tool: BaseTool) -> str:
        result = await tool(self._context, self.config)

        # Record tool output in conversation history
        self.conversation.append(
            {"role": "tool", "content": result, "tool_call_id": f"{self._context.iteration}-action"}
        )

        # Emit tool result as part of SSE stream (single chunk)
        self.streaming_generator.add_chunk_from_str(f"{result}\n")

        self._log_tool_execution(tool, result)
        return result
