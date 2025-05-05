import subprocess
import argparse
import os

def run_marker(foldername, output_dir):
    for file in os.listdir(foldername):
        command = [
            "uv", "run", "marker_single",
            os.path.join(foldername, file),
            "--output_dir", output_dir,
            "--output_format", "markdown"
    ]

        try:
            print("Running command:", " ".join(command))
            subprocess.run(command, check=True)

            # if succeeded, delete the files in the folder
            os.remove(os.path.join(foldername, file))

        except subprocess.CalledProcessError as e:
            print("Command failed:", e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper for `uv run marker`.")
    parser.add_argument("--foldername", required = False, default="./to_convert", help="Input folder name")
    parser.add_argument("--output_dir", required = False, default="./conversion_results", help="Output directory")

    args = parser.parse_args()
    run_marker(args.foldername, args.output_dir)
