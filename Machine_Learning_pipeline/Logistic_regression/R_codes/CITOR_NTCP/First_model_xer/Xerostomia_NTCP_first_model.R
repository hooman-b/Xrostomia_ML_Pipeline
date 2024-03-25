#' **This is my first NTCP model in R**
#' In this very first model, I consider the following assumptions:
#' 1. I just erase all the samples that have any null value in the features or label
#' 2. I just slice all the parotid, submandibular, mucosa, and baseline, and implement
#'    the pipeline on them.
#' 3. I implement the whole pipeline both for 6 month and twelve-month xerostomia
#'    endpoints.
#' 4. I did not slice my dataset into train and test dataset here. 
#' 5. I followed the following pipeline here.
#'    univariable analysis (without slicing features) --> forward feature extraction --> Logistic Regression

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
library(writexl)

###### import the necessary functions ###### 
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\forward_sel_logistic.R")
source("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\Hendrike_scripts\\univariable_logistic_regression.R")

###### open the proper file ###### 
DATA <- read.xlsx("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\Preprocessing\\CITOR\\first_train_06.xlsx")
DATA_test <- read.xlsx("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\Preprocessing\\CITOR\\first_test_06.xlsx")

###### univariable analysis ###### 

# make a label name(y)
ynam="xer_06"

# separate column names that are not the label or background information (mainly mean dose features)
feats_of_interest=colnames(DATA)[!colnames(DATA) %in% c(ynam,"X1")]

# slice the data  that contains only mean doses and label
DATA_num=DATA[,!colnames(DATA) %in% c("X1")]

# define the distribution type here.
dd <- datadist(DATA_num);options(datadist='dd')

# this implement a univariable logistic regression model for each feature based on the label. 
oo=univariable_logistic_regression(DATA_num,ynam)

# this is just a regular print statement that prints the number of significant univariable models in
print(round(oo,3)); cat("\n","Univariable significant: ", nrow(oo[oo[,'p_LRT']<0.05,])," of ", nrow(oo))

###### forward feature selection ###### 

# assign values to the parameters of this function
outputdir = 'C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\CITOR NTCP\\First_model_xer\\'

run_i=0;
outputdirf=paste0(outputdir,"forwards_selection\\")

# This parameter saves all the information in an excel file
excel_export=0

# This parameter determines the number of bootstraps one wants use during forward feature extraction.
boot=1000
go=forward_sel_logistic(DATA_num,ynam,boot,excel_export,outputdirf,0.05)
round(go,2)
 
###### CITOR model ###### 
# Use the coefficents of feature forward selection to make a Logistic Regression model
dd <- datadist(DATA_num);options(datadist='dd')

######## xer_06
# Assign the coefficients
#b0.ref = -3.08 # intercept
#b1.ref = -0.15 # BuccalMucosa_Dmean 
#b2.ref = 1.73 # xer_bsl 
#b3.ref = 0.39 # Submandibular_R_Dmean  
#b4.ref = 0.29 # BuccalMucosa_L_Dmean     
#b5.ref = -0.08 # Submandibular_L_Dmean   

#DATA_num$lp.ref = b0.ref + b1.ref * DATA_num$BuccalMucosa_Dmean + b2.ref * DATA_num$xer_bsl + b3.ref * DATA_num$Submandibular_R_Dmean + b4.ref * DATA_num$BuccalMucosa_L_Dmean + b5.ref * DATA_num$Submandibular_L_Dmean
######## 

######## xer_12
# Assign the coefficients
#b0.ref = -2.61 # intercept
#b1.ref = 1.86 # xer_bsl 
#b2.ref = 0.20 # OralCavity_Ext_Dmean     
#b3.ref = 0.11  # Submandibular_R_Dmean       

#DATA_num$lp.ref = b0.ref + b1.ref * DATA_num$xer_bsl + b2.ref * DATA_num$OralCavity_Ext_Dmean + b3.ref * DATA_num$Submandibular_R_Dmean
######## 

######## xer_06 (train-test)
# Assign the coefficients
b0.ref = -3.28 # intercept
b1.ref = 0.08 # Parotid_Dmean           
b2.ref = 1.64 # xer_bsl                     
b3.ref = 0.29  # Submandibular_R_Dmean         
b4.ref = 0.11  # BuccalMucosa_L_Dmean   
DATA_num$lp.ref = b0.ref + b1.ref * DATA_num$Parotid_Dmean + b2.ref * DATA_num$xer_bsl + b3.ref * DATA_num$Submandibular_R_Dmean + 
                  b4.ref * DATA_num$BuccalMucosa_L_Dmean
######## 


# Extract and plot the NTCP model
NTCP=1/(1+exp(-DATA_num$lp.ref));

# plot the NTCP values in order
plot(NTCP[order(NTCP)],col=c("black","red")[1+DATA$xer_06[order(NTCP)]],type= 'p',pch = c(16,16))

# make the model and fit the model
Model <- lrm(DATA_num$xer_06 ~ lp.ref, x = T, y = T, data = DATA_num); Model

# prdict by using this model
predict.fit <- predict(Model, type="fitted")

# Find all the elements related to ROC curve for this model
ROC_auc = roc(DATA$xer_06, NTCP, ci=T, plot=T)

# implement Hosmer-Lemeshow goodness-of-fit (GOF) test to evaluate the goodness of the fit of the model
hl.enter <-  hoslem.test(DATA$xer_06, predict.fit);hl.enter

# Save model predictions to a CSV file
write.csv(Model, file = "model1_predictions_06.csv")


###### Calibration plot ###### 
HL.test = hoslem.test(DATA_num$xer_06, 1/(1+exp(-DATA_num$lp.ref)), g=10)
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



###### Test the testing dataset (if available) ######

DATA_test$lp.ref = b0.ref + b1.ref * DATA_test$Parotid_Dmean + b2.ref * DATA_test$xer_bsl + b3.ref * DATA_test$Submandibular_R_Dmean + 
  b4.ref * DATA_test$BuccalMucosa_L_Dmean

NTCP_test=1/(1+exp(-DATA_test$lp.ref));

# plot the NTCP values in order
plot(NTCP_test[order(NTCP_test)],col=c("black","red")[1+DATA_test$xer_06[order(NTCP_test)]],type= 'p',pch = c(16,16))

# Make predictions on the test dataset
DATA_test$predicted_labels <- predict(Model, newdata = DATA_test, type = "fitted")

# The "predicted_labels" column now contains the predicted labels (probabilities or scores).

# If you want binary predictions, you can set a threshold (e.g., 0.5) to classify as 1 or 0.
DATA_test$binary_predictions <- ifelse(DATA_test$predicted_labels >= 0.5, 1, 0)


# Find all the elements related to ROC curve for this model
ROC_auc = roc(DATA_test$xer_06, NTCP_test, ci=T, plot=T)

# implement Hosmer-Lemeshow goodness-of-fit (GOF) test to evaluate the goodness of the fit of the model
hl.enter <-  hoslem.test(DATA_test$xer_06, DATA_test$predicted_labels);hl.enter

###### Calibration plot ###### 
HL.test = hoslem.test(DATA_test$xer_06, 1/(1+exp(-DATA_test$lp.ref)), g=10)
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

print(DATA_test$binary_predictions)
print(DATA_test$xer_06)

