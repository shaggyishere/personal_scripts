# 🔧 Convert curl Commands into API Test Configs


## 📌 Purpose

This utility script is designed to help you easily convert a curl command into a JSON config compatible with the `test_deployed_APIs.py ` script.

## ▶️ How to Use

Create a file `curl_to_parse.txt` and paste the curl command you want to parse.

Run the script:
```bash
python curl_to_json.py
```
The script will print and optionally save the equivalent JSON configuration.
This JSON can then be added to apis_to_test.json for automated testing.

## ✅ Example Input

File `curl_to_parse.txt` containing:

```bash
curl --request POST --location 'https://api.example.com/login?lang=en' \
--header 'Content-Type: application/json' \
--data '{
  "username": "admin",
  "password": "1234"
}'
```

### 🧾 Output JSON

File produced under `curl_to_json_output` dir:

```JSON
{
  "method": "POST",
  "route": "/login",
  "params": {
    "lang": "en"
  },
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "username": "admin",
    "password": "1234"
  }
}
```