# -*- coding: utf-8 -*-

#ライブラリの読み込み
import time
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
        #st.markdown("フィルタ特性")
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
        #ax.show()
        st.pyplot(fig)

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
        st.write('<span style="color:red">右上のコピーボタンでクリップボードにコピー</span>',unsafe_allow_html=True)
        st.code(out_string)

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

    def filter_coef(self, dt, fl, fh, filtertype):
        Wn, N = self.get_filterparam(dt, fl, fh, filtertype)
        b1, a1 = signal.butter(N, Wn, filtertype, False)
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

def main():
    #タイトル
    st.title("IIR filter coefficient output")

    sampling_time = st.sidebar.number_input('Sampling time [ms] (単位が"ms"なので注意)', 0.0, 10.0, 4.0)
    #st.sidebar.write('<span style="color:red">単位[ms]に注意</span>',unsafe_allow_html=True)
    rbX = st.sidebar.radio("Range_X", ("LPF", "HPF", "BPF"), horizontal=True)
    if rbX == "LPF":
        minX = 0
        maxX = st.sidebar.number_input('Range_X Max[Hz]', 0.0, 200.0, 50.0)
    elif rbX == "HPF":
        minX = st.sidebar.number_input('Range_X Min[Hz]', 0.0, 200.0, 1.0)
        maxX = 1000
    elif rbX == "BPF": 
        minX = st.sidebar.number_input('Range_X Min[Hz]', 0.0, 200.0, 1.0)
        maxX = st.sidebar.number_input('Range_X Max[Hz]', 0.0, 200.0, 50.0)

    rbY = st.sidebar.radio("Range_Y", ("LPF", "HPF", "BPF"), horizontal=True)
    if rbY == "LPF":
        minY = 0
        maxY = st.sidebar.number_input('Range_Y Max[Hz]', 0.0, 200.0, 50.0)
    elif rbY == "HPF":
        minY = st.sidebar.number_input('Range_Y Min[Hz]', 0.0, 200.0, 1.0)
        maxY = 1000
    elif rbY == "BPF": 
        minY = st.sidebar.number_input('Range_Y Min[Hz]', 0.0, 200.0, 1.0)
        maxY = st.sidebar.number_input('Range_Y Max[Hz]', 0.0, 200.0, 50.0)

    rbZ = st.sidebar.radio("Range_Z", ("LPF", "HPF", "BPF"), horizontal=True)
    if rbZ == "LPF":
        minZ = 0
        maxZ = st.sidebar.number_input('Range_Z Max[Hz]', 0.0, 200.0, 50.0)
    elif rbZ == "HPF":
        minZ = st.sidebar.number_input('Range_Z Min[Hz]', 0.0, 200.0, 1.0)
        maxZ = 1000
    elif rbZ == "BPF": 
        minZ = st.sidebar.number_input('Range_Z Min[Hz]', 0.0, 200.0, 1.0)
        maxZ = st.sidebar.number_input('Range_Z Max[Hz]', 0.0, 200.0, 50.0)

    execute_output = st.button("フィルタ特性確認+フィルタ係数出力")
    my_script = filter()
    
    if execute_output:
        #解析
        my_script.check_filter(sampling_time/1000, rbX, minX, maxX, rbY, minY, maxY, rbZ, minZ, maxZ)
        my_script.out_result(sampling_time/1000, rbX, minX, maxX, rbY, minY, maxY, rbZ, minZ, maxZ)
                
if __name__ == '__main__':
    main()