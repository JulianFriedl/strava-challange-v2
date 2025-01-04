### **Let's Encrypt with Dockerized Nginx: Command Summary and Explanations**

---

### **1. Installing Certbot**
```bash
sudo apt install certbot
```
- **What it does**: Installs Certbot, a tool for obtaining and managing SSL/TLS certificates from Let's Encrypt.
- **Background**: Certbot communicates with Let's Encrypt to validate domain ownership and issues certificates.

---

### **2. Running the Initial Certificate Request**
```bash
sudo certbot certonly --webroot -w /var/lib/nginx/html -d scsport.eu -d www.scsport.eu
```
- **What it does**: Obtains an SSL/TLS certificate by proving domain ownership using the **HTTP-01 challenge**.
- **Background**: Certbot creates a token file in the specified webroot directory, and Let's Encrypt validates it by making a request to `http://scsport.eu/.well-known/acme-challenge/<token>`.

---

### **3. Mounting ACME Challenge Directory in Docker**
In `docker-compose.yml`:
```yaml
  nginx:
    volumes:
      - /var/lib/nginx/html:/var/lib/nginx/html:ro
```
- **What it does**: Maps the host directory `/var/lib/nginx/html` into the Nginx container so it can serve the challenge files.
- **Background**: Docker containers have isolated filesystems. The mount makes the ACME challenge files accessible to Nginx.

---

### **4. Testing Renewal with a Dry Run**
```bash
sudo certbot renew --dry-run --webroot -w /var/lib/nginx/html
```
- **What it does**: Simulates the certificate renewal process without making actual changes.
- **Background**: Let's Encrypt validates the domain ownership again using the HTTP-01 challenge. If successful, a new certificate would replace the old one.

---


### **5. Automating Renewal with Cron**
Edit the root crontab:
```bash
sudo crontab -e
```
Add:
```bash
0 0 * * * certbot renew --quiet --webroot -w /var/lib/nginx/html && docker exec nginx nginx -s reload
```
- **What it does**: Automates certificate renewal every day at midnight and reloads Nginx to apply new certificates.
- **Background**: Certbot checks if the certificate is due for renewal (30 days before expiry). If renewed, Nginx reloads to use the new certificate.

---

### **6. Checking Certbot Logs**
```bash
sudo less /var/log/letsencrypt/letsencrypt.log
```
- **What it does**: Views Certbot logs to troubleshoot issues during certificate issuance or renewal.
- **Background**: Logs show detailed errors and steps taken during Certbot operations.

