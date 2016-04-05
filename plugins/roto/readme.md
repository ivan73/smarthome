# Roto

Das Plugin errechnet die aktuelle Position des Dachfensters (alternativ der Jalousie / Rolladen) über dessen Laufzeit.
Die Position wird dabei vom Plugin laufend im Positions-Item aktualisiert. Dazu triggert sich das Plugin während der Fahrt selber (mittels Scheduler)
Über das (externe) Setzen des Positions-Item können auch Positionen angefahren werden.

Referenzfahrt:
Beim ersten Start des Plugins wird die Position mit 50% angenommen. (Item wird mit value = 50 auf initialer Wert 50% gesetzt)
Wird das Dachfenster / die Jalousie ganz Auf- oder Zugefahren wird die Position auf roto_time_up oder roto_time_down korrigiert.

# Requirements / Benötigt werden:

Zwei Items für den Jalousie-Taster bzw. Buttons in der Visualisierung für Auf_Ab und Stop_Schrittweise 
Zwei Schaltaktor-Kanäle für ein Roto Dachfenster  (Auf bzw. Ab).

(Alternativ kann auch ein Rolladen mit Jalousieaktor (welcher keine Positionsermittlung hat) angesteuert werden.)

# Configuration

## plugin.conf

Folgende Zeilen sind in die Datei plugin.conf einzutragen:

<pre>
[roto]
    class_name = Roto
    class_path = plugins.roto

</pre>



items.conf
--------------

*roto_plugin(obligatorisch) = active
    Kennzeichnet das Item als Objekt-Item des Roto-Plugins
    Der Wert dieses Attributs muss zwingend "active" sein, damit das Plugin das Item berücksichtigt. 

*type (obligatorisch):
    Datentp des Objekt-Items
    Für das Objekt-Item muss immer der Datentyp "bool" verwendet werden

*eval_trigger (obligatorisch)
    Das Objektitems muss getriggert werden wenn eine Taste (oder Button) gedrückt wird, 
    bzw. wenn eine Position angefahren werden soll
    
*eval (obligatorisch)
    Bei jedem Triggern soll sich der Zustand des Objektitems ändern
    eval = not sh.Dg.Flur.Dachfenster.Roto
    
*roto_up_down (obligatorisch)
    Das Taster-Item, dass überwacht werden soll, muss auf Ebene des Objekt-Items über das Attribut "roto_up_down" angegeben werden.
    Bei einem 0-Signal fährt der Aktor Auf.
    Bei einem 1-Signal fährt der Aktor Ab/Zu.

*roto_stop (obligatorisch)
    Das Taster-Item, dass überwacht werden soll, muss auf Ebene des Objekt-Items über das Attribut "roto_up_down" angegeben werden.
    Wird das Item während der Fahrt geändert:
        Mit einem 0 oder 1 Signal wird die Fahrt gestoppt.
    
    ansonsten:
    Bei einem 0-Signal fährt der Aktor einen Schritt Auf. (Schrittweite einstellbar über roto_time_step)
    Bei einem 1-Signal fährt der Aktor einen Schritt Ab/Zu. (Schrittweite einstellbar über roto_time_step)

*roto_position (0-100)(obligatorisch)
    Das Item, dass überwacht bzw. geschrieben werden soll, muss auf Ebene des Objekt-Items über das Attribut "roto_up_down" angegeben werden.
    Über dieses Item wird die errechnete Position aktualisiert. 
    Wird dieses Item auf einen Wert gesetzt, wird diese Position angefahren.
    
### bei Roto Dachfenster mit Schaltaktoren:
*roto_actor_open (obligatorisch/alternativ)
    Das Item, dass gesetzt werden soll, muss auf Ebene des Objekt-Items über das Attribut "roto_up_down" angegeben werden.
    Aktor - Kanal zum Öffnen des Dachfensters
    Zum Starten des Dachfensters wird der Aktor-Kanal für eine Sekunde eingeschalten. 
    Zum Stoppen der Fahrt wird ein weiterer Impuls mit einer Sekunden gegeben.
