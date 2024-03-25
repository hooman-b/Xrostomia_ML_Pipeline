


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
source("C:\\Users\\BahrdoH\\Hooman\\NTCP\\R-script example\\forward_sel_logistic.R")
source("C:\\Users\\BahrdoH\\Hooman\\NTCP\\R-script exampleunivariable.analysis.R")
source("C:\\Users\\BahrdoH\\Hooman\\NTCP\\R-script example\\preselection_correlation_v2.R")

###### open the proper file ###### 
DATA <- read.xlsx("C:\\Users\\BahrdoH\\OneDrive - UMCG\\Hooman\\Models\\Preprocessing\\Delta_radiomics\\Feature_extraction_factory\\Sanne_12month_df1.xlsx")

###### preprocessing the data ######

# make a label name(y)
ynam="xer_12"
DATA_num=DATA[,!colnames(DATA) %in% c("X1")]

###### preselection analysis ###### 
# evaluate the correlation between features
dd <- datadist(DATA_num);options(datadist='dd')

pp = preselection_correlation(DATA_num, ynam)
pp

# Assign the name of the features of the interest based on preselection principles
feats_of_interest <- rownames(pp)
feats_of_interest <- c('Contra_Dmean_mc', 'delta_surf_mc', 'xer_bsl')
DATA_num <- DATA_num[, c(ynam, feats_of_interest)]


###### univariable analysis ###### 
# this implement a univariable logistic regression model for each feature based on the label. 
oo = univariable.analysis(DATA_num,ynam, feats_of_interest)
oo

# Save model predictions to a excel file
write_xlsx(oo$LL, path = "output_file.xlsx")


# implement the formula on each feature
for (i in 1:length(feats_of_interest)) {
  feat <- feats_of_interest[i]  # Extract the feature name from the vector
  
  # Use mutate with !!sym() and := to create or update columns dynamically
  DATA_num <- DATA_num %>%
    mutate(!!feat := eval(parse(text = oo$LL$formula[i])))
}

###### forward feature selection ###### 
# assign values to the parameters of this function
outputdir = 'C:\\Users\\BahrdoH\\Hooman\\NTCP\\R-script example\\Second_model_xer\\'

run_i=0;
outputdirf=paste0(outputdir,"forwards_selection\\")

# This parameter saves all the information in an excel file
excel_export=0

# This parameter determines the number of bootstraps one wants use during forward feature extraction.
boot=1
go=forward_sel_logistic(DATA_num,ynam,boot,excel_export,outputdirf,0.05)
round(go,2)


###### CITOR model ###### 
# Use the coefficents of feature forward selection to make a Logistic Regression model
dd <- datadist(DATA_num);options(datadist='dd')

######## xer_06
# Assign the coefficients
b0.ref = -2.9 # intercept
b1.ref = -0.2 # BuccalMucosa_Dmean 
b2.ref = 1.82   # xer_bsl 
b3.ref = 0.4   # Parotid_Dmean 
#b4.ref = -0.83 # gender    
#b5.ref = -0.52 # ROKEN  
#b6.ref = -0.83 # modality_adjusted       
#b7.ref = 2.39 # Submandibular_Dmean  

DATA_num$lp.ref = b0.ref + b1.ref * DATA_num$BuccalMucosa_Dmean + b2.ref * DATA_num$xer_bsl + b3.ref * DATA_num$Parotid_Dmean# + b4.ref * DATA_num$gender + b5.ref * DATA_num$ROKEN + b6.ref * DATA_num$modality_adjusted + b7.ref * DATA_num$Submandibular_Dmean
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


