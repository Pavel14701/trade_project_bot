from cryptography.fernet import Fernet

# Храните этот ключ в .env
ENCRYPTION_KEY = "ВАШ_КЛЮЧ_ИЗ_.ENV"
cipher = Fernet(ENCRYPTION_KEY)
