"""main.py"""

import json
from uuid import uuid4

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import DATA_DIR

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/upload/notes")
async def upload_notes(file: UploadFile = Form(...), metadata: str = Form(...)):
    """
    Upload clinical notes to the server.

    Parameters
    ----------
    file : UploadFile
        The PDF file containing the clinical notes.
    metadata : str
        A JSON string containing the metadata for the clinical notes.
    """

    metadata = json.loads(metadata)

    try:
        basename = uuid4()
        pdf_fp = DATA_DIR.joinpath("notes", f"{basename}.pdf")
        json_fp = DATA_DIR.joinpath("notes", f"{basename}.json")

        # Ensure the 'notes' directory exists
        pdf_fp.parent.mkdir(parents=True, exist_ok=True)

        # Save the PDF file
        with pdf_fp.open("wb") as buffer:
            buffer.write(await file.read())

        # Save the metadata as a JSON file
        with json_fp.open("w") as json_file:
            json.dump(metadata, json_file)

        return JSONResponse(
            content={
                "message": "Files uploaded successfully.",
                "filename": str(basename),
            },
            status_code=200,
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
