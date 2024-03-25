
#' **This is my third NTCP model in R**
#' This is just a copy of CITOR NTCP model. I just want to know how fit this
#' model is with my data.
#### import the libraries
rm(list =ls())
library(pROC)
library(SciViews)
library(ISLR)
library(gridExtra)
library(rms)
library(ResourceSelection)
library(openxlsx)
library(ggplot2)
library(dplyr)
library(writexl)

###### import the necessary functions ###### 
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\forward_sel_logistic.R")
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\univariable.analysis.R")
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\preselection_correlation_v2.R")

###### open the proper file ###### 
DATA_num <- read.xlsx("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\Preprocessing\\Delta_radiomics\\Feature_extraction_factory\\train_main1.xlsx")

###### preprocessing the data ######

# make a label name(y)
ynam="xer_06"
DATA = DATA_num[,!colnames(DATA_num) %in% c("X1")]

# make a unify Parotidfrom left and right glands and with sqrt  column
#DATA$Parotid_sqrt = sqrt(DATA$Parotid_R_Dmean) + sqrt(DATA$Parotid_L_Dmean)
#DATA$Submandibular_Dmean = ((DATA$Submandibular_R_Dmean) + (DATA$Submandibular_L_Dmean))/ 2.

# extract to label clumn out of the xerostomia baseline
#DATA$baseline_little = as.numeric(DATA$xer_bsl == 2) 
#DATA$baseline_mod_sev = as.numeric(DATA$xer_bsl == 3)

###### CITOR model ###### 
# Use the coefficents of feature forward selection to make a Logistic Regression model
dd <- datadist(DATA);options(datadist='dd')

######## xer_06
## --- construct the formula  from CITOR --- #MODIFY
b0= -2.5007
b1= 0.0193 #<- Submandibular Glands
b2= 0.1054 #<- Parotid Glands
b3= 0.5234 #<- BSL little
b4= 1.2763 #<- BSL mod sev
#b0 = -2.9032
#b1 = 0.0193
#b2 = 0.1054
#b3 = 0.5234
#b4 = 1.2763

DATA$lp.ref= b0+
        b1*DATA$Submandibular_Dmean+
        b2*DATA$sqr_parotid_Dmean+
        b3*DATA$xer_bsl_little+
        b4*DATA$xer_bsl_moderate_to_severe

######## 

# Extract and plot the NTCP model
NTCP=1/(1+exp(-DATA$lp.ref));

# plot the NTCP values in order
plot(NTCP[order(NTCP)],col=c("black","red")[1+DATA$xer_06[order(NTCP)]],type= 'p',pch = c(16,16))

# make the model and fit the model
Model <- lrm(DATA$xer_06 ~ lp.ref, x = T, y = T, data = DATA); Model

# prdict by using this model
predict.fit <- predict(Model, type="fitted")

# Find all the elements related to ROC curve for this model
ROC_auc = roc(DATA$xer_06, NTCP, ci=T, plot=T)
ROC_auc
# implement Hosmer-Lemeshow goodness-of-fit (GOF) test to evaluate the goodness of the fit of the model
HL.test <-  hoslem.test(DATA$xer_06, NTCP);HL.test

# Save model predictions to a CSV file
write.csv(Model, file = "model1_predictions_06.csv")

###### Calibration plot ###### 
HL.test = hoslem.test(DATA$xer_06, NTCP, g=10)
N <- HL.test$observed[, 1] + HL.test$observed[, 2]
obs.rate <- HL.test$observed[, 2]/N
pred.rate <- HL.test$expected[, 2]/N
Calibration_DATA <- data.frame(pred.rate,obs.rate)
Linear_Calibration_fit <- lm(obs.rate ~ pred.rate, data = Calibration_DATA)

Points <- data.frame(row.names = c(1:length(Calibration_DATA$pred.rate)), Calibration_DATA$pred.rate, Calibration_DATA$obs.rate)
label1 = sprintf("HL (p-value) = %.2f (%.3f)", HL.test$statistic, HL.test$p.value)
label2 = sprintf("y = %.2f + %.2fx", Linear_Calibration_fit$coefficients[1], Linear_Calibration_fit$coefficients[2])
Calibration_DATA$lm = Linear_Calibration_fit$coefficients[1] + Linear_Calibration_fit$coefficients[2] * Calibration_DATA$pred.rate

ggplot(Points, aes(x = pred.rate, y = obs.rate)) +
  geom_point(size = 3) +
  labs(x= "Predicted rate", y = "Observed rate") + 
  ggtitle("Calibration plot refit Van den Bosch et al. model") +
  scale_x_continuous(limits = c(0, 1), breaks = c(0, 0.2, 0.4, 0.6, 0.8, 1)) +
  scale_y_continuous(limits = c(0, 1), breaks = c(0, 0.2, 0.4, 0.6, 0.8, 1)) +
  geom_abline(aes(intercept = 0, slope = 1, colour = 'Ideal'), size = 1, show.legend = TRUE) +
  geom_line(data = Calibration_DATA, aes(pred.rate,lm, colour = 'Fit'), size=1, linetype = 2, show.legend = TRUE) + 
  theme_bw() + 
  theme(strip.text = element_text(face = "bold", size = 14),
        strip.background = element_rect(fill = "lightgrey", colour = "black"),
        axis.title = element_text(size = 15),
        axis.text = element_text(size = 12), 
        plot.title = element_text(hjust = 0.5, size = 18)) + 
  annotate("text", x = 0.2, y = 1, label = label1) +
  annotate("text", x = 0.13, y = 0.95, label = label2) + 
  guides(colour=guide_legend("Legend"))



