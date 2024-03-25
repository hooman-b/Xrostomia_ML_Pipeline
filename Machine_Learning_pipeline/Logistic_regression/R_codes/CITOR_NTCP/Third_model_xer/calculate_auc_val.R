
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
DATA_num <- read.xlsx("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\Preprocessing\\Delta_radiomics\\Feature_extraction_factory\\test.xlsx")

###### preprocessing the data ######

# make a label name(y)
ynam="xer_12"
DATA = DATA_num[,!colnames(DATA_num) %in% c("X1")]

###### CITOR model ###### 
# Use the coefficents of feature forward selection to make a Logistic Regression model
dd <- datadist(DATA);options(datadist='dd')



Submodel1 = lrm(DATA$xer_12 ~ Submandibular_Dmean + xer_bsl_little + xer_bsl_moderate_to_severe, data = DATA_num, x = T, y = T); Submodel1
Submodel2 = lrm(DATA$xer_12 ~ sqr_parotid_Dmean + xer_bsl_little + xer_bsl_moderate_to_severe, data = DATA, x = T, y = T); Submodel2
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
fit.enter<- lrm(DATA$xer_12 ~ lp, x = T, y = T); fit.enter
predict.fit <-predict(fit.enter, type="fitted")
ROC_auc=roc(DATA$xer_12, NTCP, ci=T, plot=T)
hl.enter <-  hoslem.test(DATA$xer_12, predict.fit)
hl.enter
## --- format statistics ---
externalvalstats=as.data.frame(c(ROC_auc$auc[1],ROC_auc$ci[1],ROC_auc$ci[3],BIC(fit.enter), fit.enter$stats["R2"],fit.enter$coefficients[1],fit.enter$coefficients[2]))
rownames(externalvalstats)=c("AUC","95%CI_LL","95%CI_UL","BIC","R2", "Calibration intercept","Calibration slope");colnames(externalvalstats)=""
externalvalstats

## --- run next line to copy to clipboard, you can past in excel
write.table(externalvalstats, "clipboard", sep="\t", row.names=T, col.names=T)
HL.test



# AUC-ROC

DATA$lp.ref= b0+
  b1*DATA$Submandibular_Dmean+
  b2*DATA$sqr_parotid_Dmean+
  b3*DATA$xer_bsl_little+
  b4*DATA$xer_bsl_moderate_to_severe

######## 

# Extract and plot the NTCP model
NTCP=1/(1+exp(-DATA$lp.ref));

# plot the NTCP values in order
plot(NTCP[order(NTCP)],col=c("black","red")[1+DATA$xer_12[order(NTCP)]],type= 'p',pch = c(16,16))

# make the model and fit the model
Model <- lrm(DATA$xer_12 ~ lp.ref, x = T, y = T, data = DATA); Model

# prdict by using this model
predict.fit <- predict(Model, type="fitted")

# Find all the elements related to ROC curve for this model
ROC_auc = roc(DATA$xer_12, NTCP, ci=T, plot=T)
ROC_auc

auc0 = ROC_auc
auc1 = ROC_auc
auc2 = ROC_auc
auc3 = ROC_auc
auc4 = ROC_auc
auc5 = ROC_auc
auc6 = ROC_auc
auc7 = ROC_auc
auc8 = ROC_auc
auc9 = ROC_auc

auc6$ci[3]

auc_values <- c(auc1$auc, auc2$ci[1], auc3$auc, auc4$auc, auc5$auc, auc6$auc, auc7$auc, auc8$auc, auc9$auc)

# Calculate the ensemble AUC value using mean
ensemble_auc_mean <- mean(auc_values)

# Calculate the ensemble AUC value using median
ensemble_auc_median <- median(auc_values)

# Print the ensemble AUC values
print(paste("Ensemble AUC (Mean):", ensemble_auc_mean))
print(paste("Ensemble AUC (Median):", ensemble_auc_median))




sub_df <- read.csv('\\\\zkh\\appdata\\RTDicom\\Projectline_HNC_modelling\\Users\\Hooman Bahrdo\\sub_test.csv')
regular_df <- read.csv('\\\\zkh\\appdata\\RTDicom\\Projectline_HNC_modelling\\Users\\Hooman Bahrdo\\reg_test.csv')
weekly_df <- read.csv('\\\\zkh\\appdata\\RTDicom\\Projectline_HNC_modelling\\Users\\Hooman Bahrdo\\weekly_test.csv')
trans <- read.csv('\\\\zkh\\appdata\\RTDicom\\Projectline_HNC_modelling\\Users\\Hooman Bahrdo\\transfer.csv')


##################################### TWO AUC in one plot
# Create ROC curves for your two sets of data
roc1 <- roc(sub_df$label, sub_df$pred_dl, ci = TRUE, plot = FALSE)
roc2 <- roc(regular_df$label, regular_df$pred_dl, ci = TRUE, plot = FALSE)
roc3 <- roc(weekly_df$label, weekly_df$pred_dl, ci = TRUE, plot = FALSE)
roc4 <- roc(weekly_df$label, weekly_df$pred_lr, ci = TRUE, plot = FALSE)
roc5 <- roc(trans$label, trans$dl_new, ci = TRUE, plot = FALSE)

# Plot the first ROC curve
plot(roc1, col = "blue", main = "ROC Curve Comparison (Test Set)", xlab = "False Positive Rate", ylab = "True Positive Rate", print.auc = TRUE, print.auc.y = 0.65)

# Add the second ROC curve to the plot
plot(roc2, col = "red", add = TRUE, print.auc = TRUE, print.auc.y = 0.55) # Adjust print.auc.y as needed to avoid overlap
plot(roc3, col = "green", add = TRUE, print.auc = TRUE, print.auc.y = 0.45)
plot(roc4, col = "black", add = TRUE, print.auc = TRUE, print.auc.y = 0.35)
plot(roc5, col = "brown", add = TRUE, print.auc = TRUE, print.auc.y = 0.30)
# Add a legend
legend("bottomright", legend = c("Subtraction CT", "Baseline CT", 'Week3 CT', 'CITOR NTCP', 'Transfer'), col = c("blue", "red", "green", 'black', 'brown'), lty = 1)

############################################

