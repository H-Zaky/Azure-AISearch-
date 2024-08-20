import azure.functions as func
import logging
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import re
import json
import requests
from datetime import datetime
from langdetect import detect
import sys
import Fields


# ======================================= Azure API Connection =========================================
endpoint = "YourAzureOpenAIEndpoint"
api_key = "YourAzureOpenAIKey"
deployment = "YourDeploymentName"
search_endpoint = "YourSearchEndpoint"
search_index = "YourSearchIndex"
search_key = "YourSearchKey"

fields = Fields.fields

field_names = {field["name"] for field in fields}
current_date = datetime.now().strftime("%Y")
print(current_date)

def parse_synonyms(synonym_string):
    synonyms_dict = {}
    for synonym in synonym_string.split(","):
        parts = synonym.split(":")
        if len(parts) == 2:
            key, values = parts
            synonyms_dict[key.strip().lower()] = [v.strip().lower() for v in values.split("|")]
    return synonyms_dict

# Build the complete synonyms dictionary
synonyms = {}
for field in fields:
    if "synonymMaps" in field:
        for synonym_map in field["synonymMaps"]:
            synonyms.update(parse_synonyms(synonym_map))

def normalize_value(field, value):
    if field in synonyms:
        for normalized_value, synonym_list in synonyms[field].items():
            if value.lower() in synonym_list:
                return normalized_value.capitalize()
    return value.capitalize()

# Function to map user input to search fields using OpenAI's completion
def map_input_to_fields(user_input, fields, client, deployment):
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI assistan. "
                    "You must always reply with the searchable correct fields names from the user's input, "
                    "ensuring they match the predefined field names exactly. "
                    "Provide the response in the format: 'field': 'value'. For example: "
                    "'field': 'gender', 'value': 'Female or Male', "
                    "'field': 'age', 'value': 'number only'."
                    "'field': 'graduationFrom', 'value': 'university name'. "
                    "'field': 'yearOfExperience', 'value': 'number only'. You must convert value to Number as String. "
                    "Only use the following field names: " + ", ".join(field_names) + ". "
                    f"If the user's input is a range, the response should include all years from the current year back to the specified number of years. Current date is: {current_date}. For example: if the user asks for X years, start from {current_date} year value and move back down for X years separated by ',' operator, e.g., '2024,2023,2022'."
                )
            },
            {"role": "user", "content": user_input}
        ]
    )
    response_content = response.choices[0].message.content
    # print("Raw AI Response:", response_content)

    # Extracting the mapped fields from the response
    mapped_fields = re.findall(r"'field':\s*'(.*?)',\s*'value':\s*'(.*?)'", response_content)
    mapped_fields = {field: normalize_value(field, value) for field, value in mapped_fields if field in field_names}
    return mapped_fields

def create_search_query(mapped_fields, fields):
    search_values = []
    search_fields = []
    filters = []

    for key, value in mapped_fields.items():
        field_info = next((f for f in fields if f['name'] == key), None)
        if field_info:
            if field_info["searchable"]:
                search_fields.append(key)
                if key == "yearOfGraduation" and "," in value:
                    year_conditions = " OR ".join([f'{key}:{year}' for year in value.split(",")])
                    search_values.append(f"({year_conditions})")
                else:
                    search_values.append(f'{key}:"{value}"')
            if field_info["filterable"]:
                filters.append(f"{key} eq {value}" if field_info['type'] == 'Edm.Int32' else f"{key} eq '{value}'")

    search_query = {
        "search": " AND ".join(search_values),
        "searchFields": ",".join(search_fields),
        "filter": " and ".join(filters) if filters else None,
    }

    # Remove 'filter' if it's empty
    if not search_query["filter"]:
        del search_query["filter"]

    return search_query



app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        question = req_body.get('question')

        if not question:
            return func.HttpResponse(
                "Please pass a 'question' in the request body",
                status_code=400
            )

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-01",
        )

        mapped_fields = map_input_to_fields(question, fields, client, deployment)
        print("Mapped Fields:", mapped_fields)

        search_query = create_search_query(mapped_fields, fields)
        print("Search Query:", json.dumps(search_query, indent=2))

        # ======================================= Azure Search Service =========================================
        search_url = f'{search_endpoint}/indexes/{search_index}/docs/search?api-version={_version}'
        print(search_url)

        headers = {
            'Content-Type': 'application/json',
            'api-key': search_key
        }
        
        response = requests.post(search_url, headers=headers, data=json.dumps(search_query))
        
        if response.status_code == 200:
            search_results = response.json()
            decoded_results = json.dumps(search_results, ensure_ascii=False, indent=2)
            return func.HttpResponse(decoded_results, mimetype="application/json", status_code=200)
        else:
            return func.HttpResponse(f'Error: Fail to connect to the search service, {str(search_url)}', status_code=response.status_code)
        # ======================================= Azure Search Service =========================================

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error processing request: {str(e)}", status_code=500)