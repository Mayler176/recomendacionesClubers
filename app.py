from streamlit_elements import elements, mui, nivo
import streamlit as st

def plot_preference_pie_nivo(client_id):
    preferencias = get_client_preferences(client_id)
    if preferencias is None or preferencias.empty:
        st.warning("Este cliente no tiene preferencias registradas.")
        return

    # Renombrar categorías según lo solicitado
    renombradas = preferencias.rename({
        "bebidas": "bebidas alcoholicas",
        "categoria_2": "bebidas",
        "categoria_8": "otros"
    })

    # Truncar valores a 2 decimales y mantenerlos como numéricos (no strings)
    pie_data = [
        {
            "id": cat,
            "label": cat,
            "value": round(val * 100, 2),  # CORRECTO: numérico, no string
            "color": f"hsl({(i * 37) % 360}, 70%, 50%)"
        }
        for i, (cat, val) in enumerate(renombradas.items())
    ]

    # Tema oscuro fijo
    dark_theme = {
        "background": "#0e1117",
        "textColor": "#fafafa",
        "tooltip": {
            "container": {
                "background": "#262730",
                "color": "#fff",
                "border": "solid 3px #F0F2F6",
                "border-radius": "8px",
                "padding": 5,
            }
        }
    }

    # Renderizar gráfico con Nivo
    with elements("nivo_pie_chart"):
        with mui.Box(sx={"height": 500}):
            nivo.Pie(
                data=pie_data,
                margin={"top": 100, "right": 100, "bottom": 100, "left": 100},
                innerRadius=0.5,
                padAngle=0.7,
                cornerRadius=3,
                activeOuterRadiusOffset=8,
                borderWidth=1,
                borderColor={"from": "color", "modifiers": [["darker", 0.8]]},
                arcLinkLabelsSkipAngle=0,
                arcLinkLabelsTextColor="#ccc",
                arcLinkLabelsThickness=2,
                arcLinkLabelsColor={"from": "color"},
                arcLabelsSkipAngle=0,
                arcLabelsTextColor="transparent",  # Oculta etiquetas internas
                theme=dark_theme,
                defs=[
                    {
                        "id": "dots",
                        "type": "patternDots",
                        "background": "inherit",
                        "color": "rgba(255, 255, 255, 0.3)",
                        "size": 4,
                        "padding": 1,
                        "stagger": True,
                    },
                    {
                        "id": "lines",
                        "type": "patternLines",
                        "background": "inherit",
                        "color": "rgba(255, 255, 255, 0.3)",
                        "rotation": -45,
                        "lineWidth": 6,
                        "spacing": 10,
                    },
                ],
                fill=[
                    {"match": {"id": renombradas.index[0]}, "id": "dots"},
                    {"match": {"id": renombradas.index[1]}, "id": "lines"},
                    {"match": {"id": renombradas.index[2]}, "id": "dots"} if len(renombradas) > 2 else {},
                ],
                legends=[
                    {
                        "anchor": "bottom",
                        "direction": "row",
                        "translateY": 56,
                        "itemWidth": 100,
                        "itemHeight": 18,
                        "itemTextColor": "#999",
                        "symbolSize": 18,
                        "symbolShape": "circle",
                        "effects": [{"on": "hover", "style": {"itemTextColor": "#fff"}}],
                    }
                ],
            )
