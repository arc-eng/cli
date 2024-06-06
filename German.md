<div align="center">
<img src="https://avatars.githubusercontent.com/ml/17635?s=140&v=" width="100" alt="PR Pilot Logo">
</div>

<p align="center">
  <a href="https://github.com/apps/pr-pilot-ai/installations/new"><b>Installieren</b></a> |
  <a href="https://docs.pr-pilot.ai">Dokumentation</a> |
  <a href="https://www.pr-pilot.ai/blog">Blog</a> |
  <a href="https://www.pr-pilot.ai">Webseite</a>
</p>

# PR Pilot Kommandozeilen-Schnittstelle

[PR Pilot](https://docs.pr-pilot.ai) bietet Ihnen eine Schnittstelle in natürlicher Sprache für Ihre Github-Projekte.
Anhand einer Eingabeaufforderung verwendet es LLMs (Large Language Models), um Aufgaben autonom zu erfüllen, indem es mit Ihrem Codebase
und Github-Issues interagiert.

Mit [Eingabeaufforderungsvorlagen](./prompts) können Sie leistungsstarke,
wiederverwendbare Befehle erstellen, die von PR Pilot ausgeführt werden können.

## 🛠️ Verwendung

Öffnen Sie ein Terminal und `ls` in ein Repository, in dem Sie PR Pilot [installiert](https://github.com/apps/pr-pilot-ai/installations/new) haben.

Verwenden Sie in Ihrem Repository den Befehl `pilot`:

```bash
pilot "Erzählen Sie mir von diesem Projekt!"
```

**📝 Bitten Sie PR Pilot, eine lokale Datei für Sie zu bearbeiten:**

```bash
pilot --edit cli/cli.py "Stellen Sie sicher, dass alle Funktionen und Klassen Docstrings haben."
```

**⚡ Generieren Sie schnell Code und speichern Sie ihn als Datei:**

```bash
pilot -o test_utils.py --code "Schreiben Sie einige Unit-Tests für die Datei utils.py."
```

**🔍 Erfassen Sie einen Teil Ihres Bildschirms und fügen Sie ihn einer Eingabeaufforderung hinzu:**

```bash
pilot -o component.html --code --snap "Schreiben Sie eine Bootstrap5-Komponente, die so aussieht."
```

**📊 Erhalten Sie eine organisierte Ansicht Ihrer Github-Issues:**

```bash
pilot "Finden Sie alle offenen Github-Issues, die als 'Bug' gekennzeichnet sind, kategorisieren und priorisieren Sie sie"
```

**📝 Generieren Sie Teile Ihrer Dokumentation mit einer [Vorlage](./prompts/README.md.jinja2):**

```bash
pilot --direct -f prompts/README.md.jinja2 -o README.md
```

Um mehr über Vorlagen zu erfahren, schauen Sie sich das Verzeichnis [prompts](./prompts) an.

**📝 Führen Sie einen Schritt-für-Schritt-Plan aus:**

Zerlegen Sie komplexere Aufgaben in kleinere Schritte mit einem Plan:

```yaml
# document_cli.yaml

name: Dokumentieren Sie die CLI
prompt: |
  Die CLI ist großartig, aber wir brauchen eine umfassende Benutzerdokumentation.
  Die Dokumentation sollte als Markdown-Dateien im Repository gespeichert werden.

steps:
  - name: Dokumentationsbedarf identifizieren
    output_file: doc_instructions.md
    prompt: |
      1. Lesen Sie `cli/cli.py`
      2. Identifizieren Sie die Hauptfunktionen der CLI und wie sie funktioniert
      3. Listen Sie die zu erstellenden Dokumentationsdateien auf und skizzieren Sie deren Inhalt
      4. Erstellen Sie Schritt-für-Schritt-Anweisungen zur Erstellung der Dokumentation

  - name: Dokumentieren Sie die CLI
    template: doc_instructions.md
```

Führen Sie es mit `pilot --plan document_cli.yaml` aus.

### ⚙️ Optionen und Parameter

Sie können Ihre Interaktion mit PR Pilot mithilfe von Parametern und Optionen anpassen:

```bash
Usage: pilot [OPTIONS] [PROMPT]...

  Erstellen Sie eine neue Aufgabe für PR Pilot - https://docs.pr-pilot.ai

Options:
  --wait / --no-wait        Warten Sie, bis PR Pilot die Aufgabe abgeschlossen hat.
  --repo TEXT               Github-Repository im Format owner/repo.
  --snap                    Wählen Sie einen Teil Ihres Bildschirms aus, um ihn als Bild
                            zur Aufgabe hinzuzufügen.
  -p, --plan PATH           Pfad zur YAML-Datei mit Schritt-für-Schritt-Plan für
                            PR Pilot.
  -e, --edit PATH           Lassen Sie PR Pilot eine Datei für Sie bearbeiten.
  --spinner / --no-spinner  Zeigen Sie einen Ladeindikator an.
  --quiet                   Deaktivieren Sie alle Ausgaben im Terminal.
  --cheap                   Verwenden Sie das günstigste GPT-Modell (gpt-3.5-turbo)
  --code                    Optimieren Sie die Eingabeaufforderung und die Einstellungen für die Codegenerierung
  -f, --file PATH           Generieren Sie die Eingabeaufforderung aus einer Vorlagendatei.
  --direct                  Geben Sie die gerenderte Vorlage nicht als Eingabeaufforderung in
                            PR Pilot ein, sondern geben Sie sie direkt als Ausgabe aus.
  -o, --output PATH         Ausgabedatei für das Ergebnis.
  -m, --model TEXT          Zu verwendendes GPT-Modell.
  --debug                   Zeigen Sie Debug-Informationen an.
  --help                    Zeigen Sie diese Nachricht an und beenden Sie.

```

## ⚙️ Konfiguration
Die Konfigurationsdatei befindet sich unter `~/.pr-pilot.yaml`.

```yaml
# Ihr API-Schlüssel von https://app.pr-pilot.ai/dashboard/api-keys/
api_key: IHR_API_KEY

# Standard-Github-Repository, wenn CLI nicht in einem Repository-Verzeichnis ausgeführt wird
default_repo: owner/repo
```

## 🤝 Beitrag
Mitwirkende sind willkommen, die CLI zu verbessern, indem sie Pull-Requests einreichen oder Probleme melden. Weitere Details finden Sie im GitHub-Repository des Projekts.

## 📜 Lizenz
Die PR Pilot CLI ist Open-Source-Software, die unter der GPL-3-Lizenz lizenziert ist.
