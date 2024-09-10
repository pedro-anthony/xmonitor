import requests
import json
import time
from tabulate import tabulate
from colorama import Fore, Style, Back, init

# Initialize colorama
init(autoreset=True)

# Load worker URLs from workers.json
def load_worker_urls():
    try:
        with open("workers.json", "r") as f:
            return json.load(f).get("urls", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Helper functions
def convert_bytes_to_mb(bytes_value):
    return round(bytes_value / (1024 * 1024), 2)

def load_cache():
    try:
        with open("cache.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    with open("cache.json", "w") as f:
        json.dump(cache, f, indent=4)

def clear_screen():
    print("\033c", end="")

def get_worker_data(url, cache):
    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        worker_id = data.get("worker_id", "N/A")
        hashrate = data.get("hashrate", {}).get("total", [0])[0] if data.get("hashrate") else 0
        cpu_model = data.get("cpu", {}).get("brand", "N/A")
        total_memory = data.get("resources", {}).get("memory", {}).get("total", 0)
        free_memory = data.get("resources", {}).get("memory", {}).get("free", 0)
        load_average = data.get("resources", {}).get("load_average", [0, 0, 0])
        cores = data.get("cpu", {}).get("cores", "N/A")
        threads = data.get("cpu", {}).get("threads", "N/A")
        pool = data.get("connection", {}).get("pool", "N/A")

        total_memory = convert_bytes_to_mb(total_memory)
        free_memory = convert_bytes_to_mb(free_memory)

        worker_data = {
            "worker_id": worker_id,
            "hashrate": hashrate,
            "cpu_model": cpu_model,
            "total_memory": total_memory,
            "free_memory": free_memory,
            "load_average": load_average,
            "cores": cores,
            "threads": threads,
            "pool": pool
        }
        cache[worker_id] = worker_data
        return worker_data

    except (requests.RequestException, json.JSONDecodeError):
        print(f"{Fore.RED}Failed to get data from {url}. Marking worker as offline...{Style.RESET_ALL}")
        for worker_id, worker_data in cache.items():
            if url.endswith(worker_data["worker_id"]):
                return {**worker_data, "offline": True}

        return None

def display_workers(workers_data):
    headers = [
        "Hostname", 
        "Hashrate (H/s)", 
        "Modelo da CPU", 
        "Núcleos (C/T)",  
        "Memória Total (MB)", 
        "Memória Livre (MB)", 
        "Média de Carga (1m, 5m, 15m)", 
        "Pool", 
        "Status"
    ]

    table_data = []
    for worker in workers_data:
        if worker.get("offline"):
            hashrate = 0
            total_memory = 0
            free_memory = 0
            load_average = [0, 0, 0]
            status = f"{Fore.RED}Offline{Style.RESET_ALL}"
            text_style = Fore.BLACK + Style.DIM
            cores_threads = "0c/0t"
            pool = "N/A"
        else:
            hashrate = worker.get("hashrate", 0)
            total_memory = worker.get("total_memory", 0)
            free_memory = worker.get("free_memory", 0)
            load_average = worker.get("load_average", [0, 0, 0])
            status = f"{Fore.GREEN}Online{Style.RESET_ALL}"
            text_style = ""

            cores = worker.get("cores", "N/A")
            threads = worker.get("threads", "N/A")
            cores_threads = f"{cores}c/{threads}t"
            pool = worker.get("pool", "N/A")

        table_data.append([
            f"{text_style}{Fore.GREEN}{worker['worker_id']}{Style.RESET_ALL}",
            f"{text_style}{Fore.CYAN}{hashrate}{Style.RESET_ALL}",
            f"{text_style}{Fore.YELLOW}{worker['cpu_model']}{Style.RESET_ALL}",
            f"{text_style}{Fore.MAGENTA}{cores_threads}{Style.RESET_ALL}",  
            f"{text_style}{Fore.BLUE}{total_memory} MB{Style.RESET_ALL}",
            f"{text_style}{Fore.BLUE}{free_memory} MB{Style.RESET_ALL}",
            f"{text_style}{Fore.RED}{load_average}{Style.RESET_ALL}",
            f"{text_style}{Fore.YELLOW}{pool}{Style.RESET_ALL}",
            status
        ])

    print(tabulate(table_data, headers=headers, tablefmt="simpleh"))

def display_total_hashrate(total_hashrate, pools):
    print(f"\n{Fore.YELLOW}Hashrate Total: {Fore.GREEN}{total_hashrate} H/s{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Pools sendo mineradas:{Style.RESET_ALL} {', '.join(pools)}")

def main():
    urls = load_worker_urls()
    cache = load_cache()

    while True:
        workers_data = []
        total_hashrate = 0
        pools = set()

        for worker_id, worker_data in cache.items():
            workers_data.append({**worker_data, "offline": True})

        for url in urls:
            worker_data = get_worker_data(url, cache)
            if worker_data:
                for i, worker in enumerate(workers_data):
                    if worker["worker_id"] == worker_data["worker_id"]:
                        workers_data[i] = worker_data
                        break
                else:
                    workers_data.append(worker_data)

                try:
                    hashrate = worker_data["hashrate"]
                    if hashrate is not None:
                        total_hashrate += hashrate
                    if "pool" in worker_data and worker_data["pool"] != "N/A":
                        pools.add(worker_data["pool"])
                except TypeError as e:
                    print(f"{Fore.RED}Error adding hashrate for worker {worker_data.get('worker_id', 'Unknown')}: {e}{Style.RESET_ALL}")

        clear_screen()

        display_workers(workers_data)

        display_total_hashrate(total_hashrate, pools)

        save_cache(cache)

        time.sleep(1)

if __name__ == "__main__":
    main()