*roto_actor_close (obligatorisch/alternativ))
    Das Item, dass gesetzt werden soll, muss auf Ebene des Objekt-Items über das Attribut "roto_up_down" angegeben werden.
    Aktor - Kanal zum Schließen des Dachfensters
    Zum Starten des Dachfensters wird der Aktor-Kanal für eine Sekunde eingeschalten. 
    Zum Stoppen der Fahrt wird ein weiterer Impuls mit einer Sekunden gegeben.
    
### Alternativ bei Jalosieaktoren:
*roto_actor_up_down (obligatorisch/alternativ))
    Das Item, dass gesetzt werden soll, muss auf Ebene des Objekt-Items über das Attribut "roto_up_down" angegeben werden.
    Aktor - Kanal zum Runterfahren bzw. Rauffahren der Jalousie
    Beim Runter fahren wird das Item auf 0 gesetzt
    Beim Rauf fahren wird das Item auf 1 gesetzt

*roto_actor_stop (obligatorisch/alternativ))
    Das Item, dass gesetzt werden soll, muss auf Ebene des Objekt-Items über das Attribut "roto_up_down" angegeben werden.
    Aktor - Kanal zum Stoppen der Jalousie
    Zum Stoppen der Jalousie wird das Item auf 1 gesetzt
    
*roto_time_up (in Sekunden)(optional, default 60 Sekunden)
    max. Fahrzeit beim Auffahren (wird für die Berechnung der Position benötigt)
    
*roto_time_down (in Sekunden)(optional, default 60 Sekunden)
    max. Fahrzeit beim Ab/Zu-Fahren(wird für die Berechnung der Position benötigt)
    
*roto_time_step (in Sekunden)(optional, default 10 Sekunden)
    wird das Dachfenster / Jalousie schrittweise verfahren kann hier die Schrittweite in Sekunden angegeben werden
    
*roto_cycle_time (in Sekunden)(optional, default 5 Sekunden)
    Zeit innerhalb welchem Zeitabstand das Positionsitem während der Fahrt aktualisert wird

# Beispiel

<pre>
# items/example.conf
[Dg]    
    [[Flur]]
        [[[Dachfenster]]]
			[[[[Auf_ab]]]]  # Gruppenadresse des KNX- Taster oder Button in Visu
				type = bool
				visu = yes
				visu_acl = rw
                knx_dpt = 1
				knx_listen = 3/2/114
				enforce_updates = True
			[[[[Lamellenverstellung_stop]]]]    # Gruppenadresse des KNX- Taster oder Button in Visu
				type = bool
				visu = yes
				visu_acl = rw
                knx_dpt = 1
				knx_listen = 3/2/115
				enforce_updates = True
			[[[[Position]]]]    # errechnete Position; beim Setzen dieses Items wird diese Position angefahren 0-100
				type = num
                value = 50      # Initialer Wert 50%
                cache = True
				visu = yes
				visu_acl = rw
                enforce_updates = True
			[[[[Aktor_Zu]]]]  # Schaltaktor für ZuFahren - für Roto Dachfenster!!
				type = bool
				knx_dpt = 1
				knx_send = 4/2/114
               enforce_updates = True
			[[[[Aktor_Auf]]]]  # Schaltaktor für Auffahren - für Roto Dachfenster!!
				type = bool
				enforce_updates = True
				knx_dpt = 1
				knx_send = 4/2/115
            #[[[[Aktor_Auf_ab]]]] # Gruppenadresse des Jalousieaktors
			#	type = bool
			#	enforce_updates = True
			#	knx_dpt = 1
			#	knx_send = 4/2/114
			#[[[[Aktor_stop]]]] # Gruppenadresse des Jalousieaktors
			#	type = bool
			#	enforce_updates = True
			#	knx_dpt = 1
			#	knx_send = 4/2/115
			[[[[Roto]]]]    # Objekt Item / wird für das Plugin benötigt!!
				roto_plugin = active # Kennzeichen für das Plugin
				type = bool # muss bool sein
				eval_trigger = Dg.Flur.Dachfenster.Auf_ab | Dg.Flur.Dachfenster.Lamellenverstellung_stop | Dg.Flur.Dachfenster.Position # Triggern des Items wenn Taster gedrückt wird
				eval = not sh.Dg.Flur.Dachfenster.Roto # wird für das Plugin benötigt
				roto_up_down = Dg.Flur.Dachfenster.Auf_ab # Taster 0 ab ; 1 auf
				roto_stop = Dg.Flur.Dachfenster.Lamellenverstellung_stop # Stop oder 0 Schritt ab ; 1 Schritt auf
				roto_position = Dg.Flur.Dachfenster.Position # aktuelle Position oder Position anfahren 0-100
				roto_actor_up_down = Dg.Flur.Dachfenster.Aktor_Auf_ab # Item GA des Jalousiekators
				roto_actor_stop = Dg.Flur.Dachfenster.Aktor_stop # Item GA des Jalousiekators
                #roto_actor_open = Dg.Flur.Dachfenster.Aktor_Auf  # Item Schaltaktor für Roto Dachfenster!!
				#roto_actor_close = Dg.Flur.Dachfenster.Aktor_Zu # Item Schaltaktor für Roto Dachfenster!!
				roto_time_up = 60 # [Sekunden] max. Fahrzeit beim Auffahren
				roto_time_down = 58 # [Sekunden] max. Fahrzeit beim Ab(Zu)fahren
				roto_time_step = 6 # [Sekunden] Zeit beim Schrittweise fahren
                roto_cycle_time = 5 # [Sekunden] Aktualisierungsintervall des Positionsitems
