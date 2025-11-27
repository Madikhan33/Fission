# RAG Microservice

Оптимизированная RAG система с гибридным поиском на основе BAAI/bge-m3.

## Архитектура

Микросервис работает **независимо** от основного бэкенда:
- **RAG Service**: порт 8001 (без hot-reload)
- **Main Backend**: порт 8000 (с hot-reload)

### Ключевое преимущество
Модель (~2GB) загружается **один раз** при старте RAG сервиса и остается в памяти даже при перезагрузке основного бэкенда.

## Технологии

- **FastAPI** - веб-фреймворк
- **BAAI/bge-m3** - embedding модель (dense + sparse)
- **Milvus** - векторная база данных
- **HNSW** - индекс для dense векторов
- **Sparse Inverted Index** - индекс для sparse векторов
- **RRF (Reciprocal Rank Fusion)** - алгоритм объединения результатов

## Установка

### 1. Установить зависимости

Используя Poetry:

```bash
cd rag_service
poetry install
```

### 2. Запустить Milvus

Используя Docker:

```bash
docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest
```

Или используйте Milvus Standalone/Cluster согласно [документации](https://milvus.io/docs/install_standalone-docker.md).

## Запуск

### RAG Microservice (порт 8001)

```bash
cd rag_service
poetry run python main.py
```

Вы увидите:
```
🚀 Loading BAAI/bge-m3 model...
✅ Model loaded successfully!
✅ RAG Microservice Ready!
```

### Main Backend (порт 8000)

```bash
cd backend
poetry run granian main:app --reload --host 127.0.0.1 --port 8000
```

## API Endpoints

### Индексация документа

```bash
POST http://localhost:8001/api/rag/documents
Content-Type: application/json

{
  "text": "Ваш текст для индексации",
  "document_id": "doc_123",
  "metadata": {"author": "John"}
}
```

### Поиск

```bash
POST http://localhost:8001/api/rag/search
Content-Type: application/json

{
  "query": "поисковый запрос",
  "top_k": 5,
  "search_type": "hybrid"
}
```

**Search types:**
- `hybrid` - комбинация dense + sparse (RRF)
- `dense` - только семантический поиск
- `sparse` - только keyword-based поиск

### Получить документ

```bash
GET http://localhost:8001/api/rag/documents/{document_id}
```

### Удалить документ

```bash
DELETE http://localhost:8001/api/rag/documents/{document_id}
```

### Health Check

```bash
GET http://localhost:8001/api/rag/health
```

## Использование из Main Backend

```python
from rag_client import RAGClient

# В вашем endpoint
@app.post("/analyze")
async def analyze_text(text: str, doc_id: str):
    rag = RAGClient()
    
    # Индексация
    result = await rag.index_document(text, doc_id)
    
    # Поиск
    results = await rag.search("query", top_k=5)
    
    await rag.close()
    return results
```

## Workflow разработки

```bash
# Терминал 1: Запустить RAG сервис (БЕЗ reload)
cd rag_service
poetry run python main.py

# Терминал 2: Разрабатывать основной бэкенд (С reload)
cd backend
poetry run granian main:app --reload
```

**Важно:** При изменении кода в `backend/`, основной сервис перезагрузится, но RAG сервис продолжит работать с загруженной моделью!

## Компоненты

### 1. Embedding Service (Singleton)
- Thread-safe singleton паттерн
- Загрузка модели один раз
- Dense (1024 dim) + Sparse векторы

### 2. Chunking Service
- RecursiveCharacterTextSplitter
- Умное разбиение: параграф → предложение → слово
- Configurable: chunk_size, chunk_overlap

### 3. Milvus Service
- Схема: id, text, document_id, dense_vector, sparse_vector
- HNSW индекс для dense
- Sparse Inverted Index для sparse
- Hybrid search с RRF

### 4. Orchestrator
- Координация всех компонентов
- Pipeline: text → chunks → embeddings → storage
- Поиск: query → embeddings → hybrid search → results

## Тестирование

### Тест Singleton
```python
from embedding_service import EmbeddingService

s1 = EmbeddingService()
s2 = EmbeddingService()
assert s1 is s2  # True - один и тот же объект
```

### Тест Hot-Reload
1. Запустить RAG сервис
2. Запустить main backend
3. Изменить файл в `backend/`
4. Main backend перезагрузится
5. RAG сервис НЕ перезагружается (проверить логи)

## Производительность

- **Загрузка модели**: ~10-20 сек (один раз)
- **Embedding**: <100ms на чанк
- **Hybrid search**: <200ms для top 5 результатов
- **Память**: ~3-4GB с загруженной моделью

## Конфигурация

### Milvus
```python
RAGOrchestrator(
    milvus_host="localhost",
    milvus_port=19530
)
```

### Chunking
```python
RAGOrchestrator(
    chunk_size=500,      # Размер чанка
    chunk_overlap=50     # Overlap между чанками
)
```

### Hybrid Search Weights
```python
await rag.search(
    query="...",
    search_type="hybrid",
    dense_weight=0.7,    # Вес dense поиска
    sparse_weight=0.3    # Вес sparse поиска
)
```

## Troubleshooting

### Milvus не подключается
```bash
# Проверить что Milvus запущен
docker ps | grep milvus

# Проверить логи
docker logs milvus
```

### Модель не загружается
- Проверьте наличие ~4GB свободной RAM
- Проверьте интернет для скачивания модели
- Модель кэшируется в `~/.cache/huggingface/`

### Медленный первый запрос
- Используется warmup при инициализации
- Первый запрос после старта может быть медленнее

## Лицензия

MIT