###### Using Sub models ######

##Estimate new coefficients

sub1 = DATA$Submandibular_Dmean + DATA$xer_wk1_little + DATA$xer_bsl_moderate_to_severe
sub2 = DATA$sqr_parotid_Dmean + DATA$xer_bsl_little + DATA$xer_bsl_moderate_to_severe

Submodel1 = lrm(DATA$xer_06 ~ Submandibular_Dmean + xer_bsl_little + xer_bsl_moderate_to_severe, data = DATA_num, x = T, y = T); Submodel1
Submodel2 = lrm(DATA$xer_06 ~ sqr_parotid_Dmean + xer_bsl_little + xer_bsl_moderate_to_severe, data = DATA, x = T, y = T); Submodel2
summary(Submodel1)
summary(Submodel2)

b0 = (Submodel1$coefficients[1] + Submodel2$coefficients[1])/2 # Intercept
b1 = Submodel1$coefficients[2]/2 # Submandibulars
b2 = Submodel2$coefficients[2]/2 # Parotid Glands
b3 = (Submodel1$coefficients[3] + Submodel2$coefficients[3])/2 # BSL Little
b4 = (Submodel1$coefficients[4] + Submodel2$coefficients[4])/2 # BSL Mod Sev

lp= b0+
  b1*DATA$Submandibular_Dmean+
  b2*DATA$sqr_parotid_Dmean+
  b3*DATA$xer_bsl_little+
  b4*DATA$xer_bsl_moderate_to_severe


NTCP=1/(1+exp(-lp));


# plot the NTCP values in order
plot(NTCP[order(NTCP)],col=c("black","red")[1+DATA$xer_12[order(NTCP)]],type= 'p',pch = c(16,16))

## --- fit linear predictor to endpoint to get validation statistics ---
fit.enter<- lrm(DATA$xer_06 ~ lp, x = T, y = T); fit.enter
predict.fit <-predict(fit.enter, type="fitted")
ROC_auc=roc(DATA$xer_06, NTCP, ci=T, plot=T)
hl.enter <-  hoslem.test(DATA$xer_06, predict.fit)
hl.enter
## --- format statistics ---
externalvalstats=as.data.frame(c(ROC_auc$auc[1],ROC_auc$ci[1],ROC_auc$ci[3],BIC(fit.enter), fit.enter$stats["R2"],fit.enter$coefficients[1],fit.enter$coefficients[2]))
rownames(externalvalstats)=c("AUC","95%CI_LL","95%CI_UL","BIC","R2", "Calibration intercept","Calibration slope");colnames(externalvalstats)=""
externalvalstats

## --- run next line to copy to clipboard, you can past in excel
write.table(externalvalstats, "clipboard", sep="\t", row.names=T, col.names=T)
HL.test

###### Calibration plot ###### 
HL.test = hoslem.test(DATA$xer_06, NTCP, g=10)
N <- HL.test$observed[, 1] + HL.test$observed[, 2]
obs.rate <- HL.test$observed[, 2]/N
pred.rate <- HL.test$expected[, 2]/N
Calibration_DATA <- data.frame(pred.rate,obs.rate)
Linear_Calibration_fit <- lm(obs.rate ~ pred.rate, data = Calibration_DATA)

Points <- data.frame(row.names = c(1:length(Calibration_DATA$pred.rate)), Calibration_DATA$pred.rate, Calibration_DATA$obs.rate)
label1 = sprintf("HL (p-value) = %.2f (%.2f)", hl.enter$statistic, hl.enter$p.value)
label2 = sprintf("y = %.2f + %.2fx", Linear_Calibration_fit$coefficients[1], Linear_Calibration_fit$coefficients[2])
Calibration_DATA$lm = Linear_Calibration_fit$coefficients[1] + Linear_Calibration_fit$coefficients[2] * Calibration_DATA$pred.rate

ggplot(Points, aes(x = pred.rate, y = obs.rate)) +
  geom_point(size = 3) +
  labs(x= "Predicted rate", y = "Observed rate") + 
  ggtitle("Calibration plot CITOR NTCP 6-month endpoint") +
  scale_x_continuous(limits = c(0, 1), breaks = c(0, 0.2, 0.4, 0.6, 0.8, 1)) +
  scale_y_continuous(limits = c(0, 1), breaks = c(0, 0.2, 0.4, 0.6, 0.8, 1)) +
  geom_abline(aes(intercept = 0, slope = 1, colour = 'Ideal'), size = 1, show.legend = TRUE) +
  geom_line(data = Calibration_DATA, aes(pred.rate,lm, colour = 'Fit'), size=1, linetype = 2, show.legend = TRUE) + 
  theme_bw() + 
  theme(strip.text = element_text(face = "bold", size = 14),
        strip.background = element_rect(fill = "lightgrey", colour = "black"),
        axis.title = element_text(size = 15),
        axis.text = element_text(size = 12), 
        plot.title = element_text(hjust = 0.5, size = 18)) + 
  annotate("text", x = 0.2, y = 1, label = label1) +
  annotate("text", x = 0.13, y = 0.95, label = label2) + 
  guides(colour=guide_legend("Legend"))




