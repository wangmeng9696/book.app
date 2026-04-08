import json
import hashlib
import os
import time
from datetime import datetime

# ================== 数据模型 ==================
class User:
    def __init__(self, username, password_hash, role="buyer", email=""):
        self.username = username
        self.password_hash = password_hash
        self.role = role          # "buyer", "seller", "both"
        self.email = email

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "email": self.email
        }

    @staticmethod
    def from_dict(data):
        return User(data["username"], data["password_hash"], data["role"], data["email"])

class Book:
    def __init__(self, book_id, title, author, isbn, price, description, seller, status="available"):
        self.id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.price = price
        self.description = description
        self.seller = seller
        self.status = status       # "available", "sold"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "price": self.price,
            "description": self.description,
            "seller": self.seller,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        return Book(data["id"], data["title"], data["author"], data["isbn"],
                    data["price"], data["description"], data["seller"], data["status"])

class Order:
    def __init__(self, order_id, buyer, book_id, order_time, status="completed"):
        self.id = order_id
        self.buyer = buyer
        self.book_id = book_id
        self.order_time = order_time
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "buyer": self.buyer,
            "book_id": self.book_id,
            "order_time": self.order_time,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        return Order(data["id"], data["buyer"], data["book_id"],
                     data["order_time"], data["status"])

