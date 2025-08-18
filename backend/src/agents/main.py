# run as a package module: python -m agents.main
from agents.workers import run_worker  # absolute import

def main():
    print("Starting agent worker...")
    run_worker()

if __name__ == "__main__":
    main()
