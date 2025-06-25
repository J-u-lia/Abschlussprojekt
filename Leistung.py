import json
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"
import numpy as np


class Leistung:
    zone_colors = {
        "Zone 1": "rgba(173,216,230,0.3)",
        "Zone 2": "rgba(144,238,144,0.3)",
        "Zone 3": "rgba(255,255,0,0.3)",
        "Zone 4": "rgba(255,165,0,0.3)",
        "Zone 5": "rgba(255,99,71,0.3)",
    }

    def __init__(self, csv_path_or_file):
        """ Initialisiert die Klasse mit den Daten aus der CSV-Datei.
        """
        self.df = self.csv_Datei_laden(csv_path_or_file)
        self.df["Zeit"] = np.arange(len(self.df))
        self.HR_max = self.df["Herzfrequenz (bpm)"].max()
        self.df = self._add_zonen()
        self.df = self._add_stufen()

    def _add_zonen(self):
        """ Fügt die Zonen zur DataFrame hinzu, basierend auf der maximalen Herzfrequenz. Diese Funktion nutzt die Methode Zonen_definieren, um die Zonen zu berechnen.
        Die Zonen werden in der DataFrame als neue Spalte "Zone" hinzugefügt.
        Eingabe: Keine
        Rückgabe: DataFrame mit einer neuen Spalte "Zone", die die Zonen basierend auf der Herzfrequenz enthält.
        """
        return self.Zonen_definieren()

    def _add_stufen(self):
        """ Fügt die Stufen zur DataFrame hinzu, basierend auf der Leistung. Diese Funktion nutzt die Methode Stufen_definieren, um die Stufen zu berechnen.
        Die Stufen werden in der DataFrame als neue Spalte "Stufe" hinzugefügt.
        Eingabe: Keine
        Rückgabe: DataFrame mit einer neuen Spalte "Stufe", die die Stufen basierend auf der Leistung enthält.
        """
        return self.Stufen_definieren()

    @staticmethod
    def csv_Datei_laden(path_or_file):
        """ Lädt eine CSV-Datei und gibt sie als DataFrame zurück. 
        Diese Funktion nimmt entweder einen Dateipfad oder ein Dateihandle entgegen und liest die CSV-Daten ein.
        Eingabe: path_or_file - Pfad zur CSV-Datei oder Dateihandle
        Rückgabe: DataFrame mit den geladenen Daten.
        Wenn der Pfad ungültig ist oder die Datei nicht gefunden wird, wird eine Fehlermeldung ausgegeben.
        """
        return pd.read_csv(path_or_file)

    def Zonen_definieren(self):
        """ Definiert die Zonen basierend auf der Herzfrequenz. 
        Diese Funktion erstellt eine neue Spalte "Zone" in der DataFrame, die die Zone basierend auf der Herzfrequenz angibt.
        Eingabe: Keine
        Rückgabe: DataFrame mit einer neuen Spalte "Zone", die die Zonen basierend auf der Herzfrequenz enthält.
        """
        def get_zone(hr):
            """ Bestimmt die Zone basierend auf der Herzfrequenz. 
            Diese Funktion nimmt die Herzfrequenz als Eingabe und gibt die entsprechende Zone zurück.
            Eingabe: hr - Herzfrequenz in bpm
            Rückgabe: String, der die Zone angibt (z.B. "Zone 1", "Zone 2", etc.)
            """
            if hr < 0.6 * self.HR_max:
                return "Zone 1"
            elif hr < 0.7 * self.HR_max:
                return "Zone 2"
            elif hr < 0.8 * self.HR_max:
                return "Zone 3"
            elif hr < 0.9 * self.HR_max:
                return "Zone 4"
            else:
                return "Zone 5"

        df = self.df.copy()
        df["Zone"] = df["Herzfrequenz (bpm)"].apply(get_zone)
        return df

    def Stufen_definieren(self):
        """ Definiert die Stufen basierend auf der Leistung.
        Diese Funktion erstellt eine neue Spalte "Stufe" in der DataFrame, die die Stufe basierend auf der Leistung angibt.
        Eingabe: Keine
        Rückgabe: DataFrame mit einer neuen Spalte "Stufe", die die Stufen basierend auf der Leistung enthält.
        Die Stufen werden durch Änderungen in der Leistung definiert, wobei eine Änderung von mehr als 5 Watt zwischen aufeinanderfolgenden Messungen eine neue Stufe einleitet.
        Die erste Stufe beginnt bei 0.
        """
        df = self.df.copy()
        stufe = 0
        stufen_liste = [0]

        for i in range(1, len(df)):
            if abs(df.loc[i, "Leistung (Watt)"] - df.loc[i - 1, "Leistung (Watt)"]) > 5:
                stufe += 1
            stufen_liste.append(stufe)

        df["Stufe"] = stufen_liste
        return df

    def shapes_definieren(self, spalte, farben_dict):
        """ Erstellt Hintergrundformen für die Zonen im Plot, basierend auf der angegebenen Spalte und den Farben im Dictionary.
        Diese Funktion nimmt eine Spalte und ein Dictionary mit Farben als Eingabe und gibt eine Liste von Formen zurück, die im Plotly-Diagramm verwendet werden können, um die Zonen visuell darzustellen.
        Eingabe: spalte - Name der Spalte, die die Zonen angibt (z.B. "Zone")
        farben_dict - Dictionary, das die Farben für jede Zone angibt, z.B. {"Zone 1": "red", "Zone 2": "blue", ...}
        Rückgabe: Liste von Formen, die im Plotly-Diagramm verwendet werden können, um die Zonen darzustellen.
        Die Formen sind Rechtecke, die den Bereich der jeweiligen Zone im Diagramm abdecken.
        """
        df = self.df
        shapes = []
        current = df.iloc[0][spalte]
        start = 0

        for i in range(1, len(df)):
            if df.iloc[i][spalte] != current:
                shapes.append(dict(
                    type="rect",
                    xref="x", yref="paper",
                    x0=start, x1=i,
                    y0=0, y1=1,
                    fillcolor=farben_dict.get(current, "rgba(200,200,200,0.2)"),
                    line=dict(width=0),
                    layer="below"
                ))
                start = i
                current = df.iloc[i][spalte]

        # letzte Zone hinzufügen
        shapes.append(dict(
            type="rect",
            xref="x", yref="paper",
            x0=start, x1=len(df),
            y0=0, y1=1,
            fillcolor=farben_dict.get(current, "rgba(200,200,200,0.2)"),
            line=dict(width=0),
            layer="below"
        ))
        return shapes

    def stufen_Hintergrund(self):
        """
        Diese Funktion erstellt Hintergrundformen für die Stufen im Plot, die die Form einer Treppe haben. Damit kann die
        Stufenstruktur visuell hervorgehoben werden.
        Diese Funktion analysiert die DataFrame und erstellt Rechtecke, die den Bereich jeder Stufe abdecken.
        Die Rechtecke sind in einem einheitlichen Blau gehalten, um die Stufen klar zu unterscheiden.
        Die Stufen werden durch Änderungen in der "Stufe"-Spalte der DataFrame definiert.
        Die erste Stufe beginnt bei 0 und jede Änderung in der Stufe wird durch ein Rechteck dargestellt.
        Die Höhe der Rechtecke entspricht der Leistung (in Watt) am Ende jeder Stufe.
        Eingabe: Keine
        Rückgabe: Liste von Formen, die im Plotly-Diagramm verwendet werden können, um die Stufen darzustellen.
        Jede Form ist ein Rechteck, das den Bereich der jeweiligen Stufe im Diagramm abdeckt.
        """
        df = self.df
        shapes = []
        current_stufe = df.iloc[0]["Stufe"]
        current_power = df.iloc[0]["Leistung (Watt)"]
        start = 0

        for i in range(1, len(df)):
            if df.iloc[i]["Stufe"] != current_stufe:
                end = i
                leistung = df.iloc[i - 1]["Leistung (Watt)"]
                shapes.append(dict(
                    type="rect",
                    xref="x", yref="y",
                    x0=start, x1=end,
                    y0=0, y1=leistung,
                    fillcolor="rgba(30,144,255,0.3)",  # einheitliches Blau
                    line=dict(width=0),
                    layer="below"
                ))
                start = i
                current_stufe = df.iloc[i]["Stufe"]

        # letzte Stufe
        leistung = df.iloc[-1]["Leistung (Watt)"]
        shapes.append(dict(
            type="rect",
            xref="x", yref="y",
            x0=start, x1=len(df),
            y0=0, y1=leistung,
            fillcolor="rgba(30,144,255,0.3)",
            line=dict(width=0),
            layer="below"
        ))

        return shapes


    def plot_herzfrequenz(self, mode="zonen"):
        """ Erstellt ein Plotly-Diagramm für den Herzfrequenzverlauf mit optionalen Zonen oder Stufen. Dabei gibt es zwei Modis, einmal den Modus "zonen" und einmal den Modus "stufen".
        Der Modus "zonen" zeigt die Herzfrequenz in verschiedenen Zonen, während der Modus "stufen" die Herzfrequenz in verschiedenen Stufen anzeigt.
        Die Zonen und Stufen werden durch unterschiedliche Farben im Hintergrund hervorgehoben.
        Eingabe: mode - String, der den Modus angibt ("zonen" oder "stufen")
        Rückgabe: Plotly-Figur mit dem Herzfrequenzverlauf, der Leistung und den entsprechenden Zonen oder Stufen.
        Wenn der Modus "zonen" gewählt wird, werden die Zonen im Hintergrund angezeigt und die Legende zeigt die Farben der Zonen an.
        Wenn der Modus "stufen" gewählt wird, werden die Stufen im Hintergrund angezeigt und die Legende zeigt die Stufen an.
        Wenn ein ungültiger Modus angegeben wird, wird ein einfaches Liniendiagramm ohne Zonen oder Stufen erstellt.
        Die X-Achse zeigt die Zeit in Sekunden, die Y-Achse zeigt die Herzfrequenz in bpm und die Leistung in Watt.
        Die Herzfrequenz wird in rot und die Leistung in schwarz dargestellt.
        """
        df = self.df
        if mode == "zonen":
            shapes = self.shapes_definieren("Zone", self.zone_colors)
            title = "Herzfrequenz mit Zonen"
        elif mode == "stufen":
            # Farbcodierung für Stufen, dynamisch basierend auf der Anzahl der Stufen
            stufenzahl = df["Stufe"].nunique()
            shapes = self.stufen_Hintergrund()
            title = "Herzfrequenz mit Stufen"
        else:
            shapes = []
            title = "Herzfrequenzverlauf"

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Zeit"], y=df["Herzfrequenz (bpm)"], mode="lines", name="Herzfrequenz", line=dict(color="red")))
        fig.add_trace(go.Scatter(x=df["Zeit"], y=df["Leistung (Watt)"], mode="lines", name="Leistung", line=dict(color="black")))
        # Legende für die Zonen
        if mode == "zonen":
            for zone, color in self.zone_colors.items():
                fig.add_trace(go.Scatter(
                    x=[None], y=[None], mode='markers',
                    marker=dict(size=10, color=color),
                    legendgroup=zone, showlegend=True, name=zone
                ))

        fig.update_layout(
            title=title,
            xaxis_title="Zeit (s)",
            yaxis_title="Wert",
            shapes=shapes,
            legend=dict(title="Legende", itemsizing="constant")
        )

        return fig

    def Werte_berechnen(self):
        """ Berechnet verschiedene Leistungskennzahlen aus den Daten, welche für die Analyse relevant sind.
        Diese Funktion berechnet den durchschnittlichen und maximalen Leistungswert, die Zeit in jeder Zone, die durchschnittliche Herzfrequenz pro Zone und die durchschnittliche Leistung pro Zone.
        Zusätzlich werden die durchschnittlichen Herzfrequenz- und Leistungswerte pro Stufe berechnet.
        Eingabe: Keine
        Rückgabe: Dictionary mit den berechneten Werten:
            - mean_power: Durchschnittliche Leistung in Watt
            - max_power: Maximale Leistung in Watt
            - zeit_pro_zone: Zeit in jeder Zone in Sekunden
            - hf_pro_zone: Durchschnittliche Herzfrequenz pro Zone
            - leistung_pro_zone: Durchschnittliche Leistung pro Zone
            - stufenwerte: DataFrame mit durchschnittlicher Herzfrequenz und Leistung pro Stufe
        """
        df = self.df

        mean_power = df["Leistung (Watt)"].mean()
        max_power = df["Leistung (Watt)"].max()

        # Zeit in Zone
        zeit_in_zonen = df["Zone"].value_counts().rename("Zeit in Sekunden")

        # Durchschnittswerte pro Zone
        hf_pro_zone = df.groupby("Zone")["Herzfrequenz (bpm)"].mean().round(1)
        leistung_pro_zone = df.groupby("Zone")["Leistung (Watt)"].mean().round(1)

        # Durchschnittswerte pro Stufe
        stufen_df = df.groupby("Stufe").agg(
            durchschnitts_HF=("Herzfrequenz (bpm)", "mean"),
            durchschnitts_Leistung=("Leistung (Watt)", "mean")
        ).round(1)

        return {
            "mean_power": mean_power,
            "max_power": max_power,
            "zeit_pro_zone": zeit_in_zonen,
            "hf_pro_zone": hf_pro_zone,
            "leistung_pro_zone": leistung_pro_zone,
            "stufenwerte": stufen_df
        }
