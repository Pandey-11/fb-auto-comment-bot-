import requests
import time
import random
from datetime import datetime

# === BANNER ===
print("""
\033[1;31m███████╗██╗░░░░░░█████╗░░█████╗░██╗░░██╗  ██╗░░░██╗██╗░░░██╗
██╔════╝██║░░░░░██╔══██╗██╔══██╗╚██╗██╔╝  ██║░░░██║╚██╗░██╔╝
█████╗░░██║░░░░░██║░░██║███████║░╚███╔╝░  ██║░░░██║░╚████╔╝░
██╔══╝░░██║░░░░░██║░░██║██╔══██║░██╔██╗░  ██║░░░██║░░╚██╔╝░░
██║░░░░░███████╗╚█████╔╝██║░░██║██╔╝╚██╗  ╚██████╔╝░░░██║░░░
╚═╝░░░░░╚══════╝░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝  ░╚═════╝░░░░╚═╝░░░
\033[0m
""")

# === USER INPUT ===
post_id = input("🔗 Enter Facebook Post ID: ")
comments_file = input("📂 Enter path to comment file (e.g. comment.txt): ")
repeat_count = int(input("🔁 Enter number of comments (repeat): "))
delay_seconds = int(input("⏱️ Delay (seconds) between comments: "))

# === LOAD COMMENTS ===
try:
    with open(comments_file, "r", encoding="utf-8") as f:
        all_comments = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"[×] Failed to load comments file: {e}")
    exit()

if not all_comments:
    print("[×] No comments found in the file.")
    exit()

# === LOAD TOKENS ===
try:
    with open("tokens.txt", "r") as file:
        tokens = [line.strip() for line in file if line.strip()]
except Exception as e:
    print(f"[×] Failed to load tokens.txt: {e}")
    exit()

# === CHECK INTERNET ===
def internet_ok():
    try:
        requests.head("https://www.google.com", timeout=3)
        return True
    except:
        return False

# === VALIDATE TOKEN ===
def get_user_info(token):
    try:
        res = requests.get(f"https://graph.facebook.com/v23.0/me?access_token={token}", timeout=5).json()
        if 'name' in res:
            return {'valid': True, 'name': res['name'], 'id': res['id']}
        else:
            return {'valid': False, 'error': res.get('error', {}).get('message', 'Unknown')}
    except:
        return {'valid': False, 'error': 'Network Error'}

# === COMMENT FUNCTION ===
def send_comment(token, post_id, message):
    try:
        response = requests.post(
            f"https://graph.facebook.com/v23.0/{post_id}/comments",
            data={'message': message, 'access_token': token},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {'error': {'message': str(e)}}

# === VALIDATE ALL TOKENS ===
token_info = []
print("\n🔍 Checking tokens...\n")
for token in tokens:
    info = get_user_info(token)
    if info['valid']:
        print(f"[✓] VALID: {info['name']} (ID: {info['id']})")
        token_info.append({'token': token, 'name': info['name'], 'id': info['id']})
    else:
        print(f"[✘] INVALID TOKEN: {info['error']}")

if not token_info:
    print("\n[×] No valid tokens found. Exiting...")
    exit()

print(f"\n✅ Total Valid Tokens: {len(token_info)}\n")

# === START COMMENTING ===
print("[🚀] Starting...\n")
count = 0
comment_index = 0
token_index = 0

while count < repeat_count:
    if not internet_ok():
        print("[!] No internet. Retrying in 5 seconds...")
        time.sleep(5)
        continue

    user = token_info[token_index]
    comment = all_comments[comment_index % len(all_comments)]

    now = datetime.now().strftime("%H:%M:%S")
    response = send_comment(user['token'], post_id, comment)

    if "id" in response:
        print(f"\033[1;36m[{count + 1}] ✅ Commented by {user['name']} at {now}")
        print(f"📝 {comment}\n\033[0m")
        count += 1
        comment_index += 1
    else:
        error_msg = response.get('error', {}).get('message', 'Unknown')
        print(f"\033[1;31m[×] {user['name']} failed: {error_msg}\033[0m")
        del token_info[token_index]
        if not token_info:
            print("\n[×] All tokens expired or failed. Exiting...")
            break
        if token_index >= len(token_info):
            token_index = 0
        continue

    token_index = (token_index + 1) % len(token_info)
    time.sleep(delay_seconds + random.uniform(1, 3))
