#pylint: disable=attribute-defined-outside-init
#pylint: disable=access-member-before-definition
"""
Basic neuron models.
"""
import numpy as np

from ..basemodel import Model

class IAF(Model):
    """
    Integrate-and-Fire neuron model.
    """
    Default_States = dict(spike=0, v=0)
    Default_Params = dict(vt=0.025, c=5., bias=0.01)

    def ode(self, stimulus=0.):
        self.spike = 0.
        self.d_v = 1./self.c*(stimulus+self.bias)

    def post(self):
        if self.v > self.vt:
            self.v = 0.
            self.spike = 1

class LeakyIAF(Model):
    """
    Leaky IAF neuron model.
    """
    Default_States = dict(spike=0, v=(-0.05, -0.070, 0.025))
    Default_Params = dict(vt=-0.025, c=1.5, vr=-0.070, r=0.2)

    def ode(self, stimulus=0.):

        self.spike = 0.
        self.d_v = 1./self.c*(-self.v/self.r + stimulus)

    def post(self):
        if self.v > self.vt:
            self.v = self.vr
            self.spike = 1.

class Rinzel(Model):
    """
    Rinzel neuron model.
    """
    Time_Scale = 1e3 # s to ms
    Default_States = dict(v=(-60, -80, 30), w=(0., 0., 1.))
    Default_Params = dict(C=0.75, gNa=120., gK=36., gL=0.3, \
        ENa=50., EK=-77., EL=-54.387, s=1.27135220916422)

    def ode(self, stimulus=0.):

        alpha = np.exp(-(self.v+55.)/10.)-1.
        beta = (0.125*np.exp(-(self.v+65.)/80.))
        if abs(alpha) <= 1e-7:
            alpha = 0.1
        else:
            alpha = -0.01*(self.v+55.) / alpha
        n_infty = alpha / (alpha + beta)

        alpha = np.exp(-(self.v+40.)/10.)-1.
        beta = (4.*np.exp(-(self.v+65.)/18.))
        if abs(alpha) <= 1e-7:
            alpha = 1.
        else:
            alpha = -0.1*(self.v+40.) / alpha
        m_infty = alpha / (alpha + beta)

        alpha = (0.07 * np.exp(-(self.v+65.)/20.))
        beta = 1. / (np.exp(-(self.v+35.)/10.)+1.)
        h_infty = alpha / (alpha + beta)

        w_infty = self.s/(1.+self.s**2)*(n_infty + self.s*(1.-h_infty))
        tau_w = 1. + 5.*np.exp(-(self.v+55.)*(self.v+55.)/55.*55.)

        self.d_w = 3. * w_infty/tau_w - 3./tau_w * self.w

        i_na = self.gNa * np.power(m_infty, 3) * (1.-self.w) * (self.v - self.ENa)
        i_k = self.gK * np.power(self.w/self.s, 4) * (self.v - self.EK)
        i_l = self.gL * (self.v - self.EL)

        self.d_v = 1./self.C*(stimulus - i_na - i_k - i_l)


class Wilson(Model):
    """
    Wilson neuron model.

    [1] Wilson, "Spikes, decisions, and actions," 1998.
    """
    Time_Scale = 1e3 # s to ms
    Default_States = dict(r=0.088, v=-70.)
    Default_Params = dict(C=1.2, EK=-92., gK=26., ENa=55.)

    def ode(self, stimulus=0.):

        r_infty = 0.0135*self.v+1.03
        self.d_r = (r_infty-self.r)/1.9

        i_na = (17.81+0.4771*self.v+0.003263*self.v**2)*(self.v-self.ENa)
        i_k = self.gK*self.r*(self.v-self.EK)
        self.d_v = 1./self.C*(stimulus - i_na - i_k)


class MorrisLecar(Model):
    """
    Morris-Lecar neuron model.
    """
    Default_States = dict(r=0, s=0)
    Default_Params = dict(ar=0.09, br=0.012, k3=0.18, k4=0.034, kd=100, gmax=1, n=4)

    def ode(self, **kwargs):
        pass

