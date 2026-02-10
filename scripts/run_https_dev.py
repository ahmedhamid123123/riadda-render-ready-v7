#!/usr/bin/env python3
"""Generate a local self-signed cert (SANs for localhost + 127.0.0.1 + ::1)
and run Django's `runserver_plus` with the certificate.

Usage: from project root
    python scripts/run_https_dev.py

This uses the `cryptography` library to create a cert and key, writes
`cert.pem`, `key.key` and `cert_combined.pem` in the project root, then
executes `manage.py runserver_plus` with `config.settings.dev`.
"""
import os
import sys
import subprocess
from datetime import datetime, timedelta

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509 import DNSName, IPAddress
    from ipaddress import IPv4Address, IPv6Address
except Exception as exc:
    print("Missing Python dependency for certificate generation:", exc)
    print("Install requirements: pip install cryptography pyOpenSSL django-extensions Werkzeug")
    sys.exit(1)


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)

MANAGE = os.path.join(ROOT, "manage.py")
if not os.path.exists(MANAGE):
    print("Could not find manage.py in project root. Run this script from the project root.")
    sys.exit(2)


def generate_cert(cert_path, key_path, combined_path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])

    san = x509.SubjectAlternativeName([
        DNSName("localhost"),
        IPAddress(IPv4Address("127.0.0.1")),
        IPAddress(IPv6Address("::1")),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(san, critical=False)
        .sign(key, hashes.SHA256())
    )

    # Write files
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    # Combined PEM (certificate then key)
    with open(combined_path, "wb") as out:
        out.write(cert.public_bytes(serialization.Encoding.PEM))
        out.write(b"\n")
        out.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


def main():
    cert_path = os.path.join(ROOT, "cert.pem")
    key_path = os.path.join(ROOT, "key.key")
    combined_path = os.path.join(ROOT, "cert_combined.pem")

    print("Generating self-signed certificate...")
    generate_cert(cert_path, key_path, combined_path)
    print(f"Wrote {cert_path}, {key_path}, {combined_path}")

    # Run runserver_plus with the generated certificate
    cmd = [sys.executable, "manage.py", "runserver_plus", "127.0.0.1:8000", "--cert-file", combined_path, "--settings=config.settings.dev"]
    print("Starting Django dev server with HTTPS:")
    print(" ", " ".join(cmd))
    os.execv(sys.executable, cmd)


if __name__ == "__main__":
    main()
