import os, time, multiprocessing, hashlib, base58, requests
# 'pip install coincurve pyTelegramBotAPI' zaroori hai

try:
    from coincurve import PublicKey
    HAS_COINCURVE = True
except:
    HAS_COINCURVE = False

# --- CONFIGURATION ---
BOT_TOKEN = "8711590963:AAH1WxtYCOjxTPIShWzf0zgYjo6gQFB2Uq4"
CHAT_ID = "8619569939"
TARGET_PREFIX = "1PWo3JeB" # Target ka shuruat
FULL_TARGET = "1PWo3JeDH15vMK1KFH4x28zTXyX9XV8aWA"
START_HEX_INT = 0x7fffffffffdf00000 

def send_to_bot(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

def worker_logic(start_point, worker_id):
    count = 0
    start_time = time.time()
    
    while True:
        current_hex = hex(start_point + count)[2:].zfill(64)
        
        # High Speed Generation
        if HAS_COINCURVE:
            pub = PublicKey.from_valid_secret(bytes.fromhex(current_hex)).format(compressed=True)
        else:
            # Fallback agar library missing ho (Slow)
            continue 

        h = hashlib.new('ripemd160', hashlib.sha256(pub).digest()).digest()
        addr = base58.b58encode_check(b'\x00' + h).decode()
        
        # Match Check
        if addr.startswith(TARGET_PREFIX):
            send_to_bot(f"🔔 *Potential Match!* \nAddr: `{addr}`\nHEX: `{current_hex}`\nWorker: {worker_id}")
            if addr == FULL_TARGET:
                send_to_bot(f"🚨 *JACKPOT FOUND!* 🚨\n\nAddr: `{addr}`\nHEX: `{current_hex}`")
                break
        
        count += 1
        # Har 10 lakh keys par status update (Sirf Worker 0 se)
        if count % 1000000 == 0 and worker_id == 0:
            elapsed = time.time() - start_time
            speed = int(1000000 * multiprocessing.cpu_count() / elapsed)
            send_to_bot(f"👷 Worker-0 Status: `{count:,}` keys checked. Speed: `{speed} k/s`")

if __name__ == "__main__":
    cores = multiprocessing.cpu_count()
    send_to_bot(f"🚀 *Worker Online!* \nCores Active: {cores}\nTarget: {TARGET_PREFIX}")
    
    processes = []
    for i in range(cores):
        # Har core ko alag jump point do
        p = multiprocessing.Process(target=worker_logic, args=(START_HEX_INT + (i * 0x10000000), i))
        processes.append(p)
        p.start()
