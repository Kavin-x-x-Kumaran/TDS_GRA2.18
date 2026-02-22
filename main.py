import csv
import io
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# Initialize the FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["POST"],  # Only allows POST requests as per assignment
    allow_headers=["*"],  # Allows all headers (we need this for our custom token header)
)

# Let's add a quick test route just to make sure it runs (Optional but good practice)
@app.post("/upload")
async def process_file(
    file: UploadFile = File(...),
    x_upload_token_5457: str = Header(default=None, alias="X-Upload-Token-5457")
):
    # 1. Authentication Validation
    if x_upload_token_5457 != "yy6jmepd5b6x018u":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. File Type Validation
    allowed_extensions = (".csv", ".json", ".txt")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(status_code=400, detail="Bad Request: Only .csv, .json, and .txt files are allowed")

    # 3. File Size Validation
    file_contents = await file.read()
    max_size_bytes = 92 * 1024
    if len(file_contents) > max_size_bytes:
        raise HTTPException(status_code=413, detail="Payload Too Large: File exceeds 92KB")

    # 4. Data Processing (Only for CSV files)
    if file.filename.lower().endswith(".csv"):
        # Decode the bytes into a standard string
        text = file_contents.decode('utf-8')
        
        # Read the string as a CSV using DictReader (reads rows as dictionaries)
        reader = csv.DictReader(io.StringIO(text))
        
        # Initialize our counters
        rows_count = 0
        total_value = 0.0
        category_counts = {}
        
        # Loop through each row in the CSV
        for row in reader:
            rows_count += 1
            
            # Safely add to totalValue (converting string to float)
            try:
                total_value += float(row.get('value', 0))
            except ValueError:
                pass # Skips the math if the value cell is empty or invalid
                
            # Count the categories
            category = row.get('category')
            if category:
                if category in category_counts:
                    category_counts[category] += 1
                else:
                    category_counts[category] = 1
                    
        # Return the exact JSON structure requested by your assignment
        return {
            "email": "24f2003806@ds.study.iitm.ac.in",
            "filename": file.filename,
            "rows": rows_count,
            "columns": reader.fieldnames if reader.fieldnames else [],
            "totalValue": round(total_value, 2), # Rounds to 2 decimal places
            "categoryCounts": category_counts
        }
    
    # If it's a valid .txt or .json, but not a .csv, we just return a success message
    return {"message": f"Successfully uploaded {file.filename}, but analysis is only for CSVs."}