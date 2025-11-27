import json
from typing import List, Optional
from io import BytesIO

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from pypdf import PdfReader
from .schemas import ResumeExtraction 
from core.config import settings

# Define the output structure for the LLM extraction



async def extract_data_from_pdf(file_content: bytes) -> dict:

    # 1. Extract text from PDF
    try:
        pdf_file = BytesIO(file_content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")

    if not text.strip():
        raise ValueError("PDF contains no extractable text.")

    # 2. Setup LLM and Prompt
    # Using gpt-4o for better extraction quality, fallback to gpt-3.5-turbo if needed
    llm = ChatOpenAI(
        model="gpt-4o", 
        api_key=settings.openai_api_key,
        temperature=0
    )

    parser = PydanticOutputParser(pydantic_object=ResumeExtraction)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert HR assistant. Extract the following information from the resume text provided below. "
                   "If a field is missing or cannot be inferred, leave it as null. "
                   "Ensure the output is valid JSON matching the schema."
                   'Try to write everything in detail and correctly'),
        ("user", "Resume Text:\n{text}\n\n{format_instructions}")
    ])

    chain = prompt | llm | parser

    # 3. Invoke Chain
    try:
        result = await chain.ainvoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        
        # 4. Convert to dict and handle JSON fields for DB
        data = result.model_dump()
        
        # Convert lists to JSON strings for the database as per models.py
        if data.get("core_skills") is not None:
            data["core_skills"] = json.dumps(data["core_skills"], ensure_ascii=False)
        
        if data.get("languages") is not None:
            data["languages"] = json.dumps(data["languages"], ensure_ascii=False)
            
        return data

    except Exception as e:
        # Log the error here if you have a logger
        print(f"AI Extraction Error: {e}")
        raise ValueError(f"AI extraction failed: {e}")
