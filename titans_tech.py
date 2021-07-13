#!/usr/bin/env python

# RENAME THIS FILE WITH YOUR TEAM NAME.

import numpy as np
import dayTrader
import longTrader

nInst=100
currentPos = np.zeros(nInst)

# Dummy algorithm to demonstrate function format.
def getMyPosition (prcSoFar):
    global currentPos
    (nins,nt) = prcSoFar.shape

    for i in range(100):
        if i >= 50:
            currentPos[i] = dayTrader.get_new_position(
                i, prcSoFar[i], currentPos[i]
            )
        else:
            currentPos[i] = longTrader.get_new_position(
                i, prcSoFar[i], currentPos[i]
            )

    return currentPos

