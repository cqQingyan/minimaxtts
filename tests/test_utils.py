import pytest
from app.utils import extract_text_from_epub
import io
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

# Mock EPUB structure is complex, so we'll mock ebooklib.epub.read_epub
def test_extract_text_from_epub_success(mocker):
    # Mock book item
    mock_item = mocker.Mock()
    mock_item.get_type.return_value = ebooklib.ITEM_DOCUMENT
    mock_item.get_content.return_value = b'<html><body><p>Hello World</p></body></html>'

    # Mock book
    mock_book = mocker.Mock()
    mock_book.spine = [('item1', 'yes')]
    mock_book.get_item_with_id.return_value = mock_item

    mocker.patch('ebooklib.epub.read_epub', return_value=mock_book)

    result = extract_text_from_epub(io.BytesIO(b'dummy'))
    assert result == 'Hello World'

def test_extract_text_from_epub_failure(mocker):
    mocker.patch('ebooklib.epub.read_epub', side_effect=Exception("Read error"))

    # We expect None and a log message (which we won't assert here but could)
    result = extract_text_from_epub(io.BytesIO(b'dummy'))
    assert result is None
