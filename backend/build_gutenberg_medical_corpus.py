import os
from gutenbergpy.textget import get_text_by_id

BOOK_IDS = {
    1566: "evolution_modern_medicine.txt",
    20200: "grays_anatomy.txt",
    18096: "manual_physiology.txt",
    33010: "materia_medica.txt",
    23478: "hygiene_women.txt",
    17439: "common_sense_medical_advice.txt"
}

def build_gutenberg_corpus(output_dir="corpus/gutenberg_medical/"):
    os.makedirs(output_dir, exist_ok=True)

    for book_id, filename in BOOK_IDS.items():
        try:
            print(f"📘 Downloading book ID: {book_id}")
            raw_bytes = get_text_by_id(book_id)
            raw_text = raw_bytes.decode("utf-8", errors="ignore").strip()

            output_path = os.path.join(output_dir, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(raw_text)

            print(f"✅ Saved: {filename}")

        except Exception as e:
            print(f"❌ Failed for ID {book_id}: {e}")

if __name__ == "__main__":
    build_gutenberg_corpus()
