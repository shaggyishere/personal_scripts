import json
import shlex
import os
from urllib.parse import urlparse, parse_qs


def parse_curl_file(file_path="curl_command.txt"):
    with open(file_path, "r") as f:
        curl_command = f.read().strip()

    return parse_curl_command(curl_command)


def parse_curl_command(curl_command: str) -> dict:
    tokens = shlex.split(curl_command)
    result = {
        "method": "GET",
        "route": "",
        "headers": {},
        "params": {},
        "body": {}
    }

    url_found = False
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "curl":
            i += 1
        elif token in ("-X", "--request"):
            result["method"] = tokens[i + 1].upper()
            i += 2
        elif token in ("-H", "--header"):
            header = tokens[i + 1]
            key, value = header.split(":", 1)
            result["headers"][key.strip()] = value.strip()
            i += 2
        elif token in ("-d", "--data", "--data-raw"):
            data_str = tokens[i + 1]
            try:
                result["body"] = json.loads(data_str)
            except json.JSONDecodeError:
                body_items = data_str.split("&")
                result["body"] = {k: v for k, v in (item.split("=") for item in body_items)}
            i += 2
        elif token in ("--url",):
            url = tokens[i + 1]
            url_found = True
            parsed_url = urlparse(url)
            result["route"] = parsed_url.path
            result["params"] = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
            i += 2
        elif token.startswith("http"):
            if not url_found:
                parsed_url = urlparse(token)
                result["route"] = parsed_url.path
                result["params"] = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
                url_found = True
            i += 1
        else:
            i += 1

    return result


def save_to_json(data, filename="output.json", directory="curl_to_json_output"):
    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, filename)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":

    script_dir = os.path.dirname(os.path.abspath(__file__)) 

    curl_command_file_path = os.path.join(script_dir, "curl_command.txt")

    config = parse_curl_file(curl_command_file_path)
    save_to_json(config)
    print(f"✅ Parsed curl command and saved json config to 'curl_to_json_output' directory")

