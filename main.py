import subprocess
import argparse
import os
import ebooklib
from ebooklib import epub

# convert pdf to markdown
def run_marker(filename, output_dir):
    command = [
        "uv", "run", "marker_single",
        filename,
        "--output_dir", output_dir,
        "--output_format", "markdown"
    ]

    try:
        print("Running command:", " ".join(command))
        subprocess.run(command, check=True)

        # if succeeded, delete the files in the folder
        os.remove(filename)

    except subprocess.CalledProcessError as e:
        print("Command failed:", e)


# convert epub to markdown
def run_epub(filename, output_dir):
    try:
        command = [
            "pandoc", filename,
            "-f", "epub",
            "-t", "markdown",
            "-o", os.path.join(output_dir, os.path.basename(filename) + ".md")
        ]
        subprocess.run(command, check=True)

        # if succeeded, delete the files in the folder
        os.remove(filename)

    except subprocess.CalledProcessError as e:
        print("Command failed:", e)
    


def run_main(foldername, output_dir):
    for file in os.listdir(foldername):
        print("Processing file: {0}".format(file))
        if file.endswith(".pdf"):
            run_marker(os.path.join(foldername, file), output_dir)
        elif file.endswith(".epub"):
            run_epub(os.path.join(foldername, file), output_dir)
        else:
            print("Unknown file type: {0}".format(file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper for `uv run marker`.")
    parser.add_argument("--foldername", required = False, default="./to_convert", help="Input folder name")
    parser.add_argument("--output_dir", required = False, default="./conversion_results", help="Output directory")

    args = parser.parse_args()
    run_main(args.foldername, args.output_dir)
