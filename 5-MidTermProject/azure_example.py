"""
Azure Document Intelligence PDF Parser

This module demonstrates how to use Azure Document Intelligence (formerly Form Recognizer)
to parse PDF files and extract all text content.

Requirements:
- azure-ai-documentintelligence package
- Azure Document Intelligence resource with endpoint and API key

Environment Variables Required:
- AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: Your Azure Document Intelligence endpoint URL
- AZURE_DOCUMENT_INTELLIGENCE_KEY: Your Azure Document Intelligence API key
"""

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Document Intelligence credentials
AZURE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

if AZURE_ENDPOINT is None or AZURE_KEY is None:
    raise ValueError(
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY "
        "must be set in environment variables"
    )


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file using Azure Document Intelligence.
    
    Args:
        pdf_path: Path to the PDF file to parse
        
    Returns:
        str: Extracted text content from the PDF
    """
    try:
        # Initialize the Document Intelligence client
        client = DocumentIntelligenceClient(
            endpoint=AZURE_ENDPOINT,
            credential=AzureKeyCredential(AZURE_KEY)
        )
        
        logger.info(f"Reading PDF file: {pdf_path}")
        
        # Read the PDF file
        with open(pdf_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
        
        logger.info("Sending document to Azure Document Intelligence for analysis...")
        
        # Analyze the document
        # Using the "prebuilt-read" model to extract all text
        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            analyze_request=pdf_data,
            content_type="application/pdf"
        )
        
        # Wait for the analysis to complete
        result = poller.result()
        
        logger.info("Document analysis completed successfully")
        
        # Extract text from all pages
        extracted_text = []
        
        if result.content:
            # If there's direct content, add it
            extracted_text.append(result.content)
        
        # Extract text from each page
        if result.pages:
            for page in result.pages:
                if page.lines:
                    page_text = "\n".join([line.content for line in page.lines])
                    extracted_text.append(page_text)
        
        # Combine all extracted text
        full_text = "\n\n".join(extracted_text)
        
        logger.info(f"Extracted {len(full_text)} characters from the PDF")
        
        return full_text
        
    except FileNotFoundError:
        logger.error(f"PDF file not found: {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise


def extract_text_with_metadata(pdf_path: str) -> dict:
    """
    Extract text and metadata from a PDF file using Azure Document Intelligence.
    
    Args:
        pdf_path: Path to the PDF file to parse
        
    Returns:
        dict: Dictionary containing extracted text and metadata
    """
    try:
        # Initialize the Document Intelligence client
        client = DocumentIntelligenceClient(
            endpoint=AZURE_ENDPOINT,
            credential=AzureKeyCredential(AZURE_KEY)
        )
        
        logger.info(f"Reading PDF file: {pdf_path}")
        
        # Read the PDF file
        with open(pdf_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
        
        logger.info("Sending document to Azure Document Intelligence for analysis...")
        
        # Analyze the document
        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            analyze_request=pdf_data,
            content_type="application/pdf"
        )
        
        # Wait for the analysis to complete
        result = poller.result()
        
        logger.info("Document analysis completed successfully")
        
        # Extract text
        extracted_text = []
        
        if result.content:
            extracted_text.append(result.content)
        
        if result.pages:
            for page in result.pages:
                if page.lines:
                    page_text = "\n".join([line.content for line in page.lines])
                    extracted_text.append(page_text)
        
        full_text = "\n\n".join(extracted_text)
        
        # Extract metadata
        metadata = {
            "page_count": len(result.pages) if result.pages else 0,
            "model_id": result.model_id,
            "api_version": result.api_version,
            "content_length": len(full_text),
        }
        
        # Add page-level metadata if available
        if result.pages:
            metadata["pages"] = []
            for i, page in enumerate(result.pages):
                page_meta = {
                    "page_number": i + 1,
                    "width": page.width if hasattr(page, 'width') else None,
                    "height": page.height if hasattr(page, 'height') else None,
                    "unit": page.unit if hasattr(page, 'unit') else None,
                    "line_count": len(page.lines) if page.lines else 0,
                }
                metadata["pages"].append(page_meta)
        
        return {
            "text": full_text,
            "metadata": metadata
        }
        
    except FileNotFoundError:
        logger.error(f"PDF file not found: {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise


if __name__ == "__main__":
    # Example usage
    # Replace with your PDF file path
    pdf_file_path = "example.pdf"  # Update this path to your PDF file
    
    try:
        # Extract text only
        print("=" * 80)
        print("Extracting text from PDF...")
        print("=" * 80)
        text = extract_text_from_pdf(pdf_file_path)
        print("\nExtracted Text:")
        print("-" * 80)
        print(text)
        print("-" * 80)
        
        # Extract text with metadata
        print("\n" + "=" * 80)
        print("Extracting text with metadata...")
        print("=" * 80)
        result = extract_text_with_metadata(pdf_file_path)
        print(f"\nText Length: {result['metadata']['content_length']} characters")
        print(f"Number of Pages: {result['metadata']['page_count']}")
        print(f"Model Used: {result['metadata']['model_id']}")
        print("\nExtracted Text:")
        print("-" * 80)
        print(result['text'])
        print("-" * 80)
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease set the following environment variables:")
        print("- AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        print("- AZURE_DOCUMENT_INTELLIGENCE_KEY")
    except FileNotFoundError as e:
        print(f"File Error: {e}")
        print(f"\nPlease ensure the PDF file exists at: {pdf_file_path}")
    except Exception as e:
        print(f"Error: {e}")

