# ---------------------------------------------------------------------------
# EDHEC BBA final thesis — "Financial market & oil volatility within distressed
# economies: wavelet coherence evidence from the early 21st century"
# Yann Simons — final R script, as used for the thesis (unchanged below).
#
# Reproduction notes (added for this repository):
# - The script was written for a local workbook at an absolute path. Use the
#   files in ../data instead, e.g.:
#     Thesisbook <- read.csv("data/thesis_dataset_with_returns.csv")
# - rWTI, rEPU and rGPR are simple monthly percentage changes. They are
#   provided in data/thesis_dataset_with_returns.csv and match the
#   descriptive-statistics table of the thesis (section III.B).
# - Packages: readxl, aTSA, tseries (jarque.bera.test), lmtest (grangertest),
#   vars (VARselect), biwavelet (wtc).
# ---------------------------------------------------------------------------

library(readxl)
Thesisbook <- read_excel("C:/Users/Yann/Desktop/THESE FINAL/Thesisbook.xlsx")
View(Thesisbook)
DB1=Thesisbook
attach(DB1)
summary(DB1)
acf(DB1$rWTI,lag.max = 20)
acf(DB1$rGPR,lag.max = 20)
acf(DB1$rEPU,lag.max = 20)
acf(DB1$WTI,lag.max = 20)
acf(DB1$GPR,lag.max = 20)
acf(DB1$EPU,lag.max = 20)
rOIL<- rWTI
library(aTSA)
rGEO<-rGPR
rECO<-rEPU
PP.test(rOIL)
PP.test(rGEO)
PP.test(rECO)
rECO<-rEPU
PP.test(rECO)
jarque.bera.test(rOIL)
jarque.bera.test(rECO)
jarque.bera.test(rGEO)
RLT1<-(lm(rWTI~rEPU+rGPR,data = DB1))
coef(RLT1)
summary(RLT1)
grangertest(rECO,rOIL,order = 3)
grangertest(rGEO,rOIL,order = 3)
grangertest(rOIL,rGEO,order = 1)
VARselect(data.frame(rOIL,rECO))
VARselect(data.frame(rOIL,rGEO))
VARselect(data.frame(rECO,rOIL))
VARselect(data.frame(rGEO,rOIL))
model1<-lm(rECO ~ rOIL + rOIL)
BIC(model1)
model2<-lm(rOIL ~ rGEO)
BIC(model2)
model3<-lm(rOIL ~ rECO)
BIC(model3)
library(biwavelet)
attach(Thesisbook)
A=rWTI
B=rEPU
t1<- cbind(1:267,rWTI)
t2<- cbind(1:267,rEPU)
nrands = 100
wtc.AB = wtc(t1, t2, nrands = nrands )
par(oma=c(0, 0, 0, 1),mar = c(5, 4, 4, 5) + 0.1)
plot(wtc.AB, plot.phase = TRUE, lty.coi = 1, col.coi = "grey", lwd.coi = 2, lwd.sig = 2, arrow.lwd = 0,03,
     arrow.len = 0,12, ylab = "Period", xlab="time" , plot.cb = TRUE, main = "WTI vs EPU", xaxt="n")
n=length(t1[,1])
axis(side = 1, at = c(seq(0, n, 12)), labels = c(seq(2000, 2022, 1))) 
rm(list = ls(all=TRUE))
A=rWTI
B=rGPR
t1<- cbind(1:267,rWTI)
t2<- cbind(1:267,rGPR)
nrands = 100
wtc.AB = wtc(t1, t2, nrands = nrands )
par(oma=c(0, 0, 0, 1),mar = c(5, 4, 4, 5) + 0.1)
plot(wtc.AB, plot.phase = TRUE, lty.coi = 1, col.coi = "grey", lwd.coi = 2, lwd.sig = 2, arrow.lwd = 0,03,
     arrow.len = 0,12, ylab = "Period", xlab="time" , plot.cb = TRUE, main = "WTI vs GPR", xaxt="n")
n=length(t1[,1])
axis(side = 1, at = c(seq(0, n, 12)), labels = c(seq(2000, 2022, 1)))      
     
     