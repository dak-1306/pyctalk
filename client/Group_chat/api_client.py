class APIClient:
    """Wrapper để gửi request tới server"""
    def __init__(self, connection):
        self.connection = connection

    def send_request(self, action, data):
        try:
            return self.connection.send_json({"action": action, "data": data})
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
