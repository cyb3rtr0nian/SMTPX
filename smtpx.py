#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
SMTPX – Ultimate SMTP User Enumeration Tool
--------------------------------------------

SMTPX is a next-generation SMTP user enumeration tool designed to outperform
traditional tools like `smtp-user-enum` by a wide margin. It is optimized for
speed, accuracy, and stealth.

Features:
- Multi-method enumeration: VRFY, EXPN, RCPT TO
- Supports single users or bulk user lists
- Optional domain appending for emails
- Automatic retries for failed connections
- Multithreaded enumeration for efficiency
- Live dynamic console UI using Rich
- Verbose and debug modes for troubleshooting
- Accurate detection of valid users even with ambiguous SMTP responses

Author: [Your Name or GitHub handle]
License: MIT

Usage:
------
Single user check:
    ./smtpx.py -t smtp.example.com -u alice -M VRFY

Bulk userlist:
    ./smtpx.py -t smtp.example.com -U examples/userlist.txt -M RCPT -f attacker@example.com -D example.com -T 10

Verbose + Debug mode:
    ./smtpx.py -t smtp.example.com -U examples/userlist.txt -v -d

Options:
--------
-t, --target      Target SMTP server (required)
-U, --userlist    Path to a file containing usernames
-u, --user        Single username to test
-M, --method      Enumeration method: VRFY (default), EXPN, RCPT
-f, --from-addr   MAIL FROM address (used in RCPT mode, default: user@example.com)
-D, --domain      Domain to append to usernames
-p, --port        SMTP port (default: 25)
-T, --threads     Number of threads (default: 5)
-w, --wait        Timeout in seconds (default: 10)
-v, --verbose     Verbose output
-d, --debug       Debug output for troubleshooting
-h, --help        Show help message

