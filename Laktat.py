import json
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default = "browser"
import numpy as np

class Laktat:
    zone_colors = {
        "Zone 1 (unter LT1)": "rgba(173,216,230,0.3)",
        "Zone 2 (LT1 - LT2)": "rgba(255,255,0,0.3)",
        "Zone 3 (über LT2)": "rgba(255,99,71,0.3)",
    }

    @staticmethod
    def csv_Datei_laden(path):
        """Lädt eine CSV-Datei und gibt sie als DataFrame zurück."""
        return pd.read_csv(path)

    @staticmethod
    def schwellenwerte_berechnen(df):
        """Berechnet die Laktatschwellen LT1 und LT2 aus den Daten."""
        Lt1 = df[df["Laktat (mmol/l)"] >= 2].iloc[0]["Leistung (Watt)"]
        Lt2 = df[df["Laktat (mmol/l)"] >= 4].iloc[0]["Leistung (Watt)"]
        return Lt1, Lt2

    @staticmethod
    def laktatzonen_berechnen(df, Lt1, Lt2):
        """Berechnet die Laktatzonen basierend auf LT1 und LT2."""
        def zone(leistung):
            """Bestimmt die Laktatzone basierend auf der Leistung."""
            if leistung < Lt1:
                return "Zone 1 (unter LT1)"
            elif leistung < Lt2:
                return "Zone 2 (LT1 - LT2)"
            else:
                return "Zone 3 (über LT2)"

        df["Laktatzone"] = df["Leistung (Watt)"].apply(zone)
        return df

    @staticmethod
    def Belastung_plot_erstellen(df, Lt1, Lt2):
        """Erstellt ein Plotly-Diagramm mit Laktat und Herzfrequenz über die Leistung. Im Hintergrund werden die Laktatzonen angezeigt."""
        shapes = []
        zone_legend_traces = []

        for zone_name, color in Laktat.zone_colors.items():
            zone_df = df[df["Laktatzone"] == zone_name]
            if not zone_df.empty:
                x0 = zone_df["Leistung (Watt)"].min()
                x1 = zone_df["Leistung (Watt)"].max()
                shapes.append(dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0=x0,
                    x1=x1,
                    y0=0,
                    y1=1,
                    fillcolor=color,
                    line=dict(width=0),
                    layer="below"
                ))

                # Dummy-Trace für Legende
                zone_legend_traces.append(go.Scatter(
                    x=[None], y=[None],
                    mode="markers",
                    marker=dict(size=12, color=color),
                    name=zone_name,
                    showlegend=True
                ))

        fig = go.Figure()

        # Zonenlegende-Traces hinzufügen
        for trace in zone_legend_traces:
            fig.add_trace(trace)

        # Daten-Traces
        fig.add_trace(go.Scatter(
            x=df["Leistung (Watt)"], y=df["Laktat (mmol/l)"],
            name="Laktat", yaxis="y1", mode="lines+markers"
        ))
        fig.add_trace(go.Scatter(
            x=df["Leistung (Watt)"], y=df["Herzfrequenz (bpm)"],
            name="Herzfrequenz", yaxis="y2", mode="lines+markers"
        ))

        fig.update_layout(
            title="Laktat und Herzfrequenz vs. Leistung",
            xaxis=dict(title="Leistung (Watt)"),
            yaxis=dict(title="Laktat (mmol/l)", side="left"),
            yaxis2=dict(title="Herzfrequenz (bpm)", overlaying="y", side="right"),
            shapes=shapes,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )

        return fig

    @staticmethod
    def Erholung_plot_erstellen(df, Lt1, Lt2):
        """Erstellt ein Plotly-Diagramm mit Laktat und Herzfrequenz über die Zeit. Im Hintergrund werden die Laktatzonen angezeigt."""
        shapes = []
        zone_legend_traces = []

        for zone_name, color in Laktat.zone_colors.items():
            zone_df = df[df["Laktatzone"] == zone_name]
            if not zone_df.empty:
                x0 = zone_df["Zeit (min)"].min()
                x1 = zone_df["Zeit (min)"].max()
                shapes.append(dict(
                    type="rect",
                    xref="x",
                    yref="paper",
                    x0=x0,
                    x1=x1,
                    y0=0,
                    y1=1,
                    fillcolor=color,
                    line=dict(width=0),
                    layer="below"
                ))

                # Dummy-Trace für Legende
                zone_legend_traces.append(go.Scatter(
                    x=[None], y=[None],
                    mode="markers",
                    marker=dict(size=12, color=color),
                    name=zone_name,
                    showlegend=True
                ))

        fig = go.Figure()

        # Zonenlegende-Traces hinzufügen
        for trace in zone_legend_traces:
            fig.add_trace(trace)

        # Daten-Traces
        fig.add_trace(go.Scatter(
            x=df["Zeit (min)"], y=df["Laktat (mmol/l)"],
            name="Laktat", yaxis="y1", mode="lines+markers"
        ))
        fig.add_trace(go.Scatter(
            x=df["Zeit (min)"], y=df["Herzfrequenz (bpm)"],
            name="Herzfrequenz", yaxis="y2", mode="lines+markers"
        ))

        fig.update_layout(
            title="Laktat und Herzfrequenz vs. Zeit",
            xaxis=dict(title="Zeit (min)"),
            yaxis=dict(title="Laktat (mmol/l)", side="left"),
            yaxis2=dict(title="Herzfrequenz (bpm)", overlaying="y", side="right"),
            shapes=shapes,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )

        return fig

    @staticmethod
    def Trainingsbereiche_berechnen(Lt1, Lt2):
        """Berechnet die empfohlenen Trainingsbereiche basierend auf LT1 und LT2."""
        delta = Lt2 - Lt1
        return {
            "Regenerativ": f"< {Lt1:.0f} Watt",
            "GA1": f"{Lt1:.0f} - {Lt1 + 0.4 * delta:.0f} Watt",
            "GA2": f"{Lt1 + 0.4 * delta:.0f} - {Lt1 + 0.9 * delta:.0f} Watt",
            "WSA": f"> {Lt1 + 0.9 * delta:.0f} Watt"
        }

    @staticmethod
    def Trainingsbereiche_HF_plot(df, Lt1, Lt2):
        """Erstellt ein Balkendiagramm der Trainingsbereiche auf Basis interpolierter Herzfrequenz. Dabei wird auf der x-Achse die Herzfrequenz und auf der y-Achse die Trainingsbereiche angezeigt."""
        # Berechnung der HF-Werte an Laktatschwellen
        hf_interp = np.interp(
            [Lt1, Lt1 + 0.4 * (Lt2 - Lt1), Lt1 + 0.9 * (Lt2 - Lt1), Lt2],
            df["Leistung (Watt)"],
            df["Herzfrequenz (bpm)"]
        )
        HF1, HF_40, HF_90, HF2 = hf_interp

        zonen = {
            "Regeneratives Training": (0, HF1),
            "Grundlagenausdauer 1": (HF1, HF_40),
            "Grundlagenausdauer 2": (HF_40, HF_90),
            "Wettkampfspezifische Ausdauer": (HF_90, HF2 + 5)  # kleiner Puffer
        }

        farben = {
            "Regeneratives Training": "lightblue",
            "Grundlagenausdauer 1": "green",
            "Grundlagenausdauer 2": "yellow",
            "Wettkampfspezifische Ausdauer": "firebrick"
        }

        fig = go.Figure()
        for zone, (x0, x1) in zonen.items():
            fig.add_trace(go.Bar(
                x=[x1 - x0],
                y=[zone],
                base=x0,
                orientation='h',
                marker_color=farben[zone],
                hovertemplate=f"{zone}: {x0:.0f}–{x1:.0f} bpm<extra></extra>"
            ))

        # Trennlinien für LT1 und LT2
        fig.add_vline(x=HF1, line=dict(color="black", dash="dash"), annotation_text="LT1", annotation_position="top left")
        fig.add_vline(x=HF2, line=dict(color="black", dash="dash"), annotation_text="LT2", annotation_position="top right")

        # es soll nur die Grenzwerte der Herzfrequenz angezeigt werden, was die Ablese vereinfacht
        fig.update_layout(
            title="Trainingsbereiche basierend auf Herzfrequenz",
            xaxis=dict(
                title="Herzfrequenz (bpm)",
                tickmode="array",
                tickvals=[round(HF1), round(HF_40), round(HF_90), round(HF2)],
                ticktext=[f"{round(HF1)}", f"{round(HF_40)}", f"{round(HF_90)}", f"{round(HF2)}"]
            ),
            yaxis_title="",
            barmode='stack',
            height=300,
            showlegend=False
        )

        return fig




    @classmethod
    def Analyse_durchführen(cls, csv_path):
        """Führt die gesamte Analyse durch: CSV laden, Schwellenwerte berechnen, Laktatzonen bestimmen und Diagramm erstellen."""
        df = cls.csv_Datei_laden(csv_path)
        Lt1, Lt2 = cls.schwellenwerte_berechnen(df)
        df = cls.laktatzonen_berechnen(df, Lt1, Lt2)
        fig = cls.plot_erstellen(df, Lt1, Lt2)
        trainingsbereiche = cls.trainingsbereiche_berechnen(Lt1, Lt2)

        return {
            "lt1": Lt1,
            "lt2": Lt2,
            "fig": fig,
            "trainingsbereiche": trainingsbereiche,
            "df": df
        }

    @staticmethod
    def Laktatabbau(df):
        """Berechnet den durchschnittlichen Laktatabbau während der Erholungsphase."""
        df = df.copy()
        
        start_laktat = df["Laktat (mmol/l)"].iloc[0]
        end_laktat = df["Laktat (mmol/l)"].iloc[-1]
        start_zeit = df["Zeit (min)"].iloc[0]
        end_zeit = df["Zeit (min)"].iloc[-1]
        
        gesamtdauer = end_zeit - start_zeit
        
        if gesamtdauer <= 0:
            return None
        
        abbau_rate = (start_laktat - end_laktat) / gesamtdauer
        return abbau_rate
