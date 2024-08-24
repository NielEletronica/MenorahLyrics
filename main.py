import tkinter as tk
from tkinter import PhotoImage, messagebox, filedialog
import requests
import random
import webbrowser

version = 0.1

class LyricsApp:
    def __init__(self, root):
        self.root = root
        self.root.title('MenorahLyrics')

        self.root.call('source', 'Azure/azure.tcl')
        self.root.call('set_theme', 'dark')
        

        self.root.resizable(False, False)

        # Load API keys from file
        self.api_keys = self.load_api_keys('api_keys.txt')
        if not self.api_keys:
            messagebox.showerror('Erro', 'Nenhuma chave API encontrada')
            self.root.destroy()
            return

        # Create initial song input fields
        self.song_frame = tk.Frame(root)
        self.song_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.artist_entries = []
        self.song_entries = []
        self.create_initial_song_input_fields()

        self.image = PhotoImage(file='vagalume.png')  # Adjust the path to your image file
        self.image_label = tk.Label(root, image=self.image)
        self.image_label.grid(row=1, column=0, columnspan=2, pady=10)

        
        # Buttons
        self.add_more_button = tk.Button(root, text='Adicionar mais músicas', command=self.add_song_input_fields)
        self.add_more_button.grid(row=1, column=0, pady=10)

        self.remove_button = tk.Button(root, text='Remover última música', command=self.remove_song_input_fields)
        self.remove_button.grid(row=1, column=1, pady=10)

        self.fetch_button = tk.Button(root, text='Pesquisar Letras', command=self.fetch_lyrics)
        self.fetch_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.save_button = tk.Button(root, text='Salvar Letras', command=self.save_lyrics, state=tk.DISABLED)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.lyrics_text = tk.Text(root, wrap=tk.WORD, height=15, width=60)
        self.lyrics_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.lyrics = []

        # Footer with version and GitHub link
        self.footer_frame = tk.Frame(root)
        self.footer_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='s')

         # GitHub link
        self.github_link = tk.Label(self.footer_frame, text='https://github.com/NielEletronica/MenorahLyrics' + f' : {version}', fg='blue', cursor='hand2')
        self.github_link.pack(side=tk.LEFT, padx=(0, 40))
        self.github_link.bind("<Button-1>", self.open_github)

        # Vagalume link
        self.vagalume_link = tk.Label(self.footer_frame, text='Vagalume', fg='blue', cursor='hand2')
        self.vagalume_link.pack(side=tk.RIGHT, padx=(80, 0))
        self.vagalume_link.bind("<Button-1>", self.open_vagalume)

        


       

    def load_api_keys(self, filename):
        try:
            with open(filename, 'r') as file:
                keys = [line.strip() for line in file if line.strip()]
            return keys
        except IOError as e:
            messagebox.showerror('Erro de arquivo', f'Erro ao ler chaves de API: {e}')
            return []

    def create_initial_song_input_fields(self):
        # Create two initial input fields
        self.add_song_input_fields()
        self.add_song_input_fields()

    def add_song_input_fields(self):
        num_fields = len(self.artist_entries)
        tk.Label(self.song_frame, text=f'Artista {num_fields + 1}:').grid(row=num_fields * 2, column=0, padx=10, pady=5, sticky='w')
        artist_entry = tk.Entry(self.song_frame, width=40)
        artist_entry.grid(row=num_fields * 2, column=1, padx=10, pady=5)
        self.artist_entries.append(artist_entry)

        tk.Label(self.song_frame, text=f'Música {num_fields + 1}:').grid(row=num_fields * 2 + 1, column=0, padx=10, pady=5, sticky='w')
        song_entry = tk.Entry(self.song_frame, width=40)
        song_entry.grid(row=num_fields * 2 + 1, column=1, padx=10, pady=5)
        self.song_entries.append(song_entry)

    def remove_song_input_fields(self):
        if not self.artist_entries:
            messagebox.showwarning('Sem mais músicas', 'Sem mais músicas para remover')
            return

        # Remove last set of fields and labels
        last_artist_entry = self.artist_entries.pop()
        last_song_entry = self.song_entries.pop()

        # Remove widgets from the window
        for widget in self.song_frame.winfo_children():
            if widget == last_artist_entry or widget == last_song_entry:
                widget.destroy()
            elif isinstance(widget, tk.Label) and widget.grid_info()['row'] == len(self.artist_entries) * 2:
                widget.destroy()
            elif isinstance(widget, tk.Label) and widget.grid_info()['row'] == len(self.artist_entries) * 2 + 1:
                widget.destroy()

        # Re-layout remaining fields
        for i, (artist_entry, song_entry) in enumerate(zip(self.artist_entries, self.song_entries)):
            artist_entry.grid(row=i * 2, column=1, padx=10, pady=5)
            song_entry.grid(row=i * 2 + 1, column=1, padx=10, pady=5)
            tk.Label(self.song_frame, text=f'Artista {i + 1}:').grid(row=i * 2, column=0, padx=10, pady=5, sticky='w')
            tk.Label(self.song_frame, text=f'Música {i + 1}:').grid(row=i * 2 + 1, column=0, padx=10, pady=5, sticky='w')

    def fetch_lyrics(self):
        self.lyrics = []
        for artist_entry, song_entry in zip(self.artist_entries, self.song_entries):
            artist = artist_entry.get()
            song = song_entry.get()

            if not artist or not song:
                continue

            api_key = random.choice(self.api_keys)
            url = 'https://api.vagalume.com.br/search.php'
            params = {
                'art': artist,
                'mus': song,
                'apikey': api_key
            }
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                # Check for 'mus' key and ensure it has data
                if 'mus' not in data or not data['mus']:
                    raise ValueError('Letra não encontrada')

                letra = data['mus'][0].get('text', 'Letra não disponível')
                title = f'--- {artist} - {song} ---\n\n'
                self.lyrics.append(title + letra.upper())
            except requests.exceptions.HTTPError as e:
                messagebox.showerror('Erro de API', f'Erro HTTP: {e}')
                return
            except requests.exceptions.RequestException as e:
                messagebox.showerror('Erro de API', f'Ocorreu uma exceção de solicitação: {e}')
                return
            except (KeyError, IndexError, ValueError) as e:
                messagebox.showerror('Erro de Data', f'Erro ao processar data para "{artist} - {song}": {e}')

        if self.lyrics:
            self.lyrics_text.delete('1.0', tk.END)
            self.lyrics_text.insert(tk.END, '\n\n'.join(self.lyrics))
            self.save_button.config(state=tk.NORMAL)
        else:
            messagebox.showinfo('Sem letra', 'Nenhuma letra encontrada')

    def save_lyrics(self):
        if not self.lyrics:
            messagebox.showwarning('Sem letra', 'Não há letras para salvar')
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt')],
            title='Salvar letra como: '
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write('\n\n'.join(self.lyrics))
                messagebox.showinfo('Sucesso', 'Letras salvas com sucesso')
            except IOError as e:
                messagebox.showerror('Erro de arquivo', f'Erro ao salvar arquivo: {e}')

    def open_github(self, event):
        webbrowser.open('https://github.com/NielEletronica/MenorahLyrics')

    def open_vagalume(self, event):
        webbrowser.open('https://www.vagalume.com.br/')

if __name__ == '__main__':
    root = tk.Tk()
    app = LyricsApp(root)
    root.mainloop()
