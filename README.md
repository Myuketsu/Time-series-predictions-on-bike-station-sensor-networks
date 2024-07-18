# 🚲 Statistical learning in a sensor network and application to the reconstruction of the temporal dynamics of self-service bicycle stations

## 🌟 Introduction

In this project, it is proposed to focus on observations that are collected in the form of the number of bikes available over time at all self-service bike stations in a city that offers this type of service. This is the framework for spatio-temporal data observation that can be found in many application domains, in particular on the open data platforms recently created by many municipalities.

We are concerned with the situation where certain data recording sensors are not working (for example, to save energy), resulting in missing observations at several stations in a city over a given period of time. The aim is to develop methods for estimating the number of bicycles available (with confidence intervals) at stations where sensors are faulty, based on observations available at other stations. To achieve this, we will use an approach based on penalized linear regression using data structured as a spatial network (i.e. a graph whose vertices are the positions of the stations and whose edges represent the connections between the stations). The first part of the project will focus on studying the structure of the sensor network graph. The second part will focus on extending the usual linear model for smooth interpolation of data on graphs.

## 📙 What we did

We have developed an interactive dashboard using **Dash** (Python) for the analysis of bicycle stations in Toulouse.  
The interactive dashboard is available at: https://tlavandierter.nw.r.appspot.com/  
This dashboard integrates several functionalities, including descriptive statistics, Principal Component Analysis (PCA) and predictions on bicycle use.

The prediction part exploits various machine learning models, such as random forests, XGBoost and others. In order to make these models accessible on the site without exceeding a 512 MB limit, we optimized each model for each bike station. This approach enabled us to guarantee optimal performance while respecting memory constraints.

## ⚙️ Installation

Download all the libraries we'll be using with the command: `pip install -r requirements.txt`.
Finally, run the Python file `app.py` and that's it! (The site will take some time to launch the first time, as it needs to train all the models).
You can view the site from the link when `app.py` is launched: http://127.0.0.1:8050/

## 🔍 Data mining & Conclusion

Nous avons réalisé une analyse détaillée et élaboré un rapport complet [`Rapport.pdf`] qui présente le sujet en profondeur. Ce rapport inclut une exploration exhaustive des données ainsi qu'une section dédiée aux prédictions.

## 👥 Authors
- Théo Lavandier
- Alexandre Leys
- Mathilde Tissandier