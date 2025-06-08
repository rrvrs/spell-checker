from bs4 import BeautifulSoup
import os
import glob

def extract_abstracts(xml_dir, output_path):
    abstracts = []

    for file in glob.glob(f"{xml_dir}/*.xml"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "lxml")
                sections = soup.find_all(["abstract", "title"])
                for sec in sections:
                    text = sec.get_text(strip=True)
                    if text and len(text.split()) > 5:
                        abstracts.append(text)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    with open(output_path, "w", encoding="utf-8") as out:
        out.write("\n".join(abstracts))
    print(f"✅ Saved {len(abstracts)} abstracts to {output_path}")

if __name__ == "__main__":
    xml_folder = "corpus/pmc_xml"
    output_file = "corpus/medline_abstracts.txt"
    extract_abstracts(xml_folder, output_file)
