import requests

def get_user_info(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["name"],data["email"]

def count_posts_by_user(user_id):
    url = "https://jsonplaceholder.typicode.com/posts"
    params = {'userId': user_id}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return len(response.json())
  
def report_result_core(post_fn, api_url, timestamp, voltage, status):
    """Pure logic — takes a post function as a parameter. This is what gets unit-tested."""
    payload = {"timestamp": timestamp, "voltage": voltage, "status": status}
    try:
        response = post_fn(api_url, json=payload, timeout=10)
        response.raise_for_status()
        data =response.json().get("json", response.json())
        if data != payload:
            print(f"Mismatch — sent {payload}, got back {data}")
            return False
        return data
    except requests.exceptions.RequestException as e:
        print(f"Failed to report result {e}")
        return False

def report_result(api_url, timestamp, voltage,status):
    """Thin wrapper for real use — passes the real requests.post in."""
    return report_result_core(requests.post, api_url, timestamp, voltage, status)

def get_post_titles_by_user_core(get_fn, user_id):
    try:
        url = f"https://jsonplaceholder.typicode.com/posts?userId={user_id}"
        response = get_fn(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        titles = [post["title"] for post in data]
        return titles
    except requests.exceptions.RequestException as e:
        print(f"Request failed with error {e}")
        return None

def get_post_titles_by_user(user_id):
    return get_post_titles_by_user_core(requests.get, user_id)
