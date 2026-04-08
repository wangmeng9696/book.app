import flet as ft
from core import Marketplace

class SecondhandMarketApp:
    def __init__(self):
        self.market = Marketplace()
        self.page = None
        self.main_view = None      # 主页视图（包含教材列表）
        self.bottom_nav = None

    def main(self, page: ft.Page):
        self.page = page
        page.title = "二手教材交易平台"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 10
        page.window_width = 400
        page.window_height = 700

        # 如果未登录，显示登录/注册页面；否则显示主页
        self.show_auth_page()

    # ==================== 认证页面 ====================
    def show_auth_page(self):
        def on_login_click(e):
            username = login_username.value
            password = login_password.value
            if self.market.login(username, password):
                self.page.snack_bar = ft.SnackBar(ft.Text("登录成功"), bgcolor="green")
                self.page.snack_bar.open = True
                self.show_main_page()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("用户名或密码错误"), bgcolor="red")
                self.page.snack_bar.open = True
            self.page.update()

        def on_register_click(e):
            self.show_register_page()

        login_username = ft.TextField(label="用户名", width=300)
        login_password = ft.TextField(label="密码", password=True, can_reveal_password=True, width=300)
        login_btn = ft.ElevatedButton("登录", on_click=on_login_click, width=300)
        register_btn = ft.OutlinedButton("注册新账号", on_click=on_register_click, width=300)

        self.page.clean()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("📚 二手教材交易", size=32, weight="bold"),
                        ft.Divider(height=20),
                        login_username,
                        login_password,
                        login_btn,
                        register_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        )
        self.page.update()

    def show_register_page(self):
        def on_submit(e):
            username = reg_username.value
            password = reg_password.value
            role = role_dropdown.value
            email = reg_email.value
            if self.market.register(username, password, role, email):
                self.page.snack_bar = ft.SnackBar(ft.Text("注册成功，请登录"), bgcolor="green")
                self.page.snack_bar.open = True
                self.show_auth_page()
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("用户名已存在"), bgcolor="red")
                self.page.snack_bar.open = True
            self.page.update()

        reg_username = ft.TextField(label="用户名", width=300)
        reg_password = ft.TextField(label="密码", password=True, width=300)
        reg_email = ft.TextField(label="邮箱", width=300)
        role_dropdown = ft.Dropdown(
            label="角色",
            options=[
                ft.dropdown.Option("buyer", "买家"),
                ft.dropdown.Option("seller", "卖家"),
                ft.dropdown.Option("both", "买/卖"),
            ],
            value="buyer",
            width=300,
        )
        submit_btn = ft.ElevatedButton("注册", on_click=on_submit)
        back_btn = ft.TextButton("返回登录", on_click=lambda e: self.show_auth_page())

        self.page.clean()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("注册新账号", size=28),
                        reg_username,
                        reg_password,
                        reg_email,
                        role_dropdown,
                        submit_btn,
                        back_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
        )
        self.page.update()

    # ==================== 主界面（教材列表 + 底部导航） ====================
    def show_main_page(self):
        # 刷新教材列表
        self.refresh_book_list()

        # 底部导航栏
        self.bottom_nav = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.HOME, label="首页"),
                ft.NavigationDestination(icon=ft.icons.ADD_CIRCLE, label="发布"),
                ft.NavigationDestination(icon=ft.icons.SHOPPING_CART, label="我的订单"),
                ft.NavigationDestination(icon=ft.icons.SELL, label="我的销售"),
                ft.NavigationDestination(icon=ft.icons.PERSON, label="个人"),
            ],
            on_change=self.on_nav_change,
        )

        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Row([ft.Text("📖 在售教材", size=24, weight="bold")], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row(
                        [
                            ft.IconButton(ft.icons.SEARCH, on_click=self.show_search_dialog),
                            ft.IconButton(ft.icons.FILTER_LIST, on_click=self.show_filter_dialog),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Divider(),
                    self.book_list_view,   # 教材列表
                    ft.Divider(),
                    self.bottom_nav,
                ],
                expand=True,
                spacing=10,
            )
        )
        self.page.update()

    def refresh_book_list(self):
        # 获取所有在售教材
        books = self.market.dm.get_all_books()
        available_books = [b for b in books if b.status == "available"]
        self.book_list_view = ft.ListView(expand=True, spacing=10)
        if not available_books:
            self.book_list_view.controls.append(ft.Text("暂无在售教材", italic=True))
        else:
            for book in available_books:
                self.book_list_view.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.ListTile(
                                        leading=ft.Icon(ft.icons.BOOK),
                                        title=ft.Text(book.title, weight="bold"),
                                        subtitle=ft.Text(f"作者: {book.author}  |  ¥{book.price}"),
                                    ),
                                    ft.Row(
                                        [
                                            ft.Text(f"卖家: {book.seller}", size=12),
                                            ft.IconButton(
                                                ft.icons.SHOPPING_CART,
                                                on_click=lambda e, bid=book.id: self.buy_book(bid),
                                                icon_color=ft.colors.GREEN,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                ],
                                spacing=5,
                            ),
                            padding=10,
                        ),
                        elevation=3,
                    )
                )

    def on_nav_change(self, e):
        index = e.control.selected_index
        if index == 0:   # 首页
            self.refresh_book_list()
            # 更新列内容：保持底部导航不变，只替换教材列表区域
            self.page.controls[0].controls[2] = self.book_list_view
        elif index == 1: # 发布教材
            self.show_publish_page()
        elif index == 2: # 我的订单
            self.show_my_orders()
        elif index == 3: # 我的销售
            self.show_my_sales()
        elif index == 4: # 个人
            self.show_profile()
        self.page.update()

    # ==================== 购买功能 ====================
    def buy_book(self, book_id):
        if not self.market.current_user:
            self.page.snack_bar = ft.SnackBar(ft.Text("请先登录"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return
        # 检查用户角色是否有购买权限
        if self.market.current_user.role not in ("buyer", "both"):
            self.page.snack_bar = ft.SnackBar(ft.Text("当前账号无法购买，请使用买家角色"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.market.buy_book(book_id)
        self.page.snack_bar = ft.SnackBar(ft.Text("购买成功！请查看我的订单"), bgcolor="green")
        self.page.snack_bar.open = True
        self.refresh_book_list()   # 刷新首页列表
        # 如果当前在主页，更新列表显示
        if self.bottom_nav and self.bottom_nav.selected_index == 0:
            self.page.controls[0].controls[2] = self.book_list_view
        self.page.update()

    # ==================== 发布教材页面 ====================
    def show_publish_page(self):
        if self.market.current_user.role not in ("seller", "both"):
            self.page.snack_bar = ft.SnackBar(ft.Text("只有卖家可以发布教材"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            self.show_main_page()
            return

        title_field = ft.TextField(label="教材标题", width=300)
        author_field = ft.TextField(label="作者", width=300)
        isbn_field = ft.TextField(label="ISBN", width=300)
        price_field = ft.TextField(label="价格", width=300, keyboard_type=ft.KeyboardType.NUMBER)
        desc_field = ft.TextField(label="描述", multiline=True, width=300, height=100)

        def on_publish(e):
            try:
                price = float(price_field.value)
            except ValueError:
                self.page.snack_bar = ft.SnackBar(ft.Text("价格必须是数字"), bgcolor="red")
                self.page.snack_bar.open = True
                self.page.update()
                return
            self.market.publish_book(
                title=title_field.value,
                author=author_field.value,
                isbn=isbn_field.value,
                price=price,
                description=desc_field.value,
            )
            self.page.snack_bar = ft.SnackBar(ft.Text("发布成功！"), bgcolor="green")
            self.page.snack_bar.open = True
            self.show_main_page()   # 返回主页并刷新

        publish_btn = ft.ElevatedButton("发布", on_click=on_publish)
        back_btn = ft.TextButton("返回", on_click=lambda e: self.show_main_page())

        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("📤 发布教材", size=24),
                    title_field,
                    author_field,
                    isbn_field,
                    price_field,
                    desc_field,
                    publish_btn,
                    back_btn,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            )
        )
        self.page.update()

    # ==================== 我的订单 ====================
    def show_my_orders(self):
        if not self.market.current_user:
            self.show_auth_page()
            return
        orders = self.market.dm.get_all_orders()
        my_orders = [o for o in orders if o.buyer == self.market.current_user.username]
        books = self.market.dm.get_all_books()
        order_cards = []
        for o in my_orders:
            book = next((b for b in books if b.id == o.book_id), None)
            title = book.title if book else "已下架教材"
            order_cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"订单号: {o.id}", weight="bold"),
                            ft.Text(f"教材: {title}"),
                            ft.Text(f"时间: {o.order_time}"),
                            ft.Text(f"状态: {o.status}"),
                        ]),
                        padding=10,
                    )
                )
            )
        if not order_cards:
            order_cards.append(ft.Text("暂无订单"))

        back_btn = ft.TextButton("返回主页", on_click=lambda e: self.show_main_page())
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("📦 我的订单", size=24),
                    ft.Column(order_cards, scroll=ft.ScrollMode.AUTO, expand=True),
                    back_btn,
                ],
                spacing=15,
                expand=True,
            )
        )
        self.page.update()

    # ==================== 我的销售 ====================
    def show_my_sales(self):
        if not self.market.current_user:
            self.show_auth_page()
            return
        if self.market.current_user.role not in ("seller", "both"):
            self.page.snack_bar = ft.SnackBar(ft.Text("当前账号不是卖家"), bgcolor="red")
            self.page.snack_bar.open = True
            self.show_main_page()
            return

        books = self.market.dm.get_all_books()
        my_books = [b for b in books if b.seller == self.market.current_user.username]
        orders = self.market.dm.get_all_orders()
        sale_cards = []
        for book in my_books:
            order = next((o for o in orders if o.book_id == book.id), None)
            if order:
                status_text = f"已售出，买家: {order.buyer}，时间: {order.order_time}"
            else:
                status_text = "在售中"
            sale_cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"《{book.title}》", weight="bold"),
                            ft.Text(f"价格: ¥{book.price}"),
                            ft.Text(status_text, size=12, color=ft.colors.GREEN if order else ft.colors.BLUE),
                        ]),
                        padding=10,
                    )
                )
            )
        if not sale_cards:
            sale_cards.append(ft.Text("您还没有发布过教材"))

        back_btn = ft.TextButton("返回主页", on_click=lambda e: self.show_main_page())
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("📈 我的销售", size=24),
                    ft.Column(sale_cards, scroll=ft.ScrollMode.AUTO, expand=True),
                    back_btn,
                ],
                spacing=15,
                expand=True,
            )
        )
        self.page.update()

    # ==================== 个人资料页 ====================
    def show_profile(self):
        user = self.market.current_user
        if not user:
            self.show_auth_page()
            return
        logout_btn = ft.ElevatedButton("登出", on_click=lambda e: self.logout(), bgcolor=ft.colors.RED_400)
        back_btn = ft.TextButton("返回主页", on_click=lambda e: self.show_main_page())

        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("👤 个人资料", size=24),
                    ft.Text(f"用户名: {user.username}", size=18),
                    ft.Text(f"角色: {user.role}"),
                    ft.Text(f"邮箱: {user.email}"),
                    ft.Divider(),
                    logout_btn,
                    back_btn,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
        self.page.update()

    def logout(self):
        self.market.logout()
        self.page.snack_bar = ft.SnackBar(ft.Text("已登出"), bgcolor="blue")
        self.page.snack_bar.open = True
        self.show_auth_page()

    # ==================== 搜索/筛选对话框 ====================
    def show_search_dialog(self):
        def on_search(e):
            keyword = search_field.value
            # 根据关键词刷新教材列表
            books = self.market.dm.get_all_books()
            available = [b for b in books if b.status == "available"]
            if keyword:
                filtered = [b for b in available if keyword.lower() in b.title.lower() or keyword.lower() in b.isbn]
            else:
                filtered = available
            self.update_book_list_display(filtered)
            dialog.open = False
            self.page.update()

        search_field = ft.TextField(label="输入书名或ISBN", width=300)
        dialog = ft.AlertDialog(
            title=ft.Text("搜索教材"),
            content=search_field,
            actions=[ft.TextButton("搜索", on_click=on_search)],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_filter_dialog(self):
        min_price = ft.TextField(label="最低价格", keyboard_type=ft.KeyboardType.NUMBER, width=150)
        max_price = ft.TextField(label="最高价格", keyboard_type=ft.KeyboardType.NUMBER, width=150)

        def on_filter(e):
            min_p = float(min_price.value) if min_price.value else None
            max_p = float(max_price.value) if max_price.value else None
            books = self.market.dm.get_all_books()
            available = [b for b in books if b.status == "available"]
            filtered = available
            if min_p is not None:
                filtered = [b for b in filtered if b.price >= min_p]
            if max_p is not None:
                filtered = [b for b in filtered if b.price <= max_p]
            self.update_book_list_display(filtered)
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("价格筛选"),
            content=ft.Row([min_price, max_price]),
            actions=[ft.TextButton("筛选", on_click=on_filter)],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def update_book_list_display(self, books):
        self.book_list_view.controls.clear()
        if not books:
            self.book_list_view.controls.append(ft.Text("没有找到符合条件的教材"))
        else:
            for book in books:
                self.book_list_view.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.BOOK),
                                    title=ft.Text(book.title, weight="bold"),
                                    subtitle=ft.Text(f"作者: {book.author}  |  ¥{book.price}"),
                                ),
                                ft.Row([
                                    ft.Text(f"卖家: {book.seller}", size=12),
                                    ft.IconButton(
                                        ft.icons.SHOPPING_CART,
                                        on_click=lambda e, bid=book.id: self.buy_book(bid),
                                        icon_color=ft.colors.GREEN,
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ]),
                            padding=10,
                        ),
                    )
                )
        # 更新主页显示
        if self.bottom_nav and self.bottom_nav.selected_index == 0:
            self.page.controls[0].controls[2] = self.book_list_view
        self.page.update()


def main():
    app = SecondhandMarketApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main()
