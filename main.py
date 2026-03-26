import argparse

from agent.agent import Agent


def parse_args():
    parser = argparse.ArgumentParser(description="TrailGraph AI Agent")
    parser.add_argument("--task", type=str, help="Task for the agent to execute")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def main():
    args = parse_args()
    agent = Agent(verbose=args.verbose)
    agent.run(task=args.task)


if __name__ == "__main__":
    main()