Notes:
------
- Handles timeouts, connection errors, and ambiguous server responses
- Retries failed users automatically with adjusted settings
- Requires Python 3.8+ and Rich library
"""

# ------------------- IMPORTS -------------------

import socket
import argparse
import sys
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# ------------------- GLOBALS -------------------

console = Console()
valid_users = []
current_user = ""
start_time = 0
debug_output = []
lock = threading.Lock()
failed_users = []

def check_user(smtp_server, username, method, mail_from, domain, port, timeout, debug, verbose, retry_count=0):
    """Check if a username exists on the SMTP server."""
    global valid_users, debug_output, failed_users
    
    if domain:
        test_username = f"{username}@{domain}"
    else:
        test_username = username
        
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            sock.connect((smtp_server, port))
        except socket.timeout:
            if debug:
                with lock:
                    debug_output.append(f"[DEBUG] Connection timeout for {username}")
            if retry_count < 2:
                with lock:
                    failed_users.append((username, retry_count + 1))
            return False
        except Exception as e:
            if debug:
                with lock:
                    debug_output.append(f"[DEBUG] Connection error for {username}: {str(e)}")
            if retry_count < 2:
                with lock:
                    failed_users.append((username, retry_count + 1))
            return False
            
        try:
            banner = sock.recv(1024).decode()
            if debug:
                with lock:
                    debug_output.append(f"[DEBUG] Banner: {banner.strip()}")
        except socket.timeout:
            if debug:
                with lock:
                    debug_output.append(f"[DEBUG] Banner timeout for {username}")
            sock.close()
            if retry_count < 2:
                with lock:
                    failed_users.append((username, retry_count + 1))
            return False
        
        try:
            sock.send(b"HELO test\r\n")
            helo_response = sock.recv(1024).decode()
            if debug:
                with lock:
                    debug_output.append(f"[DEBUG] HELO response: {helo_response.strip()}")
        except socket.timeout:
            if debug:
                with lock:
                    debug_output.append(f"[DEBUG] HELO timeout for {username}")
            sock.close()
            if retry_count < 2:
                with lock:
                    failed_users.append((username, retry_count + 1))
            return False
        
        if method == "VRFY":
            try:
                sock.send(f"VRFY {test_username}\r\n".encode())
                result = sock.recv(1024).decode()
                if debug:
                    with lock:
                        debug_output.append(f"[DEBUG] VRFY response: {result.strip()}")
            except socket.timeout:
                if debug:
                    with lock:
                        debug_output.append(f"[DEBUG] VRFY timeout for {username}")
                sock.close()
                if retry_count < 2:
                    with lock:
                        failed_users.append((username, retry_count + 1))
                return False
                
        elif method == "EXPN":
            try:
                sock.send(f"EXPN {test_username}\r\n".encode())
                result = sock.recv(1024).decode()
                if debug:
                    with lock:
                        debug_output.append(f"[DEBUG] EXPN response: {result.strip()}")
            except socket.timeout:
                if debug:
                    with lock:
                        debug_output.append(f"[DEBUG] EXPN timeout for {username}")
                sock.close()
                if retry_count < 2:
                    with lock:
                        failed_users.append((username, retry_count + 1))
                return False
                
        elif method == "RCPT":
            try:
                sock.send(f"MAIL FROM: {mail_from}\r\n".encode())
                mail_response = sock.recv(1024).decode()
                if debug:
                    with lock:
                        debug_output.append(f"[DEBUG] MAIL FROM response: {mail_response.strip()}")
                    
                sock.send(f"RCPT TO: {test_username}\r\n".encode())
                result = sock.recv(1024).decode()
                if debug:
                    with lock:
                        debug_output.append(f"[DEBUG] RCPT TO response: {result.strip()}")
            except socket.timeout:
                if debug:
                    with lock:
                        debug_output.append(f"[DEBUG] RCPT timeout for {username}")
                sock.close()
                if retry_count < 2:
                    with lock:
                        failed_users.append((username, retry_count + 1))
                return False
        else:
            if debug:
                with lock:
                    debug_output.append(f"[red]Unknown method: {method}[/red]")
            sock.close()
            return False

        try:
            sock.send(b"QUIT\r\n")
            sock.close()
        except:
            pass

        response_code = result[:3]
        response_text = result[3:].lower()
        
        if (response_code in ["250", "251", "252"] or 
            (response_code.startswith("2") and "ok" in response_text)):
            
            invalid_indicators = [
                "cannot", "invalid", "not found", "unknown", "unable", 
                "disabled", "denied", "reject", "fail", "error"
            ]
            
            if not any(indicator in response_text for indicator in invalid_indicators):
                valid_username = test_username if domain else username
                with lock:
                    if valid_username not in valid_users:
                        valid_users.append(valid_username)
                        if verbose:
                            debug_output.append(f"[green]Found valid user: {valid_username}[/green]")
                        return True
        
        elif response_code == "550" and "user" in response_text and "not found" not in response_text:
            if debug:
                with lock:
                    debug_output.append(f"[yellow]Ambiguous response for {username}: {result.strip()}[/yellow]")
                
    except socket.timeout:
        if debug:
            with lock:
                debug_output.append(f"[DEBUG] General timeout checking user: {username}")
        if retry_count < 2:
            with lock:
                failed_users.append((username, retry_count + 1))
    except Exception as e:
        if debug:
            with lock:
                debug_output.append(f"[DEBUG] Error checking user {username}: {str(e)}")
        if retry_count < 2:
            with lock:
                failed_users.append((username, retry_count + 1))
    return False

def main():
    global start_time, debug_output, current_user, failed_users
    
    parser = argparse.ArgumentParser(description="SMTP User Enumeration Tool", add_help=False)
    parser.add_argument("-U", "--userlist", help="Path to user list (required unless using -u)")
    parser.add_argument("-u", "--user", help="Single username to test")
    parser.add_argument("-t", "--target", required=True, help="Target SMTP server")
    parser.add_argument("-M", "--method", default="VRFY", choices=["VRFY", "EXPN", "RCPT"], 
                       help="Method to use for username guessing (default: VRFY)")
    parser.add_argument("-f", "--from-addr", default="user@example.com", 
                       help='MAIL FROM email address. Used only in "RCPT TO" mode (default: user@example.com)')
    parser.add_argument("-D", "--domain", help="Domain to append to supplied user list to make email addresses")
    parser.add_argument("-p", "--port", type=int, default=25, help="TCP port on which SMTP service runs (default: 25)")
    parser.add_argument("-d", "--debug", action="store_true", help="Debugging output")
    parser.add_argument("-w", "--wait", type=int, default=10, help="Wait a maximum of n seconds for reply (default: 10)")
    parser.add_argument("-T", "--threads", type=int, default=5, help="Number of threads to use (default: 5)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message")
    
    args = parser.parse_args()
    
    if args.help:
        parser.print_help()
        sys.exit(0)
    
    if not args.userlist and not args.user:
        console.print("[red]Error: Either -U/--userlist or -u/--user must be specified[/red]")
        parser.print_help()
        sys.exit(1)
    
    if args.userlist and args.user:
        console.print("[red]Error: Cannot specify both -U/--userlist and -u/--user[/red]")
        parser.print_help()
        sys.exit(1)
    
    if args.user:
        usernames = [args.user]
    else:
        try:
            with open(args.userlist, "r", errors="ignore") as f:
                usernames = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            console.print(f"[red]Error: File {args.userlist} not found[/red]")
            sys.exit(1)
    
    total_users = len(usernames)
    
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}", justify="center"),
        BarColumn(bar_width=None),
        TextColumn("{task.completed}/{task.total}", justify="center"),
        expand=False
    )
    task = progress.add_task("[blue]Enumerating Users[/blue]", total=total_users)

    start_time = time.time()
    
    with Live(refresh_per_second=10, console=console) as live:
        panel_content = Group(
            progress,
            f"[cyan]Current user:[/cyan] {current_user}",
            f"[green]Valid users:[/green] {', '.join(valid_users)}" if valid_users else "[green]Valid users: None[/green]"
        )
        live.update(Panel(panel_content, title="[bold cyan]SMTP User Enumeration[/bold cyan]", padding=(0, 2), expand=False))
        
        if args.verbose:
            console.print(f"[cyan]Starting enumeration with method {args.method}[/cyan]")
            if args.domain:
                console.print(f"[cyan]Using domain: {args.domain}[/cyan]")
            console.print(f"[cyan]Target: {args.target}:{args.port}[/cyan]")
            console.print(f"[cyan]Testing {total_users} users with {args.threads} threads[/cyan]")
        
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_user = {
                executor.submit(
                    check_user, 
                    args.target, 
                    username, 
                    args.method, 
                    args.from_addr, 
                    args.domain, 
                    args.port, 
                    args.wait, 
                    args.debug, 
                    args.verbose,
                    0
                ): username for username in usernames
            }
            
            for future in as_completed(future_to_user):
                username = future_to_user[future]
                try:
                    future.result()
                except Exception as e:
                    if args.debug:
                        with lock:
                            debug_output.append(f"[DEBUG] Exception for {username}: {str(e)}")
                
                progress.update(task, advance=1)
                
                panel_content = Group(
                    progress,
                    f"[cyan]Current user:[/cyan] {username}",
                    f"[green]Valid users:[/green] {', '.join(valid_users)}" if valid_users else "[green]Valid users: None[/green]"
                )
                
                if debug_output and args.debug:
                    debug_group = Group(*[f"[yellow]{line}[/yellow]" for line in debug_output[-3:]])
                    panel_content = Group(panel_content, debug_group)
                
                live.update(Panel(panel_content, title="[bold cyan]SMTP User Enumeration[/bold cyan]", padding=(0, 2), expand=False))
        
        if failed_users:
            retry_users = [user for user, count in failed_users]
            retry_count = len(retry_users)
            
            if args.verbose:
                console.print(f"[yellow]Retrying {retry_count} failed users with slower settings...[/yellow]")
            
            progress.update(task, total=total_users + retry_count)
            
            retry_threads = max(1, args.threads // 2)
            retry_timeout = args.wait * 2
            
            with ThreadPoolExecutor(max_workers=retry_threads) as executor:
                future_to_user = {
                    executor.submit(
                        check_user, 
                        args.target, 
                        username, 
                        args.method, 
                        args.from_addr, 
                        args.domain, 
                        args.port, 
                        retry_timeout,
                        args.debug, 
                        args.verbose,
                        1
                    ): username for username in retry_users
                }
                
                for future in as_completed(future_to_user):
                    username = future_to_user[future]
                    try:
                        future.result()
                    except Exception as e:
                        if args.debug:
                            with lock:
                                debug_output.append(f"[DEBUG] Exception during retry for {username}: {str(e)}")
                    
                    progress.update(task, advance=1)
                    
                    panel_content = Group(
                        progress,
                        f"[cyan]Current user:[/cyan] {username} (retry)",
                        f"[green]Valid users:[/green] {', '.join(valid_users)}" if valid_users else "[green]Valid users: None[/green]"
                    )
                    
                    if debug_output and args.debug:
                        debug_group = Group(*[f"[yellow]{line}[/yellow]" for line in debug_output[-3:]])
                        panel_content = Group(panel_content, debug_group)
                    
                    live.update(Panel(panel_content, title="[bold cyan]SMTP User Enumeration[/bold cyan]", padding=(0, 2), expand=False))
    
    end_time = time.time()
    time_taken = end_time - start_time

    console.print(f"\n[bold cyan]Enumeration Complete (Time taken: {time_taken:.2f} seconds)[/bold cyan]")
    
    if args.debug and debug_output:
        console.print("\n[bold yellow]Debug Output:[/bold yellow]")
        for line in debug_output:
            console.print(line)
    
    if failed_users:
        console.print(f"[yellow]{len(failed_users)} users failed after retries[/yellow]")
    
    if valid_users:
        console.print(f"[bold yellow]Valid users found:[/bold yellow] {', '.join(valid_users)}")
    else:
        console.print("[bold yellow]No valid users found.[/bold yellow]")

if __name__ == "__main__":
    main()
