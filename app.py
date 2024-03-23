import streamlit as st
import numpy as np
from scipy.stats import norm

import streamlit as st
import matplotlib.pyplot as plt
from scipy.stats import norm
import warnings
warnings.filterwarnings('ignore')

# Base libraries
import pandas as pd
from numpy import *
import yfinance as yf
from scipy.stats import norm

# Plotting
import matplotlib.pyplot as plt
from tabulate import tabulate

# Option Strategy plotting
import opstrat as op



class BS:
    
    """
    This is a class for Options contract for pricing European options on stocks without dividends.
    
    Attributes: 
        spot          : int or float
        strike        : int or float 
        rate          : float
        dte           : int or float [days to expiration in number of years]
        volatility    : float
    """    
    
    def __init__(self, spot, strike, rate, dte, volatility):
        
        # Spot Price
        self.spot = spot
        
        # Option Strike
        self.strike = strike
        
        # Interest Rate
        self.rate = rate
        
        # Days To Expiration
        self.dte = dte
        
        # Volaitlity
        self.volatility = volatility
       
        # Utility 
        self._a_ = self.volatility * self.dte**0.5
        
        if self.strike == 0:
            raise ZeroDivisionError('The strike price cannot be zero')
        else:
            self._d1_ = (log(self.spot / self.strike) + \
                     (self.rate + (self.volatility**2) / 2) * self.dte) / self._a_
        
        self._d2_ = self._d1_ - self._a_
        
        self._b_ = e**-(self.rate * self.dte)
        
        
        # The __dict__ attribute
        for i in ['callPrice', 'putPrice', 'callDelta', 'putDelta', 'callTheta', 'putTheta', \
                  'callRho', 'putRho', 'vega', 'gamma']:
            self.__dict__[i] = None
        
        [self.callPrice, self.putPrice] = self._price
        [self.callDelta, self.putDelta] = self._delta
        [self.callTheta, self.putTheta] = self._theta
        [self.callRho, self.putRho] = self._rho
        self.vega = self._vega
        self.gamma = self._gamma
    
        
    # Option Price    
    @property
    def _price(self):
        '''Returns the option price: [Call price, Put price]'''

        if self.volatility == 0 or self.dte == 0:
            call = maximum(0.0, self.spot - self.strike)
            put = maximum(0.0, self.strike - self.spot)
        else:
            call = self.spot * norm.cdf(self._d1_) - self.strike * e**(-self.rate * \
                                                                       self.dte) * norm.cdf(self._d2_)

            put = self.strike * e**(-self.rate * self.dte) * norm.cdf(-self._d2_) - \
                                                                        self.spot * norm.cdf(-self._d1_)
        return [call, put]

    
    # Option Delta
    @property
    def _delta(self):
        '''Returns the option delta: [Call delta, Put delta]'''

        if self.volatility == 0 or self.dte == 0:
            call = 1.0 if self.spot > self.strike else 0.0
            put = -1.0 if self.spot < self.strike else 0.0
        else:
            call = norm.cdf(self._d1_)
            put = -norm.cdf(-self._d1_)
        return [call, put]


    # Option Gamma
    @property
    def _gamma(self):
        '''Returns the option gamma'''
        return norm.pdf(self._d1_) / (self.spot * self._a_)


    # Option Vega
    @property
    def _vega(self):
        '''Returns the option vega'''
        if self.volatility == 0 or self.dte == 0:
            return 0.0
        else:
            return self.spot * norm.pdf(self._d1_) * self.dte**0.5 / 100


    # Option Theta
    @property
    def _theta(self):
        '''Returns the option theta: [Call theta, Put theta]'''
        call = -self.spot * norm.pdf(self._d1_) * self.volatility / (2 * self.dte**0.5) - self.rate * self.strike * self._b_ * norm.cdf(self._d2_)

        put = -self.spot * norm.pdf(self._d1_) * self.volatility / (2 * self.dte**0.5) + self.rate * self.strike * self._b_ * norm.cdf(-self._d2_)
        return [call / 365, put / 365]


    # Option Rho
    @property
    def _rho(self):
        '''Returns the option rho: [Call rho, Put rho]'''
        call = self.strike * self.dte * self._b_ * norm.cdf(self._d2_) / 100
        put = -self.strike * self.dte * self._b_ * norm.cdf(-self._d2_) / 100

        return [call, put]

    # Implied Vol
    @property
    def _IV(self):
        pass

    # Other property methods as you defined


# Function to calculate Greeks for a range of strikes
def calculate_greeks(spot, rate, dte, volatility, strikes,option_type ):
    deltas = []
    gammas = []
    vegas = []
    thetas = []
    
    for strike in strikes:
        
        option = BS(spot, strike, rate, dte, volatility)
        if option_type ='call' : 
            deltas.append(option.callDelta)
        else : 
            deltas.append(option.putlDelta)
        gammas.append(option.gamma)
        vegas.append(option.vega)
        thetas.append(option.callTheta)
    
    return deltas, gammas, vegas, thetas



# Streamlit app layout
# Introduction to the Black-Scholes Model
st.title("Black-Scholes Model Overview")