class ConnorStevens(Model):
    """
    Connor-Stevens neuron model.
    """
    Time_Scale = 1e3 # s to ms
    Default_States = dict(v=(-60, -80, 50), n=(0., 0., 1.), \
        m=(0., 0., 1.), h=(1., 0., 1.), a=(1., 0., 1.), b=(1., 0., 1.))
    Default_Params = dict(ms=-5.3, ns=-4.3, hs=-12., \
        gNa=120., gK=20., gL=0.3, ga=47.7, \
        ENa=55., EK=-72., EL=-17., Ea=-75.)

    def ode(self, stimulus=0.):

        alpha = np.exp(-(self.v+50.+self.ns)/10.)-1.
        if abs(alpha) <= 1e-7:
            alpha = 0.1
        else:
            alpha = -0.01*(self.v+50.+self.ns)/alpha
        beta = .125*np.exp(-(self.v+60.+self.ns)/80.)
        n_inf = alpha/(alpha+beta)
        tau_n = 2./(3.8*(alpha+beta))

        alpha = np.exp(-(self.v+35.+self.ms)/10.)-1.
        if abs(alpha) <= 1e-7:
            alpha = 1.
        else:
            alpha = -.1*(self.v+35.+self.ms)/alpha
        beta = 4.*np.exp(-(self.v+60.+self.ms)/18.)
        m_inf = alpha/(alpha+beta)
        tau_m = 1./(3.8*(alpha+beta))

        alpha = .07*np.exp(-(self.v+60.+self.hs)/20.)
        beta = 1./(1.+np.exp(-(self.v+30.+self.hs)/10.))
        h_inf = alpha/(alpha+beta)
        tau_h = 1/(3.8*(alpha+beta))

        a_inf = np.cbrt(.0761*np.exp((self.v+94.22)/31.84)/(1.+np.exp((self.v+1.17)/28.93)))
        tau_a = .3632+1.158/(1.+np.exp((self.v+55.96)/20.12))
        b_inf = np.power(1/(1+np.exp((self.v+53.3)/14.54)), 4.)
        tau_b = 1.24+2.678/(1+np.exp((self.v+50)/16.027))


        i_na = self.gNa * np.power(self.m, 3) * self.h * (self.v - self.ENa)
        i_k = self.gK * np.power(self.n, 4) * (self.v - self.EK)
        i_l = self.gL * (self.v - self.EL)
        i_a = self.ga * np.power(self.a, 3) * self.b * (self.v - self.Ea)

        self.d_v = stimulus - i_na - i_k - i_l - i_a
        self.d_n = (n_inf-self.n)/tau_n
        self.d_m = (m_inf-self.m)/tau_m
        self.d_h = (h_inf-self.h)/tau_h
        self.d_a = (a_inf-self.a)/tau_a
        self.d_b = (b_inf-self.b)/tau_b


class HodgkinHuxley(Model):
    """
    Hodgkin-Huxley neuron model.
    """
    Time_Scale = 1e3 # s to ms
    Default_States = dict(v=(-60, -80, 30), n=(0., 0., 1.), \
        m=(0., 0., 1.), h=(1., 0., 1.))
    Default_Params = dict(gNa=120., gK=36., gL=0.3, ENa=50., EK=-77., EL=-54.387)

    def ode(self, stimulus=0.):

        alpha = np.exp(-(self.v+55.)/10.)-1.
        beta = (0.125*np.exp(-(self.v+65.)/80.))
        if abs(alpha) <= 1e-7:
            self.d_n = 0.1 * (1.-self.n) - beta * self.n
        else:
            self.d_n = (-0.01*(self.v+55.)/alpha) * (1.-self.n) - beta * self.n

        alpha = np.exp(-(self.v+40.)/10.)-1.
        beta = (4.*np.exp(-(self.v+65.)/18.))
        if abs(alpha) <= 1e-7:
            self.d_m = (1.-self.m) - beta * self.m
        else:
            self.d_m = (-0.1*(self.v+40.)/alpha) * (1.-self.m) - beta * self.m

        alpha = (0.07 * np.exp(-(self.v+65.)/20.))
        beta = 1. / (np.exp(-(self.v+35.)/10.)+1.)
        self.d_h = alpha * (1-self.h) - beta * self.h

        i_na = self.gNa * np.power(self.m, 3) * self.h * (self.v - self.ENa)
        i_k = self.gK * np.power(self.n, 4) * (self.v - self.EK)
        i_l = self.gL * (self.v - self.EL)

        self.d_v = stimulus - i_na - i_k - i_l
