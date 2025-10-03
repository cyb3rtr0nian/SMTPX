# SMTPX – Ultimate SMTP User Enumeration Tool
SMTPX is a fast, accurate, and stealthy SMTP user enumeration tool. Outperforms all traditional SMTP enumeration scripts.

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

> ⚡ **SMTPX beats standard tools like `smtp-user-enum`, both in speed and accuracy.**


## Installation

```bash
git clone https://github.com/yourusername/SMTPX.git
cd SMTPX
```

#### Requirements
- Python 3.8+
- Rich
```

#### Usage:
```bash
python3 smtpx.py -t <SMTP_SERVER> [options]
```

#### Options:
```bash
-t, --target	Target SMTP server (required)
-U, --userlist	Path to a file containing usernames
-u, --user	Single username to test
-M, --method	Enumeration method: VRFY (default), EXPN, RCPT
-f, --from-addr	MAIL FROM address (used in RCPT mode, default: user@example.com)
-D, --domain	Domain to append to usernames
-p, --port	SMTP port (default: 25)
-T, --threads	Number of threads (default: 5)
-w, --wait	Timeout in seconds (default: 10)
-v, --verbose	Verbose output
-d, --debug	Debug output for troubleshooting
-h, --help	Show help message
```

### Examples
#### Single user check
```bash
python3 smtpx.py -t smtp.example.com -u alice -M VRFY
```

#### Bulk userlist
```bash
python3 smtpx.py -t smtp.example.com -U userlist.txt -M RCPT -f attacker@example.com -D example.com -T 10
```

#### Verbose + Debug mode
```bash
python3 smtpx.py -t smtp.example.com -U userlist.txt -v -d
```