# Introducing Black-Scholes
st.write("""
    The Black-Scholes model is a cornerstone of modern financial theory. It was developed by Fischer Black, 
    Myron Scholes, and Robert Merton in the early 1970s to provide a mathematical framework for valuing European 
    options, which are financial derivatives that give the holder the right, but not the obligation, 
    to buy or sell an underlying asset at a specified price on or before a specified date.
""")

# Expander for more detailed information
with st.expander("Learn More About the Black-Scholes Model"):
    st.markdown("""
        The formula led to a boom in options trading and provided a mathematical justification for the trading 
        of derivatives, which until that point had been relatively ad hoc and thinly traded. The model also 
        led to the development of several related calculations that are commonly used by traders to assess the risk 
        and potential return of options portfolios, known as the "Greeks."
        
        Although it may seem daunting at first, the Black-Scholes model is based on a few relatively simple principles 
        of financial markets and provides a systematic method for evaluating options that has been widely adopted 
        in the financial industry.
        
        In 1997, Scholes and Merton were awarded the Nobel Prize in Economics for their work in finding a new method 
        to determine the value of derivatives (Black had passed away by this time and thus was not eligible).
    """)

# Display the Black-Scholes Formula
st.subheader("Black-Scholes Formula for a Call Option:")
st.latex(r'''
    C(S, t) = S_0 N(d_1) - X e^{-rT} N(d_2)
''')
st.markdown("""
    where:
    - \(C(S, t)\) = Call option price
    - \(S_0\) = Current stock price
    - \(X\) = Strike price of the option
    - \(T\) = Time to expiration
    - \(r\) = Risk-free interest rate
    - \(N(d)\) = Cumulative distribution function of the standard normal distribution
    - \(d_1\) and \(d_2\) are intermediate calculations based on the other factors.
""")

# Additional resources and advanced topics
st.subheader("Additional Resources and Advanced Topics")
st.markdown("""
    - [Black-Scholes Model - Investopedia](https://www.investopedia.com/terms/b/blackscholes.asp)
    - [Option Pricing & Stock Price Movement - Khan Academy](https://www.khanacademy.org/economics-finance-domain/core-finance/derivative-securities/black-scholes/v/black-scholes-formula)
    - [The Greeks: Delta, Gamma, Theta, Vega, and Rho](https://www.investopedia.com/trading/getting-to-know-the-greeks/)
""")

# Advanced topics collapsible section
with st.expander("Advanced Topics"):
    st.markdown("""
        **The Greeks and Risk Management**
        - **Delta**: Measures the rate of change of the option price with respect to changes in the underlying asset's price.
        - **Gamma**: Measures the rate of change in Delta over time.
        - **Theta**: Measures the sensitivity of the option price to the passage of time.
        - **Vega**: Measures sensitivity to volatility.
        - **Rho**: Measures sensitivity to the interest rate.
        
        **Limitations of the Black-Scholes Model**
        - Assumes markets are efficient and prices follow a log-normal distribution.
        - Does not account for dividends paid during the life of the option.
        - Assumes volatility and interest rates are constant and known.
    """)




# Input fields for the option parameters in the sidebar

st.sidebar.title('Donate')
st.sidebar.image("img/QR_phatra.jpg", use_column_width=True)
# Option type selection
option_type = st.sidebar.selectbox('Option Type', ['Call', 'Put'])
# Input fields for the option parameters in the sidebar
spot = st.sidebar.number_input('Spot Price', value=100.0)
rate = st.sidebar.number_input('Interest Rate (as a decimal, e.g., 0.05 for 5%)', value=0.05)
dte = st.sidebar.number_input('Days to Expiration (in years, e.g., 0.5 for 6 months)', value=0.5)
volatility = st.sidebar.number_input('Volatility (as a decimal, e.g., 0.2 for 20%)', value=0.2)
min_strike = st.sidebar.number_input('Minimum Strike Price', value=80.0)
max_strike = st.sidebar.number_input('Maximum Strike Price', value=120.0)
num_strikes = st.sidebar.number_input('Number of Strike Prices', value=50, step=1)




import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Visualize Greeks button
if st.sidebar.button('Visualize Greeks'):
    strikes = np.linspace(min_strike, max_strike, num=num_strikes)
    if option_type == 'Call':
        deltas, gammas, vegas, thetas = calculate_greeks(spot, rate, dte, volatility, strikes)
    else:
        deltas, gammas, vegas, thetas = calculate_greeks(spot, rate, dte, volatility, strikes)
    
    # Create subplots
    fig = make_subplots(rows=2, cols=2, subplot_titles=('Delta', 'Gamma', 'Vega', 'Theta'))
    
    # Add traces for the selected option type
    fig.add_trace(go.Scatter(x=strikes, y=deltas, mode='lines', name=f'{option_type} Delta'), row=1, col=1)
    fig.add_trace(go.Scatter(x=strikes, y=gammas, mode='lines', name=f'{option_type} Gamma'), row=1, col=2)
    fig.add_trace(go.Scatter(x=strikes, y=vegas, mode='lines', name=f'{option_type} Vega'), row=2, col=1)
    fig.add_trace(go.Scatter(x=strikes, y=thetas, mode='lines', name=f'{option_type} Theta'), row=2, col=2)
    
    # Update layout
    fig.update_layout(height=600, width=800, title_text=f"Option Greeks Vs Strike - {option_type} Option")
    fig.update_layout(showlegend=False)
    
    # Show plot
    st.plotly_chart(fig)

