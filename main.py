
import asyncio
import argparse
import json
from prompt_processor import PromptProcessor
from rich.console import Console
import logging
from code_generator import CodeGenerator
from pathlib import Path  # Imported Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
console = Console()

async def main():
    parser = argparse.ArgumentParser(description='Advanced LLM Prompt Processor')
    parser.add_argument('--complexity', type=int, choices=range(1, 6),
                        default=1, help='Complexity level (1-5)')
    parser.add_argument('--prompt', type=str, required=True,
                        help='Input prompt to process')
    parser.add_argument('--output', type=str, choices=['text', 'json', 'code'],
                        default='text', help='Output format')

    args = parser.parse_args()

    try:
        logger.debug(f"Starting processing with complexity {args.complexity}")
        logger.debug(f"Prompt: {args.prompt}")

        console.print(f"[cyan]Processing prompt with complexity {args.complexity}...[/cyan]")
        processor = PromptProcessor(args.complexity)

        logger.debug("Calling process_prompt")
        result = await processor.process_prompt(args.prompt)
        logger.debug("Finished process_prompt")

        if args.output == 'json':
            logger.debug("Outputting JSON format")
            console.print_json(json.dumps(result, indent=2))
        elif args.output == 'code':
            logger.debug("Outputting Code format")
            code_gen = CodeGenerator()
            output_file = "output.py"  # Adjusted to prevent duplication
            full_output_path = code_gen.workspace_dir / output_file  # Correct path
            logger.debug(f"Writing code to {full_output_path}")
            execution_response = await code_gen.generate_and_execute(result['final_result'], output_file)

            if execution_response['success']:
                logger.debug(f"Executing file {full_output_path}")
                execution_result = code_gen._execute_file(full_output_path)
                if "STDERR:" in execution_result and execution_result.split("STDERR:")[1].strip():
                    console.print("[red]Code execution failed. Error Output:[/red]")
                    console.print(execution_result)

                    # Send the error back to the LLM for analysis
                    from llm_service import LLMService  # Import here to avoid circular import
                    llm_service = LLMService()
                    debug_prompt = (
                        "The following Python script encountered an error during execution:\n\n"
                        "TRIPLE_BS_GOES_HEREpython\n"
                        f"{execution_response['code']}\n"
                        "TRIPLE_BS_GOES_HERE\n\n"
                        "Error Output:\n"
                        "TRIPLE_BS_GOES_HERE\n"
                        f"{execution_result}\n"
                        "TRIPLE_BS_GOES_HERE\n\n"
                        "Please analyze the error and provide suggestions to fix the script."
                    )
                    logger.debug("Sending error details back to LLM for analysis")
                    llm_debug_response = await llm_service.generate_response(debug_prompt)
                    console.print("[yellow]LLM Debug Suggestions:[/yellow]")
                    console.print(llm_debug_response)
                else:
                    console.print("[green]Code executed successfully. Output:[/green]")
                    console.print(execution_result)
            else:
                console.print("[red]Failed to generate and execute code.[/red]")
                console.print(f"Error: {execution_response['error']}")
        else:
            logger.debug("Outputting text format")
            console.print("\n[cyan]Final Result:[/cyan]")
            console.print(result['final_result'])

            console.print("\n[yellow]Processing Details:[/yellow]")
            console.print(f"Time taken: {result['processing_time']}")
            console.print(f"Subtasks processed: {len(result['subtask_results'])}")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        console.print(f"[red]Error:[/red] {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
