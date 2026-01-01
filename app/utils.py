from bs4 import BeautifulSoup
from ebooklib import epub
import ebooklib

def extract_text_from_epub(file_stream):
    try:
        book = epub.read_epub(file_stream)
        text_content = []
        # Iterate over the spine to ensure correct reading order
        for item_id, _linear in book.spine:
            item = book.get_item_with_id(item_id)
            if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text_content.append(soup.get_text())
        return "\n".join(text_content)
    except Exception as e:
        print(f"Error parsing EPUB: {e}")
        return None
