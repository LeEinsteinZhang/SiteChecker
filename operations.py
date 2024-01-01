## =======================================================
## Program: Site Checker (operations)- WCMS
## Author: Le Zhang (20916452)
## Email: l652zhan@uwaterloo.ca
## Update Time: Nov. 15 2023
## Company: University of Waterloo
## Faculty: MECHANICAL AND MECHATRONICS ENGINEERING
## =======================================================


import aiohttp
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
import threading
from urllib.parse import urljoin
from file_io import *


def check_url(session, url):
    """
    check_url(session, url) returns the URL if checking it fails, otherwise None.

    Returns:
        - url (str) if any error occurs or the status code is not 200.
        - None if the URL is successfully accessed and the status code is 200.

    check_url: Session Str -> anyof(Str, None)

    Requires:
        - session is an instance of requests.Session and is used to send the HTTP request.
        - url is a string representing a valid URL to be checked.

    Example:
        faulty_url = check_url(session, 'http://example.com')
        if faulty_url:
            print(f"The URL {faulty_url} is not accessible or caused an error.")
    """
    try:
        response = session.head(url, allow_redirects=True, timeout=5)
        response_code = response.status_code
        if response_code == 404:
            return url
    except requests.exceptions.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return url
    return None


def acc_check(base_url):
    """
    acc_check(base_url) returns a tuple of lists containing broken URLs and URLs causing
    accessibility issues from the page located at base_url.

    Returns:
        - broken_urls ((listof str)): A list of strings, each representing a URL which is broken.
        - acc_problem ((listof str)): A list of strings, each representing a URL which causes
          accessibility issues.

    acc_check: Str -> ((listof str), (listof str))

    Requires:
        - base_url is a string representing a valid URL of the base page where
          the checking will be performed.

        Note: The function internally uses `exclusion_list` and `social_media_domains`
              which should be available in the scope.

    Example:
        broken_urls, acc_problems = acc_check('http://example.com')
        if broken_urls:
            print(f"Broken URLs: {broken_urls}")
        if acc_problems:
            print(f"URLs causing accessibility issues: {acc_problems}")
    """
    broken_urls = []
    acc_problem = []
    social_media_domains = load_config('social_media_domains.json')
    exclusion_list = load_config('exclusion_list.json')
    try:
        session = requests.Session()
        response = session.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for img in soup.find_all('img'):
            alt_text = img.get('alt')
            if alt_text is None or not alt_text.strip():
                img_url = img.get('src')
                img_url = urljoin(base_url, img_url)
                if img_url not in exclusion_list:
                    acc_problem.append(img_url)
        urls_to_check = []
        for a in soup.find_all('a', href=True):
            url = a.get('href')
            text = a.get_text()
            if url.startswith('tel') or url.startswith('mailto') or any(
                    domain in url for domain in social_media_domains) or url.startswith('#'):
                continue
            if not text.strip():
                url = urljoin(base_url, url)
                if "forward?path=node" in url:
                    continue
                if url not in exclusion_list:
                    acc_problem.append(url)
            url = urljoin(base_url, url)
            urls_to_check.append(url)
        with ThreadPoolExecutor(max_workers=16) as executor:
            results = executor.map(lambda url: check_url(session, url), urls_to_check)
            broken_urls = [result for result in results if result]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URLs from {base_url}: {e}")
    return broken_urls, acc_problem


def range_check(app_instance, site, start_node, end_node, mode=0, output_name='', speed=0):
    if speed == 1:
        return range_check_fast(app_instance, site, start_node, end_node, mode, output_name)
    else:
        return range_check_slow(app_instance, site, start_node, end_node, mode, output_name)
    

