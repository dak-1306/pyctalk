from Request.handle_request_client import PycTalkClient

class ClientApp:
    def __init__(self):
        self.client = PycTalkClient()

    def run(self):
        print("=== PycTalk Client ===")
        while True:
            print("\n1. Đăng ký\n2. Đăng nhập\n0. Thoát")
            choice = input("Chọn chức năng: ")

            if choice == "1":
                self.handle_register()
            elif choice == "2":
                self.handle_login()
            elif choice == "0":
                print("👋 Thoát chương trình.")
                break
            else:
                print("⚠️ Lựa chọn không hợp lệ.")

    def handle_register(self):
        username = input("Tên người dùng: ")
        if not username:
            print("⚠️ Tên người dùng không được để trống.")
            self.handle_register()
        password = input("Mật khẩu: ")
        if not password:
            print("⚠️ Mật khẩu không được để trống.")
            self.handle_register()
        email = input("Email: ")
        if not email:
            print("⚠️ Email không được để trống.")
            self.handle_register()
        
        response = self.client.register(username, password, email)
        print("📥 Phản hồi từ server:", response)

    def handle_login(self):
        username = input("Tên người dùng: ")
        if not username:
            print("⚠️ Tên người dùng không được để trống.")
            self.handle_login()
        password = input("Mật khẩu: ")
        if not password:
            print("⚠️ Mật khẩu không được để trống.")
            self.handle_login()
        response = self.client.login(username, password)
        print("📥 Phản hồi từ server:", response)


if __name__ == "__main__":
    app = ClientApp()
    app.run()