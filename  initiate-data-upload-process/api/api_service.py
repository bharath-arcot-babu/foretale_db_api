import requests

class ApiService:
    def call_api_with_error_handling(self, method, url, *, params=None, json=None, headers=None):
        try:
            response = requests.request(
                url=url,
                params=params,
                json=json,
                headers=headers
            )
            response.raise_for_status()

            result = response.json()
            return result.get("data", [])

        except requests.exceptions.HTTPError as http_err:
            status_code = response.status_code
            error_message = response.text

            if status_code == 400:
                raise Exception(f"Bad Request (400): {error_message}")
            elif status_code == 401:
                raise Exception(f"Unauthorized (401): {error_message}")
            elif status_code == 403:
                raise Exception(f"Forbidden (403): {error_message}")
            elif status_code == 404:
                raise Exception(f"Not Found (404): {error_message}")
            elif status_code == 500:
                raise Exception(f"Internal Server Error (500): {error_message}")
            else:
                raise Exception(f"HTTP {status_code}: {error_message}")

        except requests.exceptions.RequestException as req_err:
            raise Exception(f"Request failed: {str(req_err)}")

        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
