import argparse

from agent.agent import Agent
from config import ANSWER_THRESHOLD, EXPLORATION_THRESHOLD


def parse_args():
    parser = argparse.ArgumentParser(description="TrailGraph AI Agent")
    parser.add_argument("--task", type=str, help="Task for the agent to execute")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def main():
    args = parse_args()
    prompt_vars = {
        "EXPLORATION_THRESHOLD": EXPLORATION_THRESHOLD,
        "EXPLORATION_THRESHOLD_MINUS_1": EXPLORATION_THRESHOLD - 1,
        "ANSWER_THRESHOLD": ANSWER_THRESHOLD,
        "ANSWER_THRESHOLD_MINUS_1": ANSWER_THRESHOLD - 1,
    }
    agent = Agent(prompt_vars=prompt_vars, verbose=args.verbose)
    agent.run(task=args.task)


if __name__ == "__main__":
    main()
