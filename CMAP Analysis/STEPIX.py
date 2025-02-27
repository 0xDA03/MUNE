import numpy as np

class SETPIX:
    def __init__(self, DataAmps, NoiseThreshold=0.02):
        """Initialize the SETPIX class."""
        self.DataAmps = DataAmps

        self.STEPIX, self.AMPIX, self.D50, self.Point = self._Calc_Values(NoiseThreshold)

    def _Calc_Values(self, NoiseThreshold):
        """Calculate the SETPIX values."""
        try:
            SortedAmps=np.flip(np.sort(self.DataAmps))

            StepAmps = SortedAmps[:-1] - SortedAmps[1:]

            SortedStepAmps=np.flip(np.sort(StepAmps))



            StepActivation = SortedStepAmps[SortedStepAmps > 2.5*NoiseThreshold]
            Reconstruction = np.cumsum(SortedStepAmps)

            Amp_50=max(Reconstruction)/2

            for i in range(len(Reconstruction)):
                if Reconstruction[i]>Amp_50:
                    D50=i+1
                    break


            #STEPIX
            StepNumber=np.arange(1,len(StepActivation)+1)
            
            fit = np.polyfit(np.log(StepNumber), StepActivation, 1)
            
            a=fit[0]
            b=fit[1]

            P_Step=int(np.round(np.exp(-b/a)))

            Reconstruction_Percentage=100*Reconstruction/max(Reconstruction)

            if len(Reconstruction_Percentage)>P_Step:
                m=Reconstruction_Percentage[P_Step-1]/P_Step
            else:
                m=100/P_Step

            Q_Step=int(np.round(80/m))

            if len(SortedStepAmps)<=Q_Step:
                Q_Step=len(SortedStepAmps)-1

            Q_Amp=SortedStepAmps[Q_Step-1]

            Point="Q"
            while True:
                if Q_Amp>=NoiseThreshold:
                    STEPIX=Q_Step
                    break
                else:
                    Point="R"
                    Q_Step=Q_Step-1
                    Q_Amp=SortedStepAmps[Q_Step-1]

            AMPIX=1000*max(self.DataAmps)/STEPIX
        except:
            return np.nan, np.nan, np.nan, np.nan

        return STEPIX, AMPIX, D50, Point

# Fig2=go.Figure()
# Fig2.add_trace(go.Scatter(x=Xs, y=SortedStepAmps, marker=dict(color="#FF0000",size=3), mode='markers'))
# Fig2.add_trace(go.Scatter(x=[Q_Step], y=[Q_Amp], marker=dict(color="#00FF00",size=6), mode='markers'))
# Fig2.add_trace(go.Scatter(x=Xs, y=Ys, marker=dict(color="#0000FF",size=2), mode='lines'))
# Fig2.show()
