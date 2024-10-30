# code_executor.py
import subprocess
from pathlib import Path
import asyncio
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CodeExecutor:
    def __init__(self, workspace_dir: str = "generated_code"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)

    async def execute_files(self, filenames: List[str]) -> Dict[str, str]:
        """
        Execute multiple Python files asynchronously.

        Args:
            filenames (List[str]): List of Python filenames to execute.

        Returns:
            Dict[str, str]: Dictionary mapping filenames to their execution outputs.
        """
        tasks = [self._execute_file_async(filename) for filename in filenames]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_results = {}
        for filename, result in zip(filenames, results):
            if isinstance(result, Exception):
                execution_results[filename] = f"Execution failed: {str(result)}"
            else:
                execution_results[filename] = result
        return execution_results

    async def _execute_file_async(self, filename: str) -> str:
        """
        Asynchronously execute a Python file and capture its output.

        Args:
            filename (str): The Python filename to execute.

        Returns:
            str: The captured STDOUT and STDERR.
        """
        file_path = self.workspace_dir / filename
        if not file_path.exists():
            logger.error(f"File {filename} does not exist.")
            return "File not found."

        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            return f"STDOUT:\n{stdout.decode()}\nSTDERR:\n{stderr.decode()}"
        except asyncio.TimeoutError:
            logger.error(f"Execution of {filename} timed out.")
            return "Execution timed out after 30 seconds."
        except Exception as e:
            logger.error(f"Error executing {filename}: {str(e)}", exc_info=True)
            return f"Execution error: {str(e)}"