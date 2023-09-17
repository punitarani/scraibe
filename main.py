"""main.py"""

import csv
import json
from pathlib import Path
from uuid import uuid4

from codeinterpreterapi import File
from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import DATA_DIR
from scraibe.agent import analyze_data, generate_graphs
from scraibe.pdf import pdf_to_txt
from scraibe.utils import del_dir

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


files = [
    File.from_path("data/split/d_hcpcs.csv"),
    File.from_path("data/split/patients.csv"),
    File.from_path("data/split/hcpcsevents.csv"),
    File.from_path("data/split/icustays.csv"),
    File.from_path("data/split/procedures_icd.csv"),
    File.from_path("data/split/drgcodes.csv"),
    File.from_path("data/split/transfers.csv"),
    File.from_path("data/split/diagnoses_icd.csv"),
    File.from_path("data/split/microbiologyevents.csv"),
    File.from_path("data/split/outputevents.csv"),
    File.from_path("data/split/prescriptions.csv"),
    File.from_path("data/split/pharmacy.csv"),
    File.from_path("data/split/d_items.csv"),
]


def add_to_index(index_path: Path, file_id: str, filename: str) -> None:
    """
    Append file info to the index CSV.

    Parameters
    ----------
    index_path : Path
        Path to the index CSV file.
    file_id : str
        Unique ID for the file.
    filename : str
        Original filename from the metadata.
    """

    with index_path.open("a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([file_id, filename])


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

    # Ensure "filename" is a key in the metadata
    filename = metadata.get("filename", None)
    if not filename:
        return JSONResponse(
            content={"error": "Metadata must contain a 'filename' key."},
            status_code=400,
        )

    basename = str(uuid4())
    base_dir = DATA_DIR.joinpath("notes", basename)
    pdf_fp = base_dir.joinpath(f"{basename}.pdf")
    txt_fp = base_dir.joinpath(f"{basename}.txt")
    json_fp = base_dir.joinpath(f"{basename}.json")

    try:
        # Ensure the 'notes' directory exists
        pdf_fp.parent.mkdir(parents=True, exist_ok=True)

        # Save the PDF file
        try:
            with pdf_fp.open("wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

        # Save the metadata as a JSON file
        try:
            with json_fp.open("w") as json_file:
                json.dump(metadata, json_file)
        except Exception as e:
            pdf_fp.unlink()
            return JSONResponse(content={"error": str(e)}, status_code=500)

        # Convert the pdf file to a text file
        try:
            pdf_to_txt(pdf_fp, txt_fp)
        except Exception as e:
            pdf_fp.unlink()
            json_fp.unlink()
            return JSONResponse(content={"error": str(e)}, status_code=500)

        # Add file to index
        index_path = DATA_DIR.joinpath("notes", "index.csv")
        add_to_index(index_path, basename, filename)

        return JSONResponse(
            content={
                "message": "Files uploaded successfully.",
                "filename": basename,
            },
            status_code=200,
        )

    except Exception as e:
        del_dir(base_dir)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/analysis")
async def get_analysis():
    """
    Get the analysis from the server.
    """
    answer = await analyze_data(files=files)
    return JSONResponse(content=answer, status_code=200)


@app.get("/graphs")
async def get_graphs():
    """
    Get the graphs from the server.
    """
    data = await analyze_data(files=files)
    answer = await generate_graphs(files=files, data=data)
    return JSONResponse(content=answer, status_code=200)


@app.get("/get_image/{image_path:path}")
async def get_image(image_path: str):
    return FileResponse(DATA_DIR.joinpath("visualizations", image_path))
