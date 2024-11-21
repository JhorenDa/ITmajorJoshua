import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty

# FastAPI Server URL
BASE_URL = "http://localhost:8000"

class NoteApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Header
        self.header = Label(text='MemoTime Notes', size_hint_y=None, height=40)
        self.add_widget(self.header)
        
        # Input fields for adding a new note
        self.title_input = TextInput(hint_text='Title', size_hint_y=None, height=40)
        self.content_input = TextInput(hint_text='Content', size_hint_y=None, height=80)
        self.add_widget(self.title_input)
        self.add_widget(self.content_input)
        
        # Button to add a new note
        self.add_btn = Button(text='Add Note', size_hint_y=None, height=50, on_press=self.add_note)
        self.add_widget(self.add_btn)
        
        # Scrollable list of notes
        self.notes_container = ScrollView()
        self.notes_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))
        self.notes_container.add_widget(self.notes_layout)
        self.add_widget(self.notes_container)

        # Load existing notes
        self.load_notes()

    def load_notes(self):
        """Fetch and display all notes from the FastAPI server."""
        response = requests.get(f"{BASE_URL}/notes/")
        if response.status_code == 200:
            notes = response.json()
            self.notes_layout.clear_widgets()
            for note in notes:
                self.notes_layout.add_widget(NoteItem(note, self))

    def add_note(self, instance):
        """Add a new note via FastAPI."""
        title = self.title_input.text
        content = self.content_input.text
        if title and content:
            response = requests.post(f"{BASE_URL}/notes/", json={
                "title": title,
                "content": content
            })
            if response.status_code == 200:
                self.title_input.text = ""
                self.content_input.text = ""
                self.load_notes()

class NoteItem(BoxLayout):
    """Widget to display a single note."""
    def __init__(self, note, parent, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.parent_layout = parent
        self.note_id = note['id']

        # Display title and content
        self.title_label = Label(text=f"Title: {note['title']}", size_hint_y=None, height=30)
        self.content_label = Label(text=f"Content: {note['content']}", size_hint_y=None, height=30)
        self.add_widget(self.title_label)
        self.add_widget(self.content_label)

        # Buttons for updating and deleting the note
        self.buttons_layout = BoxLayout(size_hint_y=None, height=40)
        self.update_btn = Button(text='Update', on_press=self.update_note)
        self.delete_btn = Button(text='Delete', on_press=self.delete_note)
        self.buttons_layout.add_widget(self.update_btn)
        self.buttons_layout.add_widget(self.delete_btn)
        self.add_widget(self.buttons_layout)

    def update_note(self, instance):
        """Update the note using FastAPI."""
        new_title = TextInput(text=self.title_label.text.split("Title: ")[1]).text
        new_content = TextInput(text=self.content_label.text.split("Content: ")[1]).text

        response = requests.put(f"{BASE_URL}/notes/{self.note_id}", json={
            "title": new_title,
            "content": new_content
        })
        if response.status_code == 200:
            self.parent_layout.load_notes()

    def delete_note(self, instance):
        """Delete the note using FastAPI."""
        response = requests.delete(f"{BASE_URL}/notes/{self.note_id}")
        if response.status_code == 200:
            self.parent_layout.load_notes()

class MemoTimeApp(App):
    def build(self):
        return NoteApp()

if __name__ == "__main__":
    MemoTimeApp().run()
