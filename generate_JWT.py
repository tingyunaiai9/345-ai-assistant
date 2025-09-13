import jwt
import time
from datetime import datetime, timedelta

# 从文件加载私钥，需要确保私钥文件路径正确
# 私钥格式通常为 PEM
with open(r'D:\Ai assistant\ed25519-private.pem', 'rb') as f:
    private_key = f.read()

# 您的 JWT 参数
header = {
    "alg": "EdDSA",
    "kid": "TDPPQJ5HEW"  # 替换成您的凭据ID
}

payload = {
    "sub": "3GDYB9P2M8",  # 替换成您的项目ID
    "iat": int(time.time() - 10),  # 当前时间减去10秒
    "exp": int(time.time() + 86380)  # 当前时间加上1小时（3600秒）
}

# 使用 Ed25519 算法生成 JWT token
# 注意：PyJWT 库会自动处理 Base64URL 编码和签名
# 指定算法时，需要使用 'EdDSA' 字符串
# jwt.encode 会返回一个 byte 字符串，需要解码为普通字符串
encoded_jwt = jwt.encode(
    payload=payload,
    key=private_key,
    algorithm='EdDSA',
    headers=header
)

print("生成的 JWT Token:")
print(encoded_jwt)