
import asyncio
from typing import List, Dict
from datetime import datetime
import json
from llm_service import LLMService
from config import config
import logging

logger = logging.getLogger(__name__)

class PromptProcessor:
    def __init__(self, complexity: int = 1):
        logger.debug(f"Initializing PromptProcessor with complexity {complexity}")
        self.complexity = min(max(complexity, 1), 5)
        self.llm_service = LLMService()
        self.iterations = config.get_iterations(self.complexity)
        self.results_cache = {}

    async def process_prompt(self, prompt: str) -> Dict:
        logger.debug(f"Processing prompt: {prompt[:100]}...")
        start_time = datetime.now()

        # Check cache
        cache_key = f"{prompt}_{self.complexity}"
        if cache_key in self.results_cache:
            logger.debug("Cache hit")
            return self.results_cache[cache_key]

        logger.debug("Decomposing prompt into subtasks")
        subtasks = await self.llm_service.decompose_prompt(prompt, self.complexity)

        # Process subtasks
        subtask_results = []
        for i, subtask in enumerate(subtasks, 1):
            logger.debug(f"Processing subtask {i}/{len(subtasks)}: {subtask[:100]}...")
            result = await self.process_subtask(subtask)
            subtask_results.append({"task": subtask, "result": result})

        logger.debug("Combining results")
        final_result = await self.combine_results(subtask_results, prompt)

        response = {
            "original_prompt": prompt,
            "complexity_level": self.complexity,
            "processing_time": str(datetime.now() - start_time),
            "subtask_results": subtask_results,
            "final_result": final_result
        }

        logger.debug("Caching results")
        self.results_cache[cache_key] = response
        return response

    async def process_subtask(self, subtask: str) -> str:
        """Process individual subtask"""
        logger.debug(f"Processing subtask: {subtask[:100]}...")
        system_prompt = (
            "You are an expert Python developer. You will always write responses in valid Python code. "
            "Do not include any explanations, comments, or additional text. Provide only the Python code. "
            "Ensure that the code is self-contained and executable."
        )
        return await self.llm_service.generate_response(subtask, system_prompt)

    async def combine_results(self, subtask_results: List[Dict], original_prompt: str) -> str:
        """Combine all subtask results into a final response"""
        logger.debug("Combining results...")
        combination_prompt = (
            f"Original prompt: {original_prompt}\n\n"
            "Combine the following subtask results into a coherent Python script:\n"
            f"{json.dumps(subtask_results, indent=2)}\n\n"
            "Ensure that the combined script is well-structured, adheres to Python best practices, "
            f"and meets the specified complexity level of {self.complexity}/5."
        )

        system_prompt = (
            "You are an expert at synthesizing Python code into coherent, executable scripts. "
            "Do not include any explanations or comments. Provide only the Python code. "
            "Ensure that the final script is free of syntax errors and is ready to be executed. "
            "If there are any issues with the combined script, provide detailed error messages "
            "to assist in debugging."
        )
        return await self.llm_service.generate_response(combination_prompt, system_prompt)
