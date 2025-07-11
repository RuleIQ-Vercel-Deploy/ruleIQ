"""
Generates a Fernet key for encrypting and decrypting sensitive data.

Run this script once and store the output securely as an environment variable
(e.g., FERNET_KEY in your .env file).

Example:
  python scripts/generate_fernet_key.py
"""

from cryptography.fernet import Fernet


def generate_key():
    """Generates a new Fernet key."""
    key = Fernet.generate_key()
    print("Generated Fernet Key (store this securely!):")
    print(key.decode())  # Print as string for easy copy-pasting


if __name__ == "__main__":
    generate_key()
