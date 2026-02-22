import csv
import io
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# 1. Standard CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    Access-Control-Allow-Origin= ["*"]
)

# 2. Nuclear Option: Force headers on every single request
@app.middleware("http")
async def force_cors_headers(request: Request, call_next):
    # Handle preflight OPTIONS requests directly
    if request.method == "OPTIONS":
        response = JSONResponse(content="OK")
    else:
        response = await call_next(request)
        
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# 3. Catch both the root URL and /upload just in case
@app.post("/")
@app.post("/upload")
async def process_file(
    file: UploadFile = File(...),
    x_upload_token_5457: str = Header(default=None, alias="X-Upload-Token-5457")
):
    # Authentication Validation
    if x_upload_token_5457 != "yy6jmepd5b6x018u":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # File Type Validation
    allowed_extensions = (".csv", ".json", ".txt")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Bad Request: Only .csv, .json, and .txt files are allowed")

    # File Size Validation
    file_contents = await file.read()
    max_size_bytes = 92 * 1024
    if len(file_contents) > max_size_bytes:
        raise HTTPException(status_code=413, detail="Payload Too Large: File exceeds 92KB")

    # Data Processing
    if file.filename.lower().endswith(".csv"):
        text = file_contents.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        
        rows_count = 0
        total_value = 0.0
        category_counts = {}
        
        for row in reader:
            rows_count += 1
            try:
                total_value += float(row.get('value', 0))
            except ValueError:
                pass
                
            category = row.get('category')
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
                    
        return {
            "email": "24f2003806@ds.study.iitm.ac.in",
            "filename": file.filename,
            "rows": rows_count,
            "columns": reader.fieldnames if reader.fieldnames else [],
            "totalValue": round(total_value, 2),
            "categoryCounts": category_counts
        }
    
    return {"message": "Success"}

