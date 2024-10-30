
import openai
from typing import List, Dict, Any
import json
from config import config, llm_config
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.debug("Initializing LLMService")
        openai.api_key = config.api_key

    async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        try:
            logger.debug(f"Generating response for prompt: {prompt[:100]}...")
            logger.debug(f"Using system prompt: {system_prompt[:100]}...")

            response = await openai.ChatCompletion.acreate(
                model=llm_config.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
                top_p=llm_config.top_p
            )
            logger.debug("Response received from OpenAI")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}", exc_info=True)
            raise Exception(f"Error generating LLM response: {str(e)}")

    async def decompose_prompt(self, prompt: str, complexity: int) -> List[str]:
        logger.debug(f"Decomposing prompt with complexity {complexity}")
        system_prompt = (
            "You are a prompt decomposition expert. You will always write responses in Python code. "
            "Break down the given prompt into smaller, manageable sub-tasks. "
            "Return the sub-tasks as a JSON array of strings. "
            "Consider the complexity level provided and adjust the granularity accordingly. "
            "Format your response as a plain JSON array without markdown formatting."
        )

        decomposition_prompt = (
            f"Complexity Level: {complexity}/5\n"
            f"Original Prompt: {prompt}\n\n"
            f"Break this prompt into {config.get_iterations(complexity)} sub-tasks.\n"
            "Return only a JSON array of strings representing the sub-tasks.\n"
            "Example format: [\"task1\", \"task2\", \"task3\"]"
        )

        try:
            response = await self.generate_response(decomposition_prompt, system_prompt)
            logger.debug(f"Decomposition response: {response[:100]}...")

            # Clean the response - remove any markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith('TRIPLE_BS_GOES_HERE') and 'python' in cleaned_response.lower():
                cleaned_response = cleaned_response.split('\n', 1)[1]
            if cleaned_response.endswith('TRIPLE_BS_GOES_HERE'):
                cleaned_response = cleaned_response.rsplit('\n', 1)[0]
            if cleaned_response.lower().startswith('json'):
                cleaned_response = cleaned_response[4:].strip()

            subtasks = json.loads(cleaned_response)
            logger.debug(f"Successfully parsed {len(subtasks)} subtasks")
            return subtasks if isinstance(subtasks, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}", exc_info=True)
            return [prompt]
        except Exception as e:
            logger.error(f"Error in decompose_prompt: {str(e)}", exc_info=True)
            return [prompt]
