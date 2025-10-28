import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import os
import datetime
import json

vertexai.init(project="PROJECT", location="us-east1")

model = GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=[
        """
    PROMPT ENTERED HERE
    """,
    ],
)

OUTPUT_BUCKET_NAME = "prototype_curated_data"

@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data

    print(f"Processing file: {data['name']} from bucket: {data['bucket']}")

    storage_client = storage.Client()
    input_bucket_name = data["bucket"]
    input_file_name = data["name"]

    blob = storage_client.bucket(input_bucket_name).get_blob(input_file_name)

    if not blob:
        print(f"Error: File {input_file_name} not found in bucket {input_bucket_name}")
        return

    doc = blob.download_as_text()

    # --- Extract scrapy_spider using JSON parsing ---
    scrapy_spider_name = "unknown_spider" # Default value
    try:
        # Assuming the entire document might be a valid JSON or
        # at least contains a parsable JSON snippet for the 'scrapy_spider'
        # If the whole doc is NOT JSON but contains the string ""scrapy_spider": "VALUE"",
        # you might need to extract that substring first and then parse it.
        # For typical JSON documents, json.loads(doc) will work.
        
        # If the file is a well-formed JSON document
        json_data = json.loads(doc)
        scrapy_spider_name = json_data.get("scrapy_spider", "unknown_spider")
        
    except json.JSONDecodeError as e:
        print(f"Input file is not a valid JSON document: {e}")
        print(f"Attempting to find 'scrapy_spider' as a substring...")
        # Fallback to string searching if it's not a full JSON document
        search_string = '"scrapy_spider": "'
        start_index = doc.find(search_string)
        if start_index != -1:
            start_index += len(search_string)
            end_index = doc.find('"', start_index)
            if end_index != -1:
                scrapy_spider_name = doc[start_index:end_index]
                print(f"Found scrapy_spider via string search: {scrapy_spider_name}")
            else:
                print("Could not find closing quote for scrapy_spider value via string search.")
        else:
            print("Could not find 'scrapy_spider' string in document.")
            
    except Exception as e:
        print(f"An unexpected error occurred during scrapy_spider extraction: {e}")

    # --- Continue with model processing ---
    contents = [doc] # The model still processes the original full document
    response = model.generate_content(contents)
    formatted_content = response.text

    print(f"Response from Model:\n{formatted_content}")

    # --- Save the formatted content to the output bucket ---
    output_bucket = storage_client.bucket(OUTPUT_BUCKET_NAME)

    # Get the current date in YYYYMMDD format
    current_date = datetime.date.today().strftime("%Y%m%d")

    # Construct the output file name
    # Example: US_AL_Statewide_SOR_20231027.txt
    output_file_name = f"{scrapy_spider_name}_{current_date}.txt"

    output_blob = output_bucket.blob(output_file_name)
    output_blob.upload_from_string(formatted_content, content_type="text/plain")

    print(f"Successfully saved formatted content to gs://{OUTPUT_BUCKET_NAME}/{output_file_name}")