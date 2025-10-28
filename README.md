# Google Cloud Storage Data Formatter with AI

This project implements a Google Cloud Function that automatically processes data files uploaded to a specified input Google Cloud Storage (GCS) bucket. It leverages Google's Vertex AI Generative Model (Gemini 2.5 Flash) to apply custom formatting rules to the data, and then saves the transformed output to an output GCS bucket with dynamically generated filenames.

## Features

*   **Event-Driven Processing:** Automatically triggers upon new file uploads to an input GCS bucket.
*   **AI-Powered Data Transformation:** Uses a Vertex AI Generative Model (Gemini 2.5 Flash) to apply complex formatting rules specified in the system instructions.
*   **Dynamic Output Naming:** Extracts a *variable* from the input document and combines it with the processing date to create a unique and descriptive filename for the output.
*   **Serverless Architecture:** Deployed as a Google Cloud Function, eliminating server management overhead.

## How it Works

1.  **Input Data Upload:** A data file is uploaded to the configured input GCS bucket.
2.  **Cloud Function Trigger:** The GCS upload event triggers the `hello_gcs` Google Cloud Function.
3.  **Data Retrieval & variable Extraction:** The function downloads the uploaded file's content. It then attempts to parse the document as JSON to extract the value of the `"*variable*"` key. If JSON parsing fails (e.g., the file is not a complete JSON document), it falls back to a string search for the `""*variable*": "VALUE","` pattern.
4.  **AI Data Formatting:** The entire content of the input file is sent to a pre-configured Vertex AI Generative Model (Gemini 2.5 Flash) with detailed formatting `system_instruction` rules (e.g., date formats, null handling, name parsing, address extraction, vehicle details).
5.  **Output Data Storage:** The formatted content received from the AI model is then saved as a new `.txt` file in a designated output GCS bucket. The filename is constructed as `[*variable*_value]_[YYYYMMDD].txt`
## Setup and Deployment

### Prerequisites

*   A Google Cloud Project
*   `gcloud` CLI installed and authenticated
*   Node.js and `npm` (for `functions-framework` local testing, optional)
*   Two Google Cloud Storage buckets:
    *   One for **input** files (triggers the function).
    *   One for **output** files (where formatted data is saved).
*   Vertex AI API enabled in your Google Cloud Project.
*   Appropriate IAM permissions for your Cloud Function's service account to:
    *   Read from the input GCS bucket.
    *   Write to the output GCS bucket.
    *   Invoke Vertex AI models (`vertexai.generative_models.GenerativeModel`).

### Configuration

1.  **Update `OUTPUT_BUCKET_NAME`:**
    In the `main.py` file (your Cloud Function code), update the `OUTPUT_BUCKET_NAME` variable on line 32 with the actual name of your output GCS bucket:
    ```python
    OUTPUT_BUCKET_NAME = "your-actual-output-bucket-name" # <--- IMPORTANT!
    ```

2.  **`requirements.txt`:**
    Create a `requirements.txt` file in the same directory as your Cloud Function code with the following content:
    ```
    functions-framework==3.*
    google-cloud-storage==2.*
    google-cloud-aiplatform==1.*
    vertexai
    ```

### Deployment to Google Cloud Function

Navigate to the project directory in your terminal and use the `gcloud` CLI to deploy your function:

```bash
gcloud functions deploy hello_gcs \
    --region=*region* \
    --runtime=python311 \
    --source=. \
    --entry-point=hello_gcs \
    --trigger-bucket=[YOUR_INPUT_BUCKET_NAME] \
    --project=*project_ID* \
    --service-account=[YOUR_CLOUD_FUNCTION_SERVICE_ACCOUNT_EMAIL] # e.g., *project_ID*@appspot.gserviceaccount.com