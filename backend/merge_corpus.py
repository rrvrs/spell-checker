import os

def merge_medical_corpus(pmc_file, gutenberg_dir, output_file):
    combined = []

    with open(pmc_file, "r", encoding="utf-8") as f:
        combined += f.readlines()

    for file in os.listdir(gutenberg_dir):
        if file.endswith(".txt"):
            with open(os.path.join(gutenberg_dir, file), "r", encoding="utf-8") as f:
                combined += f.readlines()

    with open(output_file, "w", encoding="utf-8") as out:
        out.writelines([line.strip() + "\n" for line in combined if line.strip()])
    print(f"🧾 Merged corpus saved to: {output_file}")

merge_medical_corpus("corpus/medline_abstracts.txt", "corpus/gutenberg_medical", "corpus/medical_combined_corpus.txt")
