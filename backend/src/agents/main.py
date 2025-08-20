# run as a package module: python -m src.agents.main
from src.agents.workers import run_worker

def main():
    print("Starting agent worker...")
    run_worker()

if __name__ == "__main__":
    main()
