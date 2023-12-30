# -*- coding: utf-8 -*-

#ライブラリの読み込み
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import numpy as np
from scipy import signal

# Your existing filter class goes here

class filter():
    def __init__(self):
        self.type = 0

    def check_filter(self, dt, Xtype, Xfl, Xfh, Ytype, Yfl, Yfh, Ztype, Zfl, Zfh):
        XWn, XN = self.get_filterparam(dt, Xfl, Xfh, self.get_filtertype(Xtype))
        Xb, Xa = signal.butter(XN, XWn, self.get_filtertype(Xtype), True)
        Xw, Xh = signal.freqs(Xb, Xa)
        YWn, YN = self.get_filterparam(dt, Yfl, Yfh, self.get_filtertype(Ytype))
        Yb, Ya = signal.butter(YN, YWn, self.get_filtertype(Ytype), True)
        Yw, Yh = signal.freqs(Yb, Ya)
        ZWn, ZN = self.get_filterparam(dt, Zfl, Zfh, self.get_filtertype(Ztype))
        Zb, Za = signal.butter(ZN, ZWn, self.get_filtertype(Ztype), True)
        Zw, Zh = signal.freqs(Zb, Za)

        fn = 1.0/(2.0*float(dt))/2.0
        fig = go.Figure()

        # Adding X, Y, Z traces
        fig.add_trace(go.Scatter(x=Xw*fn, y=20*np.log10(abs(Xh)), mode='lines', name='Range_X'))
        fig.add_trace(go.Scatter(x=Yw*fn, y=20*np.log10(abs(Yh)), mode='lines', name='Range_Y'))
        fig.add_trace(go.Scatter(x=Zw*fn, y=20*np.log10(abs(Zh)), mode='lines', name='Range_Z'))

        # Adding Nyquist line
        print(fn)
        fig.add_shape(type="line", x0=(fn*1000), y0=-40, x1=(fn*1000), y1=10, line=dict(color="Red", width=2, dash="dot"))

        # Setting layout properties
        fig.update_layout(
            title='Butterworth filter frequency response',
            xaxis_title='Frequency [Hz]',
            yaxis_title='Amplitude [dB]',
            xaxis=dict(range=[0, 80]),
            yaxis=dict(range=[-40, 10]),
            legend_title="Filter Type",
            plot_bgcolor="white"
        )

        return fig

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

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Input(id='input-sampling-time', type='number', value=4.0),
    dcc.RadioItems(id='radio-x-type', options=[{'label': i, 'value': i} for i in ['LPF', 'HPF', 'BPF']], value='LPF'),
    dcc.Input(id='input-min-x', type='number', value=0.1),
    dcc.Input(id='input-max-x', type='number', value=50.0),

    dcc.RadioItems(id='radio-y-type', options=[{'label': i, 'value': i} for i in ['LPF', 'HPF', 'BPF']], value='LPF'),
    dcc.Input(id='input-min-y', type='number', value=0.1),
    dcc.Input(id='input-max-y', type='number', value=50.0),

    dcc.RadioItems(id='radio-z-type', options=[{'label': i, 'value': i} for i in ['LPF', 'HPF', 'BPF']], value='LPF'),
    dcc.Input(id='input-min-z', type='number', value=0.1),
    dcc.Input(id='input-max-z', type='number', value=50.0),

    html.Button('Submit', id='submit-button', n_clicks=0),
    dcc.Graph(id='filter-graph')
])

# コールバック関数にデバウンス機能を追加
@app.callback(
    Output('filter-graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('input-sampling-time', 'value'),
     State('radio-x-type', 'value'), State('input-min-x', 'value'), State('input-max-x', 'value'),
     State('radio-y-type', 'value'), State('input-min-y', 'value'), State('input-max-y', 'value'),
     State('radio-z-type', 'value'), State('input-min-z', 'value'), State('input-max-z', 'value')]
)
def update_graph(n_clicks, input_sampling_time, radio_x_type, input_min_x, input_max_x, radio_y_type, input_min_y, input_max_y, radio_z_type, input_min_z, input_max_z):
    if n_clicks > 0:
        # フィルタのインスタンスを作成
        filt = filter()

        # check_filter 関数を呼び出し、グラフを生成
        fig = filt.check_filter(input_sampling_time, radio_x_type, input_min_x, input_max_x, radio_y_type, input_min_y, input_max_y, radio_z_type, input_min_z, input_max_z)

        return fig

    return go.Figure()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