def range_check_slow(app_instance, site, start_node, end_node, mode=0, output_name=''):
    """
    range_check(site, start_node, end_node[, mode][, output_name]) iterates through a range
        of nodes on a website, checking for broken URLs and accessibility problems on each one,
        and optionally writes issues to a file.

    range_check: Str Int Int Int Str -> None

    Requires:
        - site is a non-empty string, representing the base URL of the website to check.
        - start_node and end_node are integers, representing the range of node numbers to check.
        - 0 <= mode <= 3, where:
            0: print all problems to console (default)
            1: write only accessibility problems to file
            2: write only broken URLs to file
            3: write all problems to file
        - output_name is an optional string to prefix the result filename with.

    Effects:
        - Performs HTTP requests to the specified site.
        - Writes to a file if mode is 1, 2, or 3, and issues are found.

    Examples:
        range_check("http://example.com/", 1, 100, 1, "example_")
    """
    app_instance.output_text.delete('1.0', tk.END)
    last_node = get_last_node(app_instance)
    app_instance.progressbar['maximum'] = end_node - start_node
    if last_node is not None:
        a = last_node + 1
    else:
        a = start_node
    site_url = site
    for i in range(a, end_node):
        print(f"Working on node {i}")
        base_url = site_url + f"node/{i}/"
        response = requests.head(base_url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            broken_urls, acc_problem = acc_check(base_url)
            if mode == 1:
                if broken_urls == [] and acc_problem != []:
                    write_to_file(output_name, base_url, acc_problem, broken_urls, 1, 0)
            elif mode == 2:
                if broken_urls != [] and acc_problem == []:
                    write_to_file(output_name, base_url, acc_problem, broken_urls, 0, 1)
            elif mode == 3:
                if broken_urls != [] or acc_problem != []:
                    write_to_file(output_name, base_url, acc_problem, broken_urls, 1, 1)
            else:
                print("Accessibility Problems:", acc_problem)
                print("Broken URLs:", broken_urls)
        app_instance.progress_var.set(i - start_node + 1)
        app_instance.update_progress_label()
        app_instance.progressbar.update_idletasks()
        set_last_node(app_instance, i)
    app_instance.update_progress_label(1)
    remove_progress()


def range_check_fast(app_instance, site, start_node, end_node, mode=0, output_name='', num_threads=10):
    app_instance.output_text.delete('1.0', tk.END)
    last_node = get_last_node(app_instance)
    app_instance.progressbar['maximum'] = end_node - start_node
    if last_node:
        finish = last_node
    else:
        finish = 0
    bits_map = load_bin(end_node + 1)
    def worker(start, end):
        for i in range(start, end):
            if not bits_map[i]:
                process_node(i)

    def process_node(node):
        nonlocal finish
        print(f"Working on node {node}\n")
        base_url = site + f"node/{node}/"
        response = requests.head(base_url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            broken_urls, acc_problem = acc_check(base_url)
            handle_results(broken_urls, acc_problem, base_url)
        bits_map[node] = 1
        save_bin(bits_map)
        finish += 1
        set_last_node(app_instance, finish)
        app_instance.progress_var.set(finish)
        app_instance.update_progress_label()
        app_instance.progressbar.update_idletasks()

    def handle_results(broken_urls, acc_problem, base_url):
        if mode == 1:
            if broken_urls == [] and acc_problem != []:
                write_to_file(output_name, base_url, acc_problem, broken_urls, 1, 0)
        elif mode == 2:
            if broken_urls != [] and acc_problem == []:
                write_to_file(output_name, base_url, acc_problem, broken_urls, 0, 1)
        elif mode == 3:
            if broken_urls != [] or acc_problem != []:
                write_to_file(output_name, base_url, acc_problem, broken_urls, 1, 1)
        else:
            print("Accessibility Problems:", acc_problem)
            print("Broken URLs:", broken_urls)

    # Divide the range into segments for each thread
    total_nodes = end_node - start_node
    nodes_per_thread = total_nodes // num_threads
    threads = []

    for i in range(num_threads):
        start = start_node + i * nodes_per_thread
        end = start_node + (i + 1) * nodes_per_thread if i != num_threads - 1 else end_node
        thread = threading.Thread(target=worker, args=(start, end))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print(f"finish {sum(bits_map)}")
    app_instance.update_progress_label(1)
    if mode != 0:
        parse_and_sort(output_name)
    remove_progress()


def node_check(app_instance, site, n, mode=0, output_name=''):
    """
    node_check(site, n[, mode][, output_name]) checks a single node on a website for broken URLs
        and accessibility problems and optionally writes issues to a file by utilizing range_check.

    node_check: Str Int [Int] [Str] -> None

     Requires:
        - site is a non-empty string, representing the base URL of the website to check.
        - start_node and end_node are integers, representing the range of node numbers to check.
        - 0 <= mode <= 3, where:
            0: print all problems to console (default)
            1: write only accessibility problems to file
            2: write only broken URLs to file
            3: write all problems to file
        - output_name is an optional string to prefix the result filename with.

    Effects:
        - Performs HTTP requests to the specified site.
        - Writes to a file if mode is 1, 2, or 3, and issues are found.

    Examples:
        range_check("http://example.com/", 1, 100, 1, "example_")
    """
    b = n + 1
    return range_check(app_instance, site, n, b, mode, output_name)


def site_check(site):
    """
    site_check(site) returns True if the website is reachable and False otherwise.

    site_check: Str -> Bool

    Requires:
        - site is a non-empty string, representing the base URL of the website to check.

    Effects:
        - Performs an HTTP HEAD request to "<site>node/1".

    Example:
        if site_check("http://example.com/"):
            print("Site is reachable.")
        else:
            print("Site is not reachable.")
    """
    response = requests.head(site + f"node/1", allow_redirects=True, timeout=5)
    return response.status_code == 200


def site_process(url):
    """
    site_process(url) validates and processes the URL, and derives an output_name
        from the URL's components.

    site_process: Str -> (Bool, Str, Str)

    Requires:
        - url is a non-empty string, representing a website URL.

    Returns:
        - A tuple containing:
            - A boolean indicating the reachability status of the site.
            - A string of the processed URL.
            - A string to be used as output_name in the file outputs.

    Examples:
        status, processed_url, output_name = site_process("http://example.com/")
    """
    name = url.split('/')
    if name[-1] == '':
        output_name = name[-2].replace("-", "_") + '_'
    else:
        url = url + '/'
        output_name = name[-1].replace("-", "_") + '_'
    status = site_check(url)
    return status, url, output_name
