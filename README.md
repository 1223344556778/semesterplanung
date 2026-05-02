<h1>Semesterplanung Major BWL (HSG)</h1>

<p>Dieses Werkzeug dient der strukturierten Planung und Überprüfung des Fach- und Kontextstudiums für den Major Betriebswirtschaftslehre (BWL) an der Universität St.Gallen (HSG). Es ermöglicht den Abgleich der individuellen Kursbelegung mit den offiziellen Anforderungen der Studienordnung.</p>

<hr>

<h2>Projektbeschreibung</h2>
<p>Die Anwendung bietet eine automatisierte Validierung der Studienplanung auf Basis des offiziellen Regelwerks.</p>

<ul>
    <li><strong>ECTS-Kontrolle:</strong> Überwachung des Fortschritts zum Erreichen der erforderlichen 120 ECTS.</li>
    <li><strong>Vertiefung Finance:</strong> Prüfung der notwendigen 16 ECTS im Vertiefungsbereich sowie der Anforderungen für Capstone-Projekte oder die Bachelorarbeit.</li>
    <li><strong>Austausch-Logik:</strong> Berechnung der Pauschalanrechnung nach dem offiziellen Wasserfall-Prinzip (Wahlbereich > Fokusbereich > Pflichtwahlbereich).</li>
    <li><strong>Anrechnungsgrenzen:</strong> Berücksichtigung der Limits für das Austauschsemester (mindestens 16 ECTS, maximal 32 ECTS).</li>
    <li><strong>Sprachnachweis:</strong> Prüfung der Mindestanforderung von 12 ECTS in englischer Sprache.</li>
    <li><strong>Datenschutz:</strong> Die Speicherung aller Eingaben erfolgt ausschließlich lokal auf dem Endgerät des Nutzers in einer <code>studienplan.json</code>.</li>
</ul>

<hr>

<h2>Setup & Installation</h2>
<p>Die Anwendung ist für die lokale Ausführung mittels <strong>Visual Studio Code</strong> und <strong>Python</strong> konzipiert.</p>

<h3>1. Voraussetzungen</h3>
<ul>
    <li>Stellen Sie sicher, dass <strong>Python</strong> auf Ihrem System installiert ist.</li>
    <li>Laden Sie die Dateien <code>app.py</code> und <code>requirements.txt</code> aus diesem Repository herunter und speichern Sie diese in einem gemeinsamen Ordner.</li>
</ul>

<h3>2. Installation der Abhängigkeiten</h3>
<p>Öffnen Sie das Terminal in Visual Studio Code innerhalb Ihres Projektordners und führen Sie folgenden Befehl aus:</p>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>3. Anwendung starten</h3>
<p>Geben Sie im Terminal den folgenden Befehl ein, um die Benutzeroberfläche zu starten:</p>
<pre><code>streamlit run app.py</code></pre>

<p>Die Anwendung öffnet sich daraufhin automatisch in Ihrem Standard-Webbrowser.</p>

<hr>

<blockquote>
    <strong>Rechtlicher Hinweis:</strong> Dies ist ein privates Planungshilfsmittel und steht in keiner offiziellen Verbindung zur Universität St.Gallen. Rechtlich bindend sind ausschließlich die offiziellen Angaben der Universität sowie der persönliche Notenauszug im Compass-Portal.
</blockquote>
