# -*- coding: utf-8 -*-

#ライブラリの読み込み
import time
import gradio as gr
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal

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
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(Xw*fn, 20*np.log10(abs(Xh)), label="Range_X")
        ax.plot(Yw*fn, 20*np.log10(abs(Yh)), label="Range_Y")
        ax.plot(Zw*fn, 20*np.log10(abs(Zh)), label="Range_Z")
        ax.axvline(fn, label="Nyquist", color="red", linestyle="dotted")
        ax.set_xlim([0,80])
        ax.set_ylim([-40,10])
        ax.set_title('Butterworth filter frequency response')
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('Amplitude [dB]')
        ax.legend()
        ax.grid(which='both', axis='both')
        return fig

    def out_result(self, dt, Xtype, Xfl, Xfh, Ytype, Yfl, Yfh, Ztype, Zfl, Zfh):
        ftype1 = self.get_filtertype(Xtype)
        ftype2 = self.get_filtertype(Ytype)
        ftype3 = self.get_filtertype(Ztype)

        out1 = self.filter_coef(dt, Xfl, Xfh, ftype1)
        out2 = self.filter_coef(dt, Yfl, Yfh, ftype2)
        out3 = self.filter_coef(dt, Zfl, Zfh, ftype3)

        out_string = out1 + out2 + out3

        # clipboard.OpenClipboard()
        # clipboard.EmptyClipboard()
        # clipboard.SetClipboardText(out_string)
        # clipboard.CloseClipboard()
        return out_string

    def get_filtertype(self, rb):
        if rb == "LPF":
            ftype = "lowpass"
        elif rb == "HPF":
            ftype = "highpass"
        else:
            ftype = "bandpass"
        return ftype

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

    def filter_coef(self, dt, fl, fh, filtertype):
        Wn, N = self.get_filterparam(dt, fl, fh, filtertype)
        b1, a1 = signal.butter(N, Wn, filtertype, True)
        coefs = map(str, list(b1)+list(a1))

        if filtertype == "bandpass":
            head1 = "/* " + str(fl) + "Hz" + " */" + "\r\n"
            head2 = "/* " + str(fh) + "Hz" + " */" + "\r\n"
            head3 = "/* BPF " + str(Wn[0]) + "-" + str(Wn[1]) + " */" + "\r\n"
        elif filtertype == "lowpass":
            head1 = "/* */" + "\r\n"
            head2 = "/* " + str(fh)+"Hz" + " */" + "\r\n"
            head3 = "/* LPF " + str(Wn) + "- */" + "\r\n"
        else:
            head1 = "/* " + str(fl)+"Hz" + " */" + "\r\n"
            head2 = "/* */" + "\r\n"
            head3 = "/* HPF " + str(Wn) + "- */" + "\r\n"
        
        return head1 + head2 + head3 + "\r\n".join(coefs) + "\r\n"

def check_filter_gradio(dt, Xtype, Xfl, Xfh, Ytype, Yfl, Yfh, Ztype, Zfl, Zfh):
    my_filter = filter()
    # check_filter メソッドを実行してグラフを取得
    fig = my_filter.check_filter(dt, Xtype, Xfl, Xfh, Ytype, Yfl, Yfh, Ztype, Zfl, Zfh)
    # matplotlibの図をGradioに適した形で返す
    return fig, my_filter.out_result(dt, Xtype, Xfl, Xfh, Ytype, Yfl, Yfh, Ztype, Zfl, Zfh)

# Gradioインターフェースの構築
iface = gr.Interface(
    fn=check_filter_gradio,  # 処理する関数
    inputs=[
        gr.Number(label="Sampling time [ms]", value=4.0),  # 'default'を'value'に変更
        gr.Radio(["LPF", "HPF", "BPF"], label="Range_X", value="LPF"),
        gr.Number(label="Range_X Min[Hz]", value=0.1),
        gr.Number(label="Range_X Max[Hz]", value=50.0),
        gr.Radio(["LPF", "HPF", "BPF"], label="Range_Y", value="LPF"),
        gr.Number(label="Range_Y Min[Hz]", value=0.1),
        gr.Number(label="Range_Y Max[Hz]", value=50.0),
        gr.Radio(["LPF", "HPF", "BPF"], label="Range_Z", value="LPF"),
        gr.Number(label="Range_Z Min[Hz]", value=0.1),
        gr.Number(label="Range_Z Max[Hz]", value=50.0),
    ],
    outputs=[gr.Plot(label="Filter Characteristics"),
        gr.Textbox(label="Filter Coefficients")]

)

if __name__ == '__main__':
    iface.launch()

    