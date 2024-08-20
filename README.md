# Azure Function with Azure OpenAI and Azure Cognitive Search Integration

## This ReadMe File is for Documentation Purposes only, using the exact code will not work as you need to identify some variables from your end

This repository contains an Azure Function designed to integrate with the Azure OpenAI service and Azure Cognitive Search. The function processes HTTP requests to map user input to searchable fields using the OpenAI API, and then performs a search query against an Azure Cognitive Search index. It supports both English and Arabic languages and formats the search results based on the detected language.

## Features

- **Language Detection**: Automatically detects whether the user input is in English or Arabic.
- **Field Mapping**: Uses the Azure OpenAI service to map user input to predefined searchable fields.
- **Search Query Construction**: Constructs a search query based on the mapped fields and submits it to Azure Cognitive Search.
- **Language-Specific Formatting**: Formats the search results according to the detected language.
- **Error Handling**: Provides error handling and logging for failed operations.

## Prerequisites

Before running this function, ensure you have the following set up:

1. **Azure Account**: You must have an active Azure account with access to Azure OpenAI and Azure Cognitive Search.
2. **Azure OpenAI Service**: An OpenAI resource with a deployment for chat completions.
3. **Azure Cognitive Search**: A search service with an index ready for queries.
4. **Python 3.9+**: The function is developed using Python 3.9. Ensure you have the correct version installed.

## Environment Variables

The following environment variables need to be set in the `.env` file for the function to work correctly:

- `AzureOpenAIEndpoint`: The endpoint for your Azure OpenAI service.
- `AzureOpenAIKey`: The API key for your Azure OpenAI service.
- `ChatCompletionsDeploymentName`: The name of the deployment for chat completions.
- `SearchEndpoint`: The endpoint for your Azure Cognitive Search service.
- `SearchIndex`: The name of the search index.
- `SearchKey`: The API key for your Azure Cognitive Search service.

## Installation

1. Clone this repository to your local machine.

2. Install the required Python packages.

    ```sh
    pip install -r requirements.txt
    ```

3. Set up your environment variables by creating a `.env` file in the root directory of the project:

    ```plaintext
    AzureOpenAIEndpoint=<Your Azure OpenAI Endpoint>
    AzureOpenAIKey=<Your Azure OpenAI API Key>
    ChatCompletionsDeploymentName=<Your Deployment Name>
    SearchEndpoint=<Your Search Service Endpoint>
    SearchIndex=<Your Search Index Name>
    SearchKey=<Your Search Service API Key>
    ```

4. Deploy the function to Azure using the Azure Functions Core Tools or via the Azure portal.

## Usage

- **Endpoint**: The function is exposed via an HTTP trigger.
- **Request**: Send a POST request with a JSON body containing a `question` key.
  
    Example:

    ```json
    {
        "question": "Show me all documents from 2023."
    }
    ```

- **Response**: The function returns the search results in JSON format, formatted according to the detected language (English or Arabic).

## Logging

The function logs important steps and errors, which can be viewed in the Azure portal or locally via the terminal when running the function.

