"""Welcome to Reflex! This file outlines the steps to create a basic app."""
from rxconfig import config
import time
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal
import reflex as rx
from typing import List
import plotly.graph_objs as go

options: List[str] = ["LPF", "HPF", "BPF"]
class RadioState(rx.State):
    text: str = "No Selection"

class DynamicFormState(rx.State):
    form_data: dict = {}
    form_fields: list[str] = [
        "sampling_time",
        "minX",
        "maxX",
    ]
    
    @rx.cached_var
    def form_field_placeholders(self) -> list[str]:
        return [
            " ".join(
                w.capitalize() for w in field.split("_")
            )
            for field in self.form_fields
        ]

    def add_field(self, form_data: dict):
        new_field = form_data.get("new_field")
        if not new_field:
            return
        field_name = (
            new_field.strip().lower().replace(" ", "_")
        )
        self.form_fields.append(field_name)

    def handle_submit(self, form_data: dict):
        self.form_data = form_data
        print(self.form_data.keys())

class State(rx.State):
    number: float
    password: str
    number_text: str
    password_text: str
    form_data: dict = {}
    data = [{"x": 0, "value": 0}]
    fig = go.Figure()

    def check_filter(self, form_data: dict):
        self.form_data = form_data
        self.keys = list(self.form_data.keys())
        print(self.form_data.keys())
        Xtype = self.form_data[self.keys[0]]
        dt = self.form_data[self.keys[1]]
        Xfl = self.form_data[self.keys[2]]
        Xfh = self.form_data[self.keys[3]]
        XWn, XN = self.get_filterparam(dt, Xfl, Xfh, self.get_filtertype(Xtype))
        Xb, Xa = signal.butter(XN, XWn, self.get_filtertype(Xtype), True)
        Xw, Xh = signal.freqs(Xb, Xa)

        fn = 1.0/(2.0*float(dt))/2.0
        self.fig = go.Figure()#ここで再定義をしないとなぜか結果が出ない？リセットされる？

        # Adding X, Y, Z traces
        self.fig.add_trace(go.Scatter(x=Xw*fn, y=20*np.log10(abs(Xh)), mode='lines', name='Range_X'))

        # Adding Nyquist line
        print(fn)
        self.fig.add_shape(type="line", x0=(fn*1000), y0=-40, x1=(fn*1000), y1=10, line=dict(color="Red", width=2, dash="dot"))

        # Setting layout properties
        self.fig.update_layout(
            title='Butterworth filter frequency response',
            xaxis_title='Frequency [Hz]',
            yaxis_title='Amplitude [dB]',
            xaxis=dict(range=[0, 80]),
            yaxis=dict(range=[-40, 10]),
            legend_title="Filter Type",
            plot_bgcolor="white"
        )

    def get_filtertype(self, rb):
        if rb == "LPF":
            ftype1 = "lowpass"
        elif rb == "HPF":
            ftype1 = "highpass"
        else:
            ftype1 = "bandpass"
        return ftype1

    def get_filterparam(self, dt, fl, fh, filtertype):
        dt = float(dt)
        fn = 1.0/(2.0*dt)/2.0
        if filtertype == "bandpass":
            Wn = [float(fl)/fn, float(fh)/fn]
            N=3
        elif filtertype == "lowpass":
            Wn = float(fh)/fn
            N=6
        else:
            Wn = float(fl)/fn
            N=6
        return Wn, N 

def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Filter_Check"),
            rx.divider(),
            dynamic_form(),
        )
    )

def dynamic_form() -> rx.Component:
    return rx.vstack(
        rx.form(
            rx.vstack(
                rx.badge(RadioState.text, color_scheme="green"),
                rx.radio_group(
                    options,
                    default_value="LPH",
                    default_checked=True,
                    on_change=RadioState.set_text,
                ),
                rx.foreach(
                    DynamicFormState.form_fields,
                    lambda field, idx: rx.input(
                        placeholder=DynamicFormState.form_field_placeholders[
                            idx
                        ],
                        name=field,
                    ),
                ),
                rx.button("Submit", type_="submit"),
            ),
            on_submit=State.check_filter,
            reset_on_submit=True,
        ),
        rx.divider(),
        rx.heading("Results"),
        rx.text(State.form_data.to_string()),
        rx.plotly(data=State.fig, height="400px")
        )

# Add state and page to the app.
app = rx.App(state=State)
app.add_page(index)
app.compile()
