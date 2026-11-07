from pydoc import Doc
from typing import final
from pathlib import Path
from chromadb import PersistentClient
from chromadb.api.models.Collection import Collection
from config import BASE_DIR
from langchain.embeddings import init_embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
KB_DIR = BASE_DIR / "data" / "kb"
CHROMA_DIR = BASE_DIR / "data" / "chroma"
#配置嵌入模型
MODEL_NAME = "qwen3-embedding:4b"
MODEL_PROVDER = "ollama"
EMBED_DIM = 2560
embeddings_model = init_embeddings(
    model = MODEL_NAME,
    provider = MODEL_PROVDER,
)
_collection: Collection | None = None
def get_collection() -> Collection:
    """初始化向量库"""
    global  _collection
    if  _collection is not None:
        return  _collection
    KB_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = PersistentClient(path=str(CHROMA_DIR))
    _collection = client.get_or_create_collection(
        name="knowledge_base",
        metadata={
            "embedding_model": MODEL_NAME,
            "embedding_dim": EMBED_DIM
        }
    )
    return _collection
def load_txt_file(file_path:Path)->str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="gbk") as f:
            return f.read()
def split_text(text: str) -> list[str]:
    """文本分块，调整chunk_size根据你的文档长度"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,        # 每块字符长度
        chunk_overlap=100,     # 块之间重叠，防止上下文断裂
        separators=["\n\n", "\n", "。", "，", " "]
    )
    chunks = splitter.split_text(text)
    return chunks

def import_kb_txt():
    """批量加载KB目录下所有txt，切分，存入向量库"""
    coll = get_collection()
    # 遍历kb文件夹下全部txt文件
    txt_files = list(KB_DIR.glob("*.txt"))
    if not txt_files:
        print("data/kb 目录下没有找到txt文件")
        return

    for txt_path in txt_files:
        print(f"正在加载文档：{txt_path.name}")
        raw_text = load_txt_file(txt_path)
        text_chunks = split_text(raw_text)

        # 生成id和元数据，记录来源文件名
        ids = [f"{txt_path.stem}_{i}" for i in range(len(text_chunks))]
        metadatas = [{"source": txt_path.name} for _ in text_chunks]

        # 生成向量并入库
        embeddings = embeddings_model.embed_documents(text_chunks)
        coll.add(
            documents=text_chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    print("✅ 文档全部导入向量库完成！")
def similarity_search(query: str, top_k: int = 3):
    """检索相关片段"""
    coll = get_collection()
    query_embedding = embeddings_model.embed_query(query)
    result = coll.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return result
if __name__ == "__main__":
    import_kb_txt()