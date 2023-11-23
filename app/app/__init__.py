import flet as ft
import sqlite3
import datetime
import os



db_file = 'database.db'
with sqlite3.connect(db_file) as connection:
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT (1) FROM people")
    except:
        cursor.execute("""CREATE TABLE people (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	name TEXT(255) NOT NULL,
	date TEXT(10) NOT NULL
);""")


class Task(ft.UserControl):
    def __init__(self, task_name, task_delete):
        super().__init__()
        self.task_name = task_name
        self.task_delete = task_delete

    def build(self):
        self.display_task = ft.Text(value=self.task_name)
        self.display_view = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Удалить",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )
        return None
        # return ft.Column(controls=[self.display_view])

    def delete_clicked(self, e):
        self.task_delete(self, e)

class TodoApp(ft.UserControl):
    def build(self):
        self.new_task = ft.TextField(hint_text="ФИО", expand=True)
        self.tasks = ft.Column()
        self.date_picker = ft.DatePicker(
            on_change=self.change_date,
            on_dismiss=self.date_picker_dismissed,
            first_date=datetime.datetime(2023, 10, 1)
        )
        self.date_button = ft.ElevatedButton(
            f"{str(datetime.datetime.now()).split(' ')[0]}",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.date_picker.pick_date(),
        )

        def close_banner(e):
            self.banner.open = False
            self.update()

        with sqlite3.connect(db_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, date FROM people")
            rows_from_db = cursor.fetchall()
        
        self.show_rows = []
        self.infive = []
        for row in rows_from_db:
            color = ft.colors.GREY_100
            date = datetime.datetime.strptime(row[2], '%Y-%m-%d').strftime('%d.%m.%y')
            today = (datetime.datetime.now() - datetime.datetime.strptime(row[2], '%Y-%m-%d')).days
            if today and today % 5 == 0:
                self.infive.append(f"{row[1]} - {today} день")
                color = ft.colors.AMBER_50
            elif today and today % 10 == 0:
                self.infive.append(f"{row[1]} - {today} день")
                color = ft.colors.AMBER_100
            elif today and today % 15 == 0:
                self.infive.append(f"{row[1]} - {today} день")
                color = ft.colors.AMBER_200 
            self.show_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{row[1]}")),
                    ft.DataCell(ft.Text(f"{date}")),
                    ft.DataCell(ft.Text(f"{today}")),
                    ft.DataCell(
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Удалить",
                            on_click=self.task_delete,
                            data=row[0]
                        )
                    ),
                ],
                data=row[0],
                color=color
                ),
            )
        if self.infive:
            self.banner = ft.Banner(
            bgcolor=ft.colors.AMBER_100,
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
            content=ft.Text('\n'.join(self.infive)
            ),
            actions=[
            ft.TextButton("Ok", on_click=close_banner),
            ],
            )
            self.banner.open = True


        self.display_view = ft.DataTable(
            bgcolor= ft.colors.BLUE_50,
            width=10000,
            columns=[
                ft.DataColumn(ft.Text("ФИО")),
                ft.DataColumn(ft.Text("Дата")),
                ft.DataColumn(ft.Text("Кол-во дней"), numeric= True),
                ft.DataColumn(ft.Text(""))
            ],
            rows=self.show_rows
        )

        try:

            self.column =  ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.new_task,
                            self.date_button,
                            self.date_picker,
                            ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked),
                        ],
                    ),
                    self.display_view,
                    self.tasks,
                    self.banner
                ],
            )
        except:
            self.column =  ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.new_task,
                            self.date_button,
                            self.date_picker,
                            ft.FloatingActionButton(icon=ft.icons.ADD, on_click=self.add_clicked),
                        ],
                    ),
                    self.display_view,
                    self.tasks
                ],
            )
        return self.column

    def change_date(self, e):
        self.date_button.text = f"{str(self.date_picker.value).split(' ')[0]}"
        self.update()

    def date_picker_dismissed(self, e):
        self.date_button.text = "Дата"
        self.update()

    def add_clicked(self, e):
        color = ft.colors.GREY_50
        if not self.new_task.value:
            self.new_task.error_text = "Заполнить ФИО"
        elif self.date_button.text == "Дата":
            self.new_task.error_text = "Выбери дату"
        else:
            data_to_insert = [self.new_task.value, self.date_button.text]
            with sqlite3.connect(db_file) as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO people (name,date) VALUES (?, ?)", data_to_insert)
                id = cursor.lastrowid
            date = datetime.datetime.strptime(self.date_button.text, '%Y-%m-%d').strftime('%d.%m.%y')
            today = (datetime.datetime.now() - datetime.datetime.strptime(self.date_button.text, '%Y-%m-%d')).days
            if today == 4:
                color = ft.colors.AMBER_50
            if today == 11:
                color = ft.colors.AMBER_100
            if today == 17:
                color = ft.colors.AMBER_200 
            self.show_rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"{self.new_task.value}")),
                    ft.DataCell(ft.Text(f"{date}")),
                    ft.DataCell(ft.Text(f"{today}")),
                    ft.DataCell(
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="Удалить",
                            on_click=self.task_delete,
                            data=id
                        )
                    ),
                ],
                data = id,
                color=color
                )
            )
            self.new_task.error_text = None
            self.new_task.value = ""
            date = str(datetime.datetime.now()).split(' ')[0]
            self.date_button.text = date
        self.update()

    def task_delete(self, task):
        with sqlite3.connect(db_file,timeout=30) as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM people WHERE id = ?", (str(task.control.data),))
        for i,row in enumerate(self.show_rows):
            if row.data == task.control.data:
                self.show_rows.__delitem__(i)
        # self.tasks.controls.remove(task)
        self.update()

def main(page: ft.Page):
    page.title = "Цикл осмотра"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "always"
    page.window_width = 500
    page.window_resizable = True
    page.update()
    todo = TodoApp()
    page.add(todo)

if __name__ == '__main__':
    ft.app(target=main)