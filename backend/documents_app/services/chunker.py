from langchain_text_splitters import RecursiveCharacterTextSplitter



class Chunker:
    def __init__(self, text):
        self.text = text
        self.chunker = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50,
                                                       separators=["\n\n", "\n", "۔",
                                                       ".", "؟", "!", "،", " ", ""],)

    def chunking(self):
        return self.chunker.split_text(self.text)