# ================== 数据管理 ==================
class DataManager:
    def __init__(self, user_file="users.json", book_file="books.json", order_file="orders.json"):
        self.user_file = user_file
        self.book_file = book_file
        self.order_file = order_file
        self._init_files()

    def _init_files(self):
        for file in [self.user_file, self.book_file, self.order_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump([], f)

    def _load(self, filename):
        with open(filename, "r") as f:
            return json.load(f)

    def _save(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    # 用户操作
    def get_all_users(self):
        data = self._load(self.user_file)
        return [User.from_dict(u) for u in data]

    def save_user(self, user):
        users = self.get_all_users()
        users.append(user)
        self._save(self.user_file, [u.to_dict() for u in users])

    def update_users(self, users):
        self._save(self.user_file, [u.to_dict() for u in users])

    # 教材操作
    def get_all_books(self):
        data = self._load(self.book_file)
        return [Book.from_dict(b) for b in data]

    def save_book(self, book):
        books = self.get_all_books()
        books.append(book)
        self._save(self.book_file, [b.to_dict() for b in books])

    def update_books(self, books):
        self._save(self.book_file, [b.to_dict() for b in books])

    # 订单操作
    def get_all_orders(self):
        data = self._load(self.order_file)
        return [Order.from_dict(o) for o in data]

    def save_order(self, order):
        orders = self.get_all_orders()
        orders.append(order)
        self._save(self.order_file, [o.to_dict() for o in orders])

    def update_orders(self, orders):
        self._save(self.order_file, [o.to_dict() for o in orders])

# ================== 业务逻辑 ==================
class Marketplace:
    def __init__(self):
        self.dm = DataManager()
        self.current_user = None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # ---------- 用户相关 ----------
    def register(self, username, password, role, email=""):
        users = self.dm.get_all_users()
        if any(u.username == username for u in users):
            print("用户名已存在！")
            return False
        user = User(username, self.hash_password(password), role, email)
        self.dm.save_user(user)
        print("注册成功！")
        return True

    def login(self, username, password):
        users = self.dm.get_all_users()
        for user in users:
            if user.username == username and user.password_hash == self.hash_password(password):
                self.current_user = user
                print(f"欢迎回来，{username}！")
                return True
        print("用户名或密码错误。")
        return False

    def logout(self):
        self.current_user = None
        print("已登出。")

    # ---------- 教材相关 ----------
    def publish_book(self, title, author, isbn, price, description):
        if not self.current_user:
            print("请先登录。")
            return
        books = self.dm.get_all_books()
        new_id = max([b.id for b in books], default=0) + 1
        book = Book(new_id, title, author, isbn, price, description, self.current_user.username)
        self.dm.save_book(book)
        print(f"教材《{title}》发布成功，ID：{new_id}")

    def browse_books(self, keyword=None, min_price=None, max_price=None):
        books = self.dm.get_all_books()
        available = [b for b in books if b.status == "available"]
        if not available:
            print("暂无在售教材。")
            return []

        # 筛选
        filtered = available
        if keyword:
            filtered = [b for b in filtered if keyword.lower() in b.title.lower() or keyword.lower() in b.isbn]
        if min_price is not None:
            filtered = [b for b in filtered if b.price >= min_price]
        if max_price is not None:
            filtered = [b for b in filtered if b.price <= max_price]

        # 显示
        for b in filtered:
            print(f"ID:{b.id} | {b.title} | 作者:{b.author} | ISBN:{b.isbn} | 价格:¥{b.price} | 卖家:{b.seller}")
            print(f"  描述: {b.description[:50]}...")
        return filtered

    def buy_book(self, book_id):
        if not self.current_user:
            print("请先登录。")
            return
        books = self.dm.get_all_books()
        book = next((b for b in books if b.id == book_id and b.status == "available"), None)
        if not book:
            print("教材不存在或已售出。")
            return

        # 生成订单
        orders = self.dm.get_all_orders()
        new_order_id = max([o.id for o in orders], default=0) + 1
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order = Order(new_order_id, self.current_user.username, book_id, order_time)
        self.dm.save_order(order)

        # 修改教材状态
        book.status = "sold"
        self.dm.update_books(books)

        print(f"购买成功！订单号：{new_order_id}，请与卖家 {book.seller} 联系交易事宜。")

    # ---------- 订单相关 ----------
    def view_my_orders(self):
        if not self.current_user:
            print("请先登录。")
            return
        orders = self.dm.get_all_orders()
        my_orders = [o for o in orders if o.buyer == self.current_user.username]
        if not my_orders:
            print("暂无订单。")
            return
        books = self.dm.get_all_books()
        for o in my_orders:
            book = next((b for b in books if b.id == o.book_id), None)
            title = book.title if book else "已删除教材"
            print(f"订单号:{o.id} | {title} | 时间:{o.order_time} | 状态:{o.status}")

    def view_my_sales(self):
        if not self.current_user:
            print("请先登录。")
            return
        books = self.dm.get_all_books()
        my_books = [b for b in books if b.seller == self.current_user.username]
        if not my_books:
            print("您还没有发布过教材。")
            return
        orders = self.dm.get_all_orders()
        for book in my_books:
            order = next((o for o in orders if o.book_id == book.id), None)
            if order:
                print(f"教材《{book.title}》(ID:{book.id}) 已售出，买家:{order.buyer}，时间:{order.order_time}")
            else:
                print(f"教材《{book.title}》(ID:{book.id}) 仍在售。")

# ================== 命令行界面 ==================
def main():
    app = Marketplace()
    print("===== 二手教材交易平台 =====")
    while True:
        if not app.current_user:
            print("\n[未登录] 请选择操作：")
            print("1. 登录")
            print("2. 注册")
            print("3. 退出")
            choice = input("请输入数字：").strip()
            if choice == "1":
                username = input("用户名：")
                password = input("密码：")
                app.login(username, password)
            elif choice == "2":
                username = input("用户名：")
                password = input("密码：")
                role = input("角色(buyer/seller/both)：").strip().lower()
                email = input("邮箱(可选)：")
                app.register(username, password, role, email)
            elif choice == "3":
                print("再见！")
                break
            else:
                print("无效输入。")
        else:
            print(f"\n[已登录：{app.current_user.username}，角色：{app.current_user.role}]")
            print("1. 浏览所有在售教材")
            print("2. 搜索教材（关键词/ISBN）")
            print("3. 按价格范围浏览")
            if app.current_user.role in ("seller", "both"):
                print("4. 发布教材")
            if app.current_user.role in ("buyer", "both"):
                print("5. 购买教材（输入ID）")
            print("6. 查看我的订单（作为买家）")
            if app.current_user.role in ("seller", "both"):
                print("7. 查看我的销售记录")
            print("8. 登出")
            print("0. 退出程序")
            choice = input("请输入数字：").strip()
            if choice == "1":
                app.browse_books()
            elif choice == "2":
                kw = input("输入关键词或ISBN：")
                app.browse_books(keyword=kw)
            elif choice == "3":
                try:
                    min_p = input("最低价格(留空表示不限)：").strip()
                    max_p = input("最高价格(留空表示不限)：").strip()
                    min_p = float(min_p) if min_p else None
                    max_p = float(max_p) if max_p else None
                    app.browse_books(min_price=min_p, max_price=max_p)
                except ValueError:
                    print("价格请输入数字。")
            elif choice == "4" and app.current_user.role in ("seller", "both"):
                title = input("教材标题：")
                author = input("作者：")
                isbn = input("ISBN：")
                try:
                    price = float(input("价格："))
                except ValueError:
                    print("价格无效。")
                    continue
                desc = input("描述：")
                app.publish_book(title, author, isbn, price, desc)
            elif choice == "5" and app.current_user.role in ("buyer", "both"):
                try:
                    bid = int(input("请输入教材ID："))
                except ValueError:
                    print("ID必须是数字。")
                    continue
                app.buy_book(bid)
            elif choice == "6":
                app.view_my_orders()
            elif choice == "7" and app.current_user.role in ("seller", "both"):
                app.view_my_sales()
            elif choice == "8":
                app.logout()
            elif choice == "0":
                print("感谢使用，再见！")
                break
            else:
                print("无效选项，请重试。")

if __name__ == "__main__":
    main()


