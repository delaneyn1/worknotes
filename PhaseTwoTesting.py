import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import os # Import the os module for path manipulation

vertexai.init(project="project", location="us-east1")

model = GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=[
        """
    Prompt ENTERED HERE
    """,
    ],
)

# --- Configuration for the output bucket ---
OUTPUT_BUCKET_NAME = "prototype_curated_data" #output bucket name
# ------------------------------------------

@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data

    # Log the input event for debugging
    print(f"Processing file: {data['name']} from bucket: {data['bucket']}")

    # download the file
    storage_client = storage.Client()
    input_bucket_name = data["bucket"]
    input_file_name = data["name"]

    blob = storage_client.bucket(input_bucket_name).get_blob(input_file_name)

    if not blob:
        print(f"Error: File {input_file_name} not found in bucket {input_bucket_name}")
        return # Exit the function if the blob doesn't exist

    doc = blob.download_as_text()
    contents = [doc]

    response = model.generate_content(contents)
    formatted_content = response.text

    print(f"Response from Model:\n{formatted_content}")

    # --- Save the formatted content to the output bucket ---
    output_bucket = storage_client.bucket(OUTPUT_BUCKET_NAME)

    # You can customize the output file name.
    # Here, we're prepending "formatted_" to the original file name.
    base_file_name = os.path.basename(input_file_name) # Gets just the file name without directories
    output_file_name = f"formatted_{base_file_name}"

    output_blob = output_bucket.blob(output_file_name)

    # Upload the formatted content as a text file
    output_blob.upload_from_string(formatted_content, content_type="text/plain")

    print(f"Successfully saved formatted content to gs://{OUTPUT_BUCKET_NAME}/{output_file_name}")