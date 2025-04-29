from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routes import documents, brainstorms
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware (
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(documents.router, prefix="/api")
app.include_router(brainstorms.router, prefix="/api")

@app.get("/items")
def read_items():
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM items;")
        results = cur.fetchall()
    return {"items": results}

'''
class Author(BaseModel):
    name: str
    email: str

class Brainstorm(BaseModel):
    id: Optional[int] = None
    message: str
    author: Author
    date: int = int(time.time())

class Document(BaseModel):
    id: Optional[str] = None
    title: str
    contributors: Optional[list[Author]] = []
    # We store brainstorms as a dict keyed by brainstorm id.
    brainstorms: Dict[int, Brainstorm] = {}

memory_db = {
    "documents": {},  # key: document_id, value: Document dict
}


@app.get("/")
def read_root():
    return {"message": "AWS"}

# Document endpoints

@app.get("/api/documents/{document_id}", response_model=Document)
def get_document(document_id: str = Path(description="ID of document"), db: Session = Depends(get_db)):
    
    if document_id not in memory_db["documents"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document ID not found.")
    
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document ID not found.")

    return doc

@app.patch("/api/documents/{document_id}")
async def update_document(document_id: str, document: Document):
    if document_id not in memory_db["documents"]:
        raise HTTPException(status_code=404, detail="Document ID not found.")

    existing_document = memory_db["documents"][document_id]

    if document.title is not None:
        existing_document.title = document.title
    
    return existing_document


@app.post("/api/documents")
def create_document(document: Document, db: Session = Depends(get_db)):
    
    try:
        document.id = generate(size=15)
        db.add(document)
        db.commit()
        #db.refresh(document)
    except IntegrityError:
        db.rollback()

    if document_id in memory_db["documents"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document ID already exists.")
    document.id = document_id
    memory_db["documents"][document_id] = document

    return document.id


@app.delete("/api/documents/{document_id}")
def delete_document(document_id: str):
    if document_id not in memory_db["documents"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document ID not found.")

    del memory_db["documents"][document_id]

@app.get("/api/documents", response_model=List[Document])
def get_documents():
    if not memory_db["documents"]:
        return []

    return list(memory_db["documents"].values())


# Brainstorm endpoints

@app.get("/api/documents/{document_id}/brainstorms/{brainstorm_id}", response_model=Brainstorm)
def get_brainstorm(
    document_id: str = Path(description="ID of document"),
    brainstorm_id: int = Path(description="ID of brainstorm")
):
    if document_id not in memory_db["documents"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document ID not found.")

    if brainstorm_id not in memory_db["documents"].get(document_id, {}).brainstorms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brainstorm ID not found.")
    
    return memory_db["documents"].get(document_id, {}).brainstorms[brainstorm_id]

@app.get("/api/documents/{document_id}/brainstorms")
def get_brainstorms(document_id: str = Path(description="ID of document")):
    if document_id not in memory_db["documents"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document ID not found.")

    return list(memory_db["documents"].get(document_id, {}).brainstorms.values())

@app.post("/api/documents/{document_id}/brainstorms", response_model=Brainstorm)
def create_brainstorm(document_id: str, brainstorm: Brainstorm):
    print('Document ID: ', document_id)
    if document_id not in memory_db["documents"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document ID not found.")
    
    doc = memory_db["documents"][document_id] # Get document
    if not doc.brainstorms: # Check if documents has initialized brainstorms dictionary
        doc.brainstorms = {}
    existing_brainstorms = doc.brainstorms # Get existing brainstorms
    brainstorm_id = max(existing_brainstorms.keys(), default=0) + 1 # Generate new brainstorm id
    print('Brainstorm ID: ', brainstorm_id)
    brainstorm.id = brainstorm_id # Set brainstorm id
    doc.brainstorms[brainstorm_id] = brainstorm # Add brainstorm to document
    return brainstorm

@app.delete("/api/documents/{document_id}/brainstorms/{brainstorm_id}")
def delete_brainstorm(document_id: str, brainstorm_id: int):
    if document_id not in memory_db["documents"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Document ID not found.')

    if brainstorm_id not in memory_db["documents"].get(document_id, {}).get("brainstorms", {}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Brainstorm ID not found.')
    
    del memory_db["documents"][document_id].brainstorms[brainstorm_id]






class Item(BaseModel):
    name: str
    price: float
    brand: Optional[str] = None

class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None

inventory = {}

# Path parameter
@app.get("/get-item/{item_id}")
def get_item(item_id: int = Path(description="ID of item")):
    if item_id not in inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item ID not found.")
    return inventory[item_id]

# Query paramter
# http://127.0.0.1:8000/get-by-name?name=Milk
@app.get("/get-by-name")
def get_item(name: Optional[str] = None):
    for item_id in inventory:
        if inventory[item_id].name == name:
            return inventory[item_id]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item name not found.")

@app.post("/create-item/{item_id}")
def create_item(item_id: int, item: Item):
    if item_id in inventory:
        raise HTTPException(status_code=400, detail="Item ID already exists.")
    
    inventory[item_id] = item
    return inventory[item_id]

@app.put("/update-item/{item_id}")
def update_item(item_id: int, item: UpdateItem):
    if item_id not in inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item does not exist.")
    
    if item.name != None:
        inventory[item_id].name = item.name
    if item.price != None:
        inventory[item_id].price = item.price
    if item.brand != None:
        inventory[item_id].brand = item.brand
    
    return inventory[item_id]

@app.delete("/delete-item")
def delete_item(item_id: int = Query(..., description="ID of item to delete")):
    if item_id not in inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item does not exist.")
    
    del inventory[item_id]
'''