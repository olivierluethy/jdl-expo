# JDL Expo
## Installation - Einrichtung

```
sudo apt update
```
```
sudo apt install python3-venv
```
```
python3 -m venv venv
```
```
source /home/random_user/Documents/jdl-expo/venv/bin/activate
```
```
(venv) random_user@random-user-MS-7C37:~/Documents/jdl-expo$ python3 main.py
```
```
(venv) random_user@random-user-MS-7C37:~/Documents/jdl-expo$ deactivate
```
```
pip install -r requirements.txt
```

## Vorgehensweisen - Schritten der Bearbeitung und Erkenntnisse
Dieses Repo dient als basis orientierung für die Skripts die wir für TuneVote dazu verwenden, prinzipiell unter befugnis der Verarbeitung der YouTube Video Daten. Die Orientierung basiert hierbei auf die Abnutzung von YouTube Data API um sich dem Abzuwenden, da dessen Benutzung sich als unfakultärisch und sehr unzuverlessig erweisst aufgrund der gegebenen Einschränkungen.

Damit alle Daten nun korrekt geholt und gemäss unseren Hingaben verarbeiten und für TuneVote zunutzen machen wollen, war zuerst der erste Anhieb dies mittels [YouTube AutoScript](https://github.com/BaskLash/youtube_autoscript) zu lösen. Diese Lösung basiert auf die Erkenntniss der Datenabgreifung über die allgemeine Webseite unter Benutzung und einwand der Browser Dev Tools.

Aber bevor ich diese ganzen Channels überhaupt abgreifen konnte wurde schon eine ältere Version des [youtube_autoscripts](https://github.com/BaskLash/youtube_autoscript/blob/4cf17def58099f538881cb5a7e15d78db930b3ad/main.js) genau dafür missbraucht um ganz viele Videos pro YouTube Kanal zu scrappen. Also ich hatte schon über 30 - 40k an Video Songs. Was ich aber noch ergänzlich haben wollte, ist das man für TuneVote auch noch die Künstler sieht, also wie Künstlerstatistiken aufbereiten kann, dass wenn z.B. ein Song gibt über dem oft am Tag gevotet wird, dann soll nicht nur der Song auf der HomePage von TuneVote angezeigt werden, sondern auch der Künstler an sich. Aber den Künstler habe ich schlicht nicht separat erfassen, was ein erdeutender Denkfehler zu sein scheinen mag.

Was ich also nicht machen wollte, ist durch jeden YouTube Channel den ich im vermuteten masse im Browserverlauf hatte, den separat abzufragen. Ich will gehabenes Material wiederverwenden. Also was habe ich gemacht, ich habe die youtube_video_cache tabelle exportiert und zwar das ganze, und danach wollte ich das Python mir alle YOuTube Channels darüber extrahiert. Aber das hätte gänzlich einfach unheimlich lange gedauert. Also was habe ich mir gedacht, nun ja die einzige Abgrenzung ist ja, das Pro Creator mindestens begutachtliche 30 - 100 - vielleicht gar 500 für nur ein und den selben Creator zu sein schein mag. Also habe ich geschaut wo haben sie den womöglich von dessen der Videobetitelung des Creators etwas gemeinsam worauf sich die Gemeinsamkeit aufstössig auf eine Referenz zum creator nachstellen lässt. Ein bekanntes musster war "[Künstler - Musiktitel]" oder "[Künstler, Musiktitel]" also es gab sehr viele Auffschlüsse die sich über die betitelung als auffschlüsselig genug empfundend wirkten um daraus eine Vereinheitlichung zu bilden, sodass so viel Musik wie möglich von nur einem Creator wegfählt, aber es immer mindestens einen Song des Creators gibt. Daraufhin konnte ich von 29364 runter auf knapp etwas mehr als 9000 kommen, was eine beachtliche Verkleinerung der gesamten Insert liste an und für sich darstellt. Danach war das Ziel, dass Pro insert, also pro Videolink der Channel Creator ermittelt wird mit ChannelId und danach der aufbereitung einer blockierten Redundanz auf ChannelIds sodass man dann nie mehr als ein Creator aus der Liste herstellen konnte und somit eine vereinheitlich von allen Creators ohne Redundanz hergeleitet hat. 

Diese Lösung beschreibt inzufolgedessen folgende Vorteile erfahrungsgemäss:
- Alle Daten eines YouTube Kanals insbesondere auf hinblick auf dessen populärsten Beiträge lassen sich in kürzester Zeit sehr viele Videos entnehmen und alle benötigten Daten werden schnell über das Frontend abgegriffen.

Aber auch folgende Schwerwiegende Nachteile:
- Für knapp 300 - 1k vereinzelte Künstler müsste jeder Künstlerchannel auf YouTube separat aufgerufen werden, müsste sich zu den Videos widmen und danach nach beliebtheit sortieren, danach möglichst weit runterscrollen bis ab einer abgränzung wenn es ein sehr populärer künstler ist ab weniger als einer Million aufrufe und danach alle Videos von diesem Bereich abfangen.
- Es werden nicht alle Videos eines Künstlers abgefangen
- Der Aufwand nur schon für die Vorbereitung die zur Ausführung des Scriptes erfordert ist empfindend lächerlich

Als nächster Approach war es, es mittels Selenium zu probieren indem python selbst den Browser steuert und diesen Weg für uns diese Steps ausführt.

Aber auch das folgt mit nachteilen:
- Es ist verbraucht so viele unnötige Resourcen die gespart werden können
- Möglichst viele Steps müssten dabei schon weit voraus vorangedacht sein und ist daher ein sehr aufwändig ansetzbarer Prozess
- Wird sehr viel Ram und CPU verbrauchen

Also kam ich plötzlich auf yt_dlp wo das mächtigste Python Library ist, klar beständig zum Web Scrapping von YouTube Video Kanälen.

Der Prozess nur zum holen der Videos von einem Kanal ging extrem schnell, jedoch fehlten die Videodauer und was einem erst am Schluss aufgefallen wäre ist, dass wenn es alle Videos aus dem /videos URL bereich geholt hat, dass es nie auch die neusten Videos auf dem kanal miteinbezieht sondern immer die etwas älteren, obwohl keine Filterung die Neusten Videos Extrahierung eingrenzen würde.

Darüber hinaus wurde ich dann über einen Trick von ChatGPT aufmerksam wer darauf hingedeutet hat, dass sich aus einem YouTube Kanal eine channelId herauslesen lässt. Diese ChannelId gelte als channelidentifikation zu YouTube kanelen um an sich daraus, wenn es sich bei einem Kanal um einen Musikkanal handeln würde die URL so aufgebaut ist:
https://www.youtube.com/channel/UC0C-w0YjGpqDXGB8IHb662A

Dort sieht man das sich die Channel ID Direkt in der URL befindet. Aber das lustige dabei ist, entnehme man die ID von einem Kanal also "UC0C-w0YjGpqDXGB8IHb662A" und entnehme man die ersten zwei Zeichen
"UC" und ersetzt das "C" durch ein "U" so ergibt sich "UU" und somit "UU0C-w0YjGpqDXGB8IHb662A". Wenn man diese Umwandlung in den Link einer Playlist einfügt:
https://www.youtube.com/playlist?list=UU0C-w0YjGpqDXGB8IHb662A

Gelangt man auf eine Playlistseite, auf die Man über die Kanalpage des Künstlers niemals kommen würde. Doch das Spezielle gerade an dem ist, dass sich dort wirklich alle Videos des Künstlers auf einmal befinden. Versucht man dies mittels der yt_dlp-Python Library zu Web Scrapen und die daten zu extrahieren, kommt man nach dessen Extrahierung auf genau viele Videos wie auf der Playlist angezeigt.
Das heisst, es wird von dieser Playlist Page wirklich alles geholt. Und diese Extrahierung erfolgt realtiv zügig.

Nur ist das einzige Problem, das dafür die Durations nicht mitgehandhabt werden, da man für die Beabsichtigung dieser Durations noch zusätzlich jedes Einzelnes Video über die Python Libarary abfragen muss um über die daraus gewonnenen Metadaten die Duration von diesem Video herausziehen zu können.

Nur wenn man diese separate Abfrage nun mal halt jedes mal macht, dauert das umso mehr sehr viel länger den diese Abfrage führt das Skript jedes mal separat pro extrahiertem Video von dieser Playlist des künstlers separat ab was total resourcen schädigend ist und zudem noch auch für mich viel zu lange dauert.

Also wurde danach gegebenenermassen versucht dies über die httpx asyncio Schnittstelle über separate HTTP request das JSON namens ytInitialData zu holen und auszuwerten. Der Punkte der dafür sich ausgesprochen hat war, dass sich angeblich in diesem Objekt ein JSON befinden solle, worin sich alle Videos aus dem Frontend holen lassen. Ganz erklinglich hat es für mich so getönt, also es wurde so beschrieben, dass YouTube für das Frontend dieses JSON lädt und über dieses JSON, alle Daten für das Frontend aufbereitet. Dies erklang für mich sehr komisch, weil warum das so machen und es nicht ganz einfach über die DB holen lassen? Danach ging es mehr so darum, dass verarbeiten, filtern und das verarbeitbare verarbeitbar für uns für unsere Bedürfnisse so zu befugen, da sich der Vorteil daraus hätte erschliessen können, dass man mittels Python sehr schnell HTTP Request pro bestimmten Künstler ausführen kann, ihn kleine Anweisungen oberflächlich bezüglich klicks auf Buttons zur Filterung zur Gewinnung der populäreren Videos und somit, pro Künstler weniger Songs zu speichern, aber dafür die populärsten, so am schnellsten arbeiten + das Durations problem auch auf den Grund zu gehen, da sich im Frontend die Dauer immer am Video repräsentieren lässt. Natürlich logisch, damit man auch weiss im Vorgang, wie lange ein YouTube Video geht bevor man es sich anschaut.

Doch das Extrahieren, Verarbeiten und Konservieren der Inhalte über das JSON schien eine unmögliche Sache zu sein, da das Skript am Anfang keine korrekten Requests ausführen konnte, da es Google als zu wenig menschlich kommender Requests zusehendsten empfunden hat. Ein Umgehweg der auch funktioniert hatte, war selbst ein Inkognito Browserfenster zu öffnen, dort youtube aufzurufen und dann bei den Dev Tools unter den Cookies das Cookie namens "SOCS" zu kopieren und für den Request Handler für YouTube zu verwenden als täuschungsmanöver das wir ein echter mensch seien aufgrund dieser Gültigkeitswirkung von diesem Cookie den wir einfach verwendet haben für diesen Request. Aber dann entstand das nächste unabsehbare Problem. Dieses JSON mit den ganzen Inhalten die dieses JSON in sich befand konnten nie richtig abgeholt und verarbeitet werden, da man nicht wusste wie man das macht, öffentliche Bekundgebungen sowie foren keine ansatzpunkte zu Wege nach Rom führten und das selbst die Aktuellsten Vorgehensweisen also mit aktuell stammend aus dem Jahr 2023 - 2024 sich der HTML Context von YouTube wieder stark zu verändern haben scheint und es genau deshalb nicht möglich gewesen schein mag, überhaupt korrekte schlüsse bei der Abgreifung der Daten dieses JSONs beabsichtigt möglich gewordend zu sein scheint. Und das spezielere war an dieser unscheinbar doch etwas sehr komischen sache erdachte mir dann so, als ich selbst einen einblick in dieses JSON selbst geworfen hatte. Es schien erwartungsgemäss aufgrund der vielen wegen des Channels zu ladenden Videos zu sein, aber als ich nach konkreten Vidoes gesucht habe z.B. nach dem aller ersten konnte ich dessen Titel dort niergends finden sowie auch weitere Titeln. Das schein für mich sehr verwerflich und daher entschloss ich dieser Anweisung dem gegenüber weniger Wert zu schänken.

Nun blieb es nur noch weiterhin an jt_dlp-Python Library zu glauben und dessen Geschwindigkeit mittels zunehmeneder Threads zu beschleunigen. Und nach einer beachtlich getätigten Einstellung von bis auf 30 Threads schien das Script echt schnell extrem Viele YOuTube VIdeos von einem YouTube Kanal Playlist runterzuziehen. Nur shcon das zuschauen bei dessen vorgehen erschien mir einen zutiefst sehr erstaunenden Eindruck mir gegenüber im Kopf einzubringen.