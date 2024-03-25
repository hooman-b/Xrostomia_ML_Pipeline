
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
library(lmSubsets)

###### import the necessary functions ###### 
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\forward_sel_logistic.R")
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\univariable.analysis.R")
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\preselection_correlation_v2.R")

###### open the proper file ###### 
DATA_num <- read.xlsx("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\Preprocessing\\Delta_radiomics\\Feature_extraction_factory\\train_main.xlsx")

###### preprocessing the data ######

# make a label name(y)
ynam="xer_12"
DATA = DATA_num[,!colnames(DATA_num) %in% c("X1")]

#DATA$delta_surf_mc = (DATA$delta_surf_mc+240.9)/1000


###### CITOR model ###### 
# Use the coefficents of feature forward selection to make a Logistic Regression model
dd <- datadist(DATA);options(datadist='dd')

######## xer_06
## --- construct the formula  from CITOR --- #MODIFY
b0= -3.305 #-1.853 # <- Intercept
b1= 1.936 #1.574   #<- Xer bsl
b2= 0.054 #0.034   #<- PG Dose
b3= -0.360 #-0.228 #<- Delta-surf PG

DATA$lp.ref= b0+
  b1*DATA$xer_bsl+
  b2*DATA$Contra_Dmean+
  b3*DATA$delta_surf_dlc


######## 

# Extract and plot the NTCP model
NTCP=1/(1+exp(-DATA$lp.ref));

# plot the NTCP values in order

plot(NTCP[order(NTCP)],col=c("black","red")[1+DATA$xer_12[order(NTCP)]],type= 'p',pch = c(16,16))

# make there model and fit the model
Model <- lrm(DATA$xer_12 ~ lp.ref, x = T, y = T, data = DATA); Model

#prdict by using this model
predict.fit <- predict(Model, type="fitted")

# Find all the elements related to ROC curve for this model
ROC_auc = roc(DATA$xer_12, NTCP, ci=T, plot=T)
ROC_auc1 = roc(DATA$xer_12, NTCP, ci=T, plot=T)

# implement Hosmer-Lemeshow goodness-of-fit (GOF) test to evaluate the goodness of the fit of the model
HL.test <-  hoslem.test(DATA$xer_12, NTCP);HL.test

# Save model predictions to a CSV file
write.csv(Model, file = "model1_predictions_06.csv")

###### Calibration plot ###### 

HL.test = hoslem.test(DATA_num$xer_12, 1/(1+exp(-DATA$lp.ref)), g=10)
N <- HL.test$observed[, 1] + HL.test$observed[, 2]
obs.rate <- HL.test$observed[, 2]/N
pred.rate <- HL.test$expected[, 2]/N
Calibration_DATA <- data.frame(pred.rate,obs.rate)
Linear_Calibration_fit <- lm(obs.rate ~ pred.rate, data = Calibration_DATA)

Points <- data.frame(row.names = c(1:length(Calibration_DATA$pred.rate)), Calibration_DATA$pred.rate, Calibration_DATA$obs.rate)
label1 = sprintf("HL (p-value) = %.2f (%.2f)", HL.test$statistic, HL.test$p.value)
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

# Save the plot as an image file (e.g., PNG)
ggsave("calibration_plot.png", plot = last_plot(), width = 10, height = 8, units = "in", dpi = 300)

##################################### TWO AUC in one plot
# Create ROC curves for your two sets of data
roc1 <- roc(DATA$xer_12, NTCP, ci = TRUE, plot = FALSE)
roc2 <- roc(Other_DATA$xer_12, Other_NTCP, ci = TRUE, plot = FALSE)

# Plot the first ROC curve
plot(ROC_auc, col = "blue", main = "ROC Curve Comparison (MC Vs DLC)", xlab = "False Positive Rate", ylab = "True Positive Rate", print.auc = TRUE)

# Add the second ROC curve to the plot
plot(ROC_auc1, col = "red", add = TRUE, print.auc = TRUE, print.auc.y = 0.25) # Adjust print.auc.y as needed to avoid overlap

# Add a legend
legend("bottomright", legend = c("MC", "DLC"), col = c("blue", "red"), lty = 1)

############################################


########### Refit the model by using the main dataset #############

# Initial model using lrm
fitted_model <- lrm(xer_12 ~ xer_bsl+ Contra_Dmean + delta_surf_dlc, data = DATA)
fitted_model
summary(fitted_model)

b00= -3.9608 # <- Intercept
b11= 1.6878 #<- Xer bsl
b22= 0.0861 #<- PG Dose
b33= -0.2743

b00= -4.2534 # <- Intercept
b11= 1.7979 #<- Xer bsl
b22= 0.1230 #<- PG Dose
b33= -0.0340

# Main model
b00= -1.5869  # <- Intercept
b11= 1.9216 #<- Xer bsl
b22= 0.0186 #<- PG Dose
b33= 0.0165

lp.ref1 = b00 + b11*DATA$xer_bsl + b22*DATA$Contra_Dmean + b33*DATA$delta_surf_dlc
######## 

# make there model and fit the model
Model <- lrm(DATA$xer_12 ~ lp.ref1, x = T, y = T, data = DATA); Model


# Extract and plot the NTCP model
NTCP=1/(1+exp(-lp.ref1));

# plot the NTCP values in order
plot(NTCP[order(NTCP)],col=c("black","red")[1+DATA$xer_12[order(NTCP)]],type= 'p',pch = c(16,16))

#prdict by using this model
predict.fit <- predict(fitted_model, type="fitted")

# Find all the elements related to ROC curve for this model
ROC_auc = roc(DATA$xer_12, NTCP, ci=T, plot=T)
ROC_auc1 = roc(DATA$xer_12, NTCP, ci=T, plot=T)



# implement Hosmer-Lemeshow goodness-of-fit (GOF) test to evaluate the goodness of the fit of the model
HL.test <-  hoslem.test(DATA$xer_12, NTCP);HL.test

# Save model predictions to a CSV file
write.csv(Model, file = "model1_predictions_06.csv")

###### Calibration plot ###### 

HL.test = hoslem.test(DATA_num$xer_12, 1/(1+exp(-lp.ref1)), g=10)
N <- HL.test$observed[, 1] + HL.test$observed[, 2]
obs.rate <- HL.test$observed[, 2]/N
pred.rate <- HL.test$expected[, 2]/N
Calibration_DATA <- data.frame(pred.rate,obs.rate)
Linear_Calibration_fit <- lm(obs.rate ~ pred.rate, data = Calibration_DATA)

Points <- data.frame(row.names = c(1:length(Calibration_DATA$pred.rate)), Calibration_DATA$pred.rate, Calibration_DATA$obs.rate)
label1 = sprintf("HL (p-value) = %.2f (%.2f)", HL.test$statistic, HL.test$p.value)
label2 = sprintf("y = %.2f + %.2fx", Linear_Calibration_fit$coefficients[1], Linear_Calibration_fit$coefficients[2])
Calibration_DATA$lm = Linear_Calibration_fit$coefficients[1] + Linear_Calibration_fit$coefficients[2] * Calibration_DATA$pred.rate

ggplot(Points, aes(x = pred.rate, y = obs.rate)) +
  geom_point(size = 3) +
  labs(x= "Predicted rate", y = "Observed rate") + 
  ggtitle("Calibration plot Delta-radiomics NTCP using DLC") +
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

# Save the plot as an image file (e.g., PNG)
ggsave("calibration_plot.png", plot = last_plot(), width = 10, height = 8, units = "in", dpi = 300)