</pre>

Bei Jalousieaktoren werden die Items "Aktor_Zu" und "Aktor_Auf" auskommentiert werden, und dafür die beiden Items "Aktor_Auf_ab" und "Aktor_stop" aktiviert werden.

<pre>
# items/example.conf

			#[[[[Aktor_Zu]]]]  # Schaltaktor für ZuFahren - für Roto Dachfenster!!
			#	type = bool
			#	knx_dpt = 1
	 		#	knx_send = 4/2/114
			#	enforce_updates = True
			#[[[[Aktor_Auf]]]]  # Schaltaktor für Auffahren - für Roto Dachfenster!!
			#	type = bool
			#	enforce_updates = True
			#	knx_dpt = 1
			#	knx_send = 4/2/115
            [[[[Aktor_Auf_ab]]]] # Gruppenadresse des Jalousieaktors
				type = bool
				enforce_updates = True
				knx_dpt = 1
				knx_send = 4/2/114
			[[[[Aktor_stop]]]] # Gruppenadresse des Jalousieaktors
				type = bool
				enforce_updates = True
				knx_dpt = 1
				knx_send = 4/2/115
			[[[[Roto]]]]    # Objekt Item / wird für das Plugin benötigt!!
				roto_plugin = active # Kennzeichen für das Plugin
				type = bool # muss bool sein
				eval_trigger = Dg.Flur.Dachfenster.Auf_ab | Dg.Flur.Dachfenster.Lamellenverstellung_stop | Dg.Flur.Dachfenster.Position # Triggern des Items wenn Taster gedrückt wird
				eval = not sh.Dg.Flur.Dachfenster.Roto # wird für das Plugin benötigt
				roto_up_down = Dg.Flur.Dachfenster.Auf_ab # Taster 0 ab ; 1 auf
				roto_stop = Dg.Flur.Dachfenster.Lamellenverstellung_stop # Stop oder 0 Schritt ab ; 1 Schritt auf
				roto_position = Dg.Flur.Dachfenster.Position # aktuelle Position oder Position anfahren 0-100
				#roto_actor_up_down = Dg.Flur.Dachfenster.Aktor_Auf_ab # Item GA des Jalousiekators
				#roto_actor_stop = Dg.Flur.Dachfenster.Aktor_stop # Item GA des Jalousiekators
                roto_actor_open = Dg.Flur.Dachfenster.Aktor_Auf  # Item Schaltaktor für Roto Dachfenster!!
				roto_actor_close = Dg.Flur.Dachfenster.Aktor_Zu # Item Schaltaktor für Roto Dachfenster!!
				roto_time_up = 60 # [Sekunden] max. Fahrzeit beim Auffahren
				roto_time_down = 58 # [Sekunden] max. Fahrzeit beim Ab(Zu)fahren
				roto_time_step = 6 # [Sekunden] Zeit beim Schrittweise fahren
                roto_cycle_time = 5 # [Sekunden] Aktualisierungsintervall des Positionsitems
</pre>

