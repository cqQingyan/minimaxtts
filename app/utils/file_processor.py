import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def process_epub_to_text(file_path):
    text_content = []
    try:
        book = epub.read_epub(file_path)
        for item_id, _linear in book.spine:
            item = book.get_item_with_id(item_id)
            if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text_content.append(soup.get_text())
        return "\n".join(text_content)
    except Exception as e:
        raise ValueError(f"Failed to process EPUB: {str(e)}")
