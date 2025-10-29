
https://github.com/cyb3rtr0nian/SMTPX/blob/main/screenshots/smptx.png

# SMTPX – Ultimate SMTP User Enumeration Tool
A high-performance, multi-threaded SMTP user enumeration tool with real-time visualization, designed for penetration testers and security professionals to efficiently identify valid users on SMTP servers.

---

## Features

- ✅ Multi-method enumeration: `VRFY`, `EXPN`, `RCPT TO`
- ✅ Supports single user or bulk user lists
- ✅ Optional domain appending for emails
- ✅ Automatic retries for failed connections
- ✅ Multithreaded for speed and efficiency
- ✅ Live Rich console UI with progress bars
- ✅ Verbose and debug modes for maximum insight
- ✅ Accurately detects valid users even with ambiguous SMTP responses
- ✅ Handles timeouts, connection errors, and tricky server responses

> ⚡ **SMTPX beats standard tools like smtp-user-enum, both in speed and accuracy.**

## Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/SMTPX.git
cd SMTPX
chmod +x smtpx.py
```

## Requirements
For SMTPX, the only external dependency the tool uses is `Rich` for the console output.
```bash
- Python 3.8+
- Rich
```

## Usage
```bash
./smtpx.py -t <SMTP_SERVER> [options]
```

### Options
```bash
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
```

### Examples
#### Single user check + Debug mode
```bash
./smptx.py -t 10.129.239.107 -u robin -d
```
![1](https://github.com/cyb3rtr0nian/SMTPX/blob/main/screenshots/single-user.png?raw=true)

#### Bulk userlist + Verbose mode
```bash
./smptx.py -t 10.129.239.107 -U userlist.txt -T 50 -M VRFY -v 
```

##### Starting the attack:
![2](https://github.com/cyb3rtr0nian/SMTPX/blob/main/screenshots/wordlist-1.png?raw=true)
##### Results:
![4](https://github.com/cyb3rtr0nian/SMTPX/blob/main/screenshots/wordlist-3.png?raw=true)

#### Verbose + Debug modes
```bash
./smptx.py -t 10.129.239.107 -U userlist.txt -T 50 -M VRFY -v -d
```
![5](https://github.com/cyb3rtr0nian/SMTPX/blob/main/screenshots/wordlist+debug.png?raw=true)
![6](https://github.com/cyb3rtr0nian/SMTPX/blob/main/screenshots/debug%20output.png?raw=true)

#### Verify with **Netcat**
![7](https://github.com/cyb3rtr0nian/SMTPX/blob/main/screenshots/verify.png?raw=true)

#### Other usage example
##### Advanced Techniques
```bash
# RCPT method with custom domain and MAIL FROM
./smptx.py -U users.txt -t 10.10.10.10 -M RCPT -D example.com -f attacker@evil.com

# EXPN method with debugging enabled
./smptx.py -U users.txt -t 10.10.10.10 -M EXPN -d

# Email enumeration with domain
./smptx.py -U usernames.txt -t 10.10.10.10 -D target-company.com -v
```
##### Troubleshooting & Debugging
```bash
# Debug connection issues
./smptx.py -u testuser -t 10.10.10.10 -d -w 20

# Test all three methods
./smptx.py -u testuser -t 10.10.10.10 -M VRFY
./smptx.py -u testuser -t 10.10.10.10 -M EXPN
./smptx.py -u testuser -t 10.10.10.10 -M RCPT
```
