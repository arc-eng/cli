### README_German.md
<div align="center">
<img src="https://avatars.githubusercontent.com/ml/17635?s=140&v=" width="100" alt="PR Pilot Logo">
</div>

<p align="center">
  <a href="https://github.com/apps/pr-pilot-ai/installations/new"><b>Installieren</b></a> |
  <a href="https://docs.pr-pilot.ai">Dokumentation</a> | 
  <a href="https://www.pr-pilot.ai/blog">Blog</a> | 
  <a href="https://www.pr-pilot.ai">Webseite</a>
</p>

# PR Pilot CLI

PR Pilot bietet Ihnen eine natürliche Sprachschnittstelle für Ihre Github-Projekte.
Auf Basis eines Prompts verwendet es LLMs (Large Language Models), um Aufgaben autonom durch Interaktion mit Ihrer Codebasis
und Github-Issues zu erfüllen, was eine Vielzahl von wegweisenden, KI-gestützten Automatisierungsmöglichkeiten ermöglicht.

## Installation

 > Stellen Sie sicher, dass Sie PR Pilot [in Ihrem Repository installiert haben](https://github.com/apps/pr-pilot-ai/installations/new)

Um die CLI zu installieren, führen Sie den folgenden Befehl aus:

```bash
pip install --upgrade pr-pilot-cli
```

Standardmäßig fordert die CLI Sie auf, Ihren API-Schlüssel einzugeben, falls dieser noch nicht konfiguriert ist.

## Nutzung

Nach der Installation öffnen Sie ein Terminal und `ls` in ein Repository, in dem Sie PR Pilot installiert haben, und sprechen Sie mit PR Pilot:

### Beispiele

Übersetzen Sie eine Datei:

```bash
pilot --raw "übersetze das README ins Deutsche" > README_German.md
```

Lassen Sie einige Unit-Tests schreiben:

```bash
pilot "Schreibe einige Unit-Tests für die Datei utils.py."
```

Finden Sie Informationen in Ihren Github-Issues:

```bash
pilot "Haben wir offene Github-Issues bezüglich der Klasse AuthenticationView?"
```

Für weitere Informationen schauen Sie in unserem [Benutzerhandbuch](https://docs.pr-pilot.ai/user_guide.html).

### Optionen und Parameter

Sie können die Standardeinstellungen mit Parametern und Optionen ändern:

```bash
Usage: pilot [OPTIONS] [PROMPT]...

Options:
  --wait / --no-wait  Warten Sie auf das Ergebnis.
  --repo TEXT         Github-Repository im Format owner/repo.
  --chatty            Drucke mehr Informationen.
  --raw               Für Pipelines. Kein schöner Druck, kein Statusindikator.
  --help              Zeige diese Nachricht und beende.
```


## Funktionen
- **Konfigurationsmanagement**: Verwaltet automatisch die Konfiguration des API-Schlüssels, indem der Benutzer aufgefordert wird, seinen API-Schlüssel einzugeben, falls dieser noch nicht konfiguriert ist.
- **Aufgabenerstellung**: Benutzer können Aufgaben erstellen, indem sie ein Repository und einen Prompt angeben. Die CLI übernimmt die Aufgabenerstellung und wartet optional auf das Ergebnis.
- **Ergebnisabruf**: Wenn die Option `--wait` verwendet wird, wartet die CLI auf die Fertigstellung der Aufgabe und zeigt das Ergebnis direkt im Terminal an.
- **Dashboard-Link**: Für Aufgaben, die nicht abgewartet werden, bietet die CLI einen Link zum Dashboard der Aufgabe für weitere Überwachung.


## Konfiguration
Die Konfigurationsdatei befindet sich unter `~/.pr-pilot.yaml`.

## Mitwirken
Mitwirkende sind willkommen, die CLI zu verbessern, indem sie Pull-Anfragen einreichen oder Probleme melden. Weitere Details finden Sie im GitHub-Repository des Projekts.

## Lizenz
Die PR Pilot CLI ist Open-Source-Software, lizenziert unter der GPL-3-Lizenz.