# クッキーを暗号化して安全に保管するサンプルコード

# 暗号化するためのパスワードを設定する
cookie_password = "your_cookie_password"

email = "your_email"
password = "your_password"

import yaylib

api = yaylib.Client(cookie_password=cookie_password)

api.login(email, password)

api.create_post("Hello with yaylib!")
