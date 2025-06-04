from ccbr_tools.pipeline.hpc import get_hpcname

def main():
    HPC = get_hpcname()
    print(f"{HPC}")

if __name__ == "__main__":
    main()