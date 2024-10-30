
import os
import sys
import ast
import asyncio
from typing import Dict, List, Optional
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self, workspace_dir: str = "generated_code"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)  # Ensure directory exists

    def _validate_syntax(self, code: str) -> bool:
        """Validate the syntax of the generated Python code."""
        try:
            ast.parse(code)
            logger.debug("Syntax validation passed")
            return True
        except SyntaxError as e:
            logger.error(f"Syntax validation failed: {e}")
            return False

    async def generate_and_execute(self, code_spec: str, filename: str) -> Dict:
        """Generate code file and execute it based on specification"""
        try:
            # Validate syntax before writing
            if not self._validate_syntax(code_spec):
                logger.error("Syntax validation failed.")
                return {
                    'success': False,
                    'error': 'Syntax validation failed.',
                    'code': code_spec
                }

            # Generate the file
            file_path = self.workspace_dir / filename
            with open(file_path, 'w') as f:
                f.write(code_spec)
            logger.debug(f"Written code to: {file_path}")

            # Execute and capture output
            result = self._execute_file(file_path)
            logger.debug(f"Execution result: {result}")

            return {
                'success': True,
                'file_path': str(file_path),
                'output': result,
                'code': code_spec
            }
        except Exception as e:
            logger.error(f"Error in generate_and_execute: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'code': code_spec
            }

    def _execute_file(self, file_path: Path) -> str:
        """Execute a Python file and return its output"""
        try:
            logger.debug(f"Executing file: {file_path}")
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            logger.debug(f"Execution STDOUT: {result.stdout}")
            logger.debug(f"Execution STDERR: {result.stderr}")
            if result.returncode != 0:
                return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            return f"STDOUT:\n{result.stdout}"
        except subprocess.TimeoutExpired:
            logger.error("Execution timed out after 30 seconds")
            return "Execution timed out after 30 seconds"
        except Exception as e:
            logger.error(f"Error executing file: {str(e)}", exc_info=True)
            return f"Error executing file: {str(e)}"
