# stress_test.py
import os
import time
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from file_client_cli import remote_get, remote_upload, remote_list
import pandas as pd
from datetime import datetime

# Konfigurasi
OPERATIONS = ['download', 'upload']
FILE_SIZES = {
    10 * 1024 * 1024: '10mb.mp4',
    50 * 1024 * 1024: '50mb.txt',
    100 * 1024 * 1024: '100mb.pdf'
}
CLIENT_WORKERS = [1, 5, 50]
SERVER_WORKERS = [1, 5, 50]
POOL_TYPES = ['thread', 'process']

# Fungsi untuk mencatat ke backlog.txt
def log_to_backlog(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('backlog.txt', 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

# Fungsi untuk menjalankan server
def run_server(max_workers, pool_type):
    log_to_backlog(f"Starting server with {max_workers} workers, pool type: {pool_type}")
    proc = subprocess.Popen(['python', 'file_server.py', str(max_workers), pool_type])
    time.sleep(2)
    return proc

# Fungsi untuk stress test
def run_stress_test(operation, file_size, client_workers, server_workers, pool_type):
    filename = FILE_SIZES[file_size]
    filepath = os.path.join('files', filename)
    
    log_to_backlog(f"Running test: operation={operation}, file={filename}, client_workers={client_workers}, server_workers={server_workers}, pool_type={pool_type}")
    
    if not os.path.exists(filepath):
        log_to_backlog(f"Error: File {filepath} tidak ditemukan")
        return {
            'Operation': operation,
            'File Size (MB)': file_size // (1024 * 1024),
            'Client Workers': client_workers,
            'Server Workers': server_workers,
            'Avg Duration (s)': 0,
            'Avg Throughput (B/s)': 0,
            'Client Success': 0,
            'Client Failure': client_workers,
            'Server Success': 0,
            'Server Failure': server_workers
        }
    
    server_proc = run_server(server_workers, pool_type)
    
    # Test list file sebelum operasi utama
    log_to_backlog("Testing remote_list before operation")
    list_success = remote_list()
    log_to_backlog(f"remote_list result: {'Success' if list_success else 'Failed'}")
    
    results = []
    success_count = 0
    failure_count = 0
    total_duration = 0
    total_bytes = 0
    
    def worker():
        nonlocal success_count, failure_count, total_duration, total_bytes
        try:
            if operation == 'download':
                log_to_backlog(f"Worker starting download for {filename}")
                success, duration, throughput = remote_get(filename)
            else:
                log_to_backlog(f"Worker starting upload for {filename}")
                success, duration, throughput = remote_upload(filename)
            if success:
                success_count += 1
                total_duration += duration
                total_bytes += throughput * duration
                log_to_backlog(f"Worker completed: Success, Duration={duration:.2f}s, Throughput={throughput:.2f} B/s")
            else:
                failure_count += 1
                log_to_backlog("Worker completed: Failed")
        except Exception as e:
            failure_count += 1
            log_to_backlog(f"Worker error: {str(e)}")
    
    try:
        if pool_type == 'thread':
            with ThreadPoolExecutor(max_workers=client_workers) as executor:
                futures = [executor.submit(worker) for _ in range(client_workers)]
                for future in futures:
                    future.result()
        else:
            with ProcessPoolExecutor(max_workers=client_workers) as executor:
                futures = [executor.submit(worker) for _ in range(client_workers)]
                for future in futures:
                    future.result()
        
        avg_duration = total_duration / success_count if success_count > 0 else 0
        avg_throughput = total_bytes / total_duration if total_duration > 0 else 0
        
        server_success = server_workers
        server_failure = 0
        
        result = {
            'Operation': operation,
            'File Size (MB)': file_size // (1024 * 1024),
            'Client Workers': client_workers,
            'Server Workers': server_workers,
            'Avg Duration (s)': round(avg_duration, 2),
            'Avg Throughput (B/s)': round(avg_throughput, 2),
            'Client Success': success_count,
            'Client Failure': failure_count,
            'Server Success': server_success,
            'Server Failure': server_failure
        }
        log_to_backlog(f"Test result: {result}")
        return result
    except Exception as e:
        log_to_backlog(f"Test error: {str(e)}")
        return {
            'Operation': operation,
            'File Size (MB)': file_size // (1024 * 1024),
            'Client Workers': client_workers,
            'Server Workers': server_workers,
            'Avg Duration (s)': 0,
            'Avg Throughput (B/s)': 0,
            'Client Success': 0,
            'Client Failure': client_workers,
            'Server Success': 0,
            'Server Failure': server_workers
        }
    finally:
        server_proc.terminate()
        log_to_backlog("Server terminated")

def main():
    if os.path.exists('backlog.txt'):
        os.remove('backlog.txt')
    log_to_backlog("Starting stress test")
    
    results = []
    test_number = 1
    for pool_type in POOL_TYPES:
        for operation in OPERATIONS:
            for file_size in FILE_SIZES:
                for client_workers in CLIENT_WORKERS:
                    for server_workers in SERVER_WORKERS:
                        logging.warning(f"Running test {test_number}: {operation}, {file_size} bytes, {client_workers} clients, {server_workers} servers, {pool_type}")
                        result = run_stress_test(operation, file_size, client_workers, server_workers, pool_type)
                        result['Test Number'] = test_number
                        result['Pool Type'] = pool_type
                        results.append(result)
                        test_number += 1
    
    df = pd.DataFrame(results)
    df = df[['Test Number', 'Pool Type', 'Operation', 'File Size (MB)', 'Client Workers', 'Server Workers',
             'Avg Duration (s)', 'Avg Throughput (B/s)', 'Client Success', 'Client Failure',
             'Server Success', 'Server Failure']]
    df.to_csv('stress_test_results.csv', index=False)
    print(df)
    
    log_to_backlog("Stress test completed")
    return df

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    main()