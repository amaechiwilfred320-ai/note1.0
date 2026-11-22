from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import json
import os
from datetime import datetime

def get_notes_path():
    # Save notes.json in the same folder as this file.
    # This fixes the Windows PermissionError.
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, 'notes.json')

class NotepadWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 5
        self.padding = 10
        self.current_index = None
        self.notes = self.load_notes()

        # Top title
        self.title_label = Label(
            text='Date - Notepad',
            font_size=26,
            bold=True,
            size_hint_y=0.1,
            color=(0, 0.6, 1, 1)
        )
        self.add_widget(self.title_label)

        # Title input
        self.note_title = TextInput(
            hint_text='Note title...',
            multiline=False,
            size_hint_y=0.08,
            font_size=18
        )
        self.add_widget(self.note_title)

        # Main text area
        self.text_area = TextInput(
            hint_text='Write your note here...',
            font_size=18,
            size_hint_y=0.45
        )
        self.add_widget(self.text_area)

        # Buttons row
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=5)
        save_btn = Button(text='Save', background_color=(0, 0.7, 0.3, 1))
        save_btn.bind(on_press=self.save_note)
        new_btn = Button(text='New', background_color=(0, 0.6, 1, 1))
        new_btn.bind(on_press=self.new_note)
        delete_btn = Button(text='Delete', background_color=(1, 0.2, 0.2, 1))
        delete_btn.bind(on_press=self.delete_note)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(new_btn)
        btn_row.add_widget(delete_btn)
        self.add_widget(btn_row)

        self.status = Label(
            text='Ready',
            size_hint_y=0.05,
            font_size=14,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.status)

        # Notes list label
        self.add_widget(Label(
            text='My Notes:',
            font_size=18,
            bold=True,
            size_hint_y=0.07,
            halign='left'
        ))

        # Scroll list
        scroll = ScrollView(size_hint_y=0.4)
        self.list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        scroll.add_widget(self.list_layout)
        self.add_widget(scroll)

        self.refresh_list()

    def load_notes(self):
        path = get_notes_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return []
            except:
                return []
        return []

    def save_to_file(self):
        path = get_notes_path()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=2)
        except Exception as e:
            self.status.text = f'Could not save: {e}'

    def save_note(self, instance):
        title = self.note_title.text.strip()
        content = self.text_area.text.strip()
        if not content:
            self.status.text = 'Note is empty, cannot save'
            return
        if not title:
            title = content[:30]
        date_now = datetime.now().strftime('%d %b %Y - %I:%M %p')
        note = {'title': title, 'content': content, 'date': date_now}
        if self.current_index is not None and 0 <= self.current_index < len(self.notes):
            self.notes[self.current_index] = note
            self.status.text = 'Note updated'
        else:
            self.notes.insert(0, note)
            self.status.text = 'Note saved'
        self.save_to_file()
        self.refresh_list()
        self.new_note(None)

    def new_note(self, instance):
        self.note_title.text = ''
        self.text_area.text = ''
        self.current_index = None
        self.status.text = 'New note'

    def delete_note(self, instance):
        if self.current_index is not None and 0 <= self.current_index < len(self.notes):
            del self.notes[self.current_index]
            self.save_to_file()
            self.refresh_list()
            self.new_note(None)
            self.status.text = 'Note deleted'
        else:
            self.status.text = 'Open a note first to delete it'

    def open_note(self, index):
        if 0 <= index < len(self.notes):
            note = self.notes[index]
            self.note_title.text = note.get('title', '')
            self.text_area.text = note.get('content', '')
            self.current_index = index
            self.status.text = f"Opened - {note.get('date', '')}"

    def refresh_list(self):
        self.list_layout.clear_widgets()
        if not self.notes:
            self.list_layout.add_widget(
                Label(text='No notes yet. Write one above.', size_hint_y=None, height=40)
            )
            return
        for i, note in enumerate(self.notes):
            title = note.get('title', 'Untitled')
            date_text = note.get('date', '')
            btn = Button(
                text=f"{title}\n{date_text}",
                size_hint_y=None,
                height=60,
                halign='left',
                valign='middle',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0, 0, 0, 1)
            )
            btn.bind(on_press=lambda x, idx=i: self.open_note(idx))
            self.list_layout.add_widget(btn)

class DateApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return NotepadWidget()

if __name__ == '__main__':
    DateApp().run()