import os
from functools import reduce
from uuid import uuid4

import fitz
from tqdm import tqdm

from .utils import get_chunks, sanitize


class Pdf:

    def __init__(self, file_path):

        try:
            self._doc = fitz.open(file_path)
        except:
            raise ("Unable to read file as pdf")

        self.file_path = os.path.abspath(file_path)
        self.file_name = os.path.basename(file_path)

    def _get_words(self):
        """
        Extract and return words from pdf along with page number, page dimensions,
        block number, line number and word sequence number
        """
        words = []
        for page_number, page in enumerate(self._doc):
            words_in_page = [
                (*ele, page_number, page.rect.height, page.rect.width)
                for ele in page.get_text("words")
            ]
            words += words_in_page

        return words

    def _get_boundingrect(self, bboxes):
        """
        Calculate and return the the smallest rectangle that encompasses
        all the bounding boxes for a text passage. If the text spans multiple
        pages, only the bounding boxes from the first page are considered.
        """
        page_number = bboxes[0]["pageNumber"]
        i = 1
        while i < len(bboxes) and page_number == bboxes[i]["pageNumber"]:
            i += 1

        return {
            "x1": bboxes[0]["x1"],
            "y1": bboxes[0]["y1"],
            "x2": bboxes[i - 1]["x2"],
            "y2": bboxes[i - 1]["y2"],
            "pageNumber": page_number,
            "height": bboxes[0]["height"],
            "width": bboxes[0]["width"],
        }

    def _get_text_pos(self, lst):
        """
        Return text positions after grouping word bounding boxes
        based-on page, text block, and line number information.

        lst[i] : tuple(x1, y1, x2, y2, "word", block_no, line_no, word_no, page_number, height, width)
        """
        bboxes = []
        i = 0

        while i < len(lst):

            x1, y1 = lst[i][:2]
            block_no, line_no = lst[i][5:7]
            page_number, height, width = lst[i][8:]

            i += 1

            while (
                i < len(lst)
                and block_no == lst[i][5]
                and line_no == lst[i][6]
                and page_number == lst[i][8]
            ):
                i += 1

            bboxes.append(
                {
                    "x1": x1,
                    "y1": y1,
                    "x2": lst[i - 1][2],
                    "y2": lst[i - 1][3],
                    "pageNumber": page_number + 1,  # convert to 1-indexed
                    "height": height,
                    "width": width,
                }
            )

        return {
            "rects": bboxes,
            "boundingRect": self._get_boundingrect(bboxes),
        }

    def extract_text(self, chunk_size=50):
        embedding_input = []
        words = self._get_words()

        chunks = get_chunks(words, chunk_size)

        for chunk in tqdm(chunks, desc="Extracting text"):
            text = reduce(lambda prev, curr: prev + curr[4] + " ", chunk, "")
            position = self._get_text_pos(chunk)
            embedding_input.append(
                {"id": str(uuid4()), "text": sanitize(text), "position": position}
            )

        return embedding_input
