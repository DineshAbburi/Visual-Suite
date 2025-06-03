# Flask Dashboard Application

This Flask application is designed for data management, visualization, and analysis. It provides functionalities to upload CSV files, preprocess data, visualize data using Plotly charts, handle duplicates, and perform statistical analysis.

## Features

- **User Authentication:** Allows users to register and log in securely.
- **Data Upload:** Upload CSV files and visualize the dataset.
- **Data Preprocessing:** Transform data with options for log transformation, Box-Cox transformation, standardization, normalization, one-hot encoding, and label encoding.
- **Visualization:** Gen erate various interactive Plotly charts (line, bar, scatter, heatmap) based on user-selected columns.
- **Data Analysis:** View statistics, handle duplicates, and analyze correlations between variables.
- **Dashboard:** Interactive dashboard with multiple tabs for different functionalities.
                     
## Technologies Used    
                     
- **Backend:** Flask, Python                              
- **Frontend:** HTML/CSS, Jinja2 templating               
- **Data Visualization:** Plotly, Plotly Dash             
- **Database:** MySQL                                     
- **Regression Analysis:** pycaret                        
- **Other Libraries:** pandas, scikit-learn, scipy             

## Setup Instructions

1. **Clone the repository:**    
   ```
   git clone https://github.com/DineshAbburi/Visual-Suite.git  
     
   ```
                            
2. **Install dependencies:**
   ```                      
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root directory with your MySQL credentials:  
     ```                                  
     MYSQL_HOST=your_mysql_host              
     MYSQL_USER=your_mysql_username           
     MYSQL_PASSWORD=your_mysql_password       
     MYSQL_DB=your_mysql_database              
     ```

4. **Run the application:**      
   ```                            
   python app.py                
   ```                         

5. **Access the application:**                             
   Open a web browser and go to `http://localhost:5000`      

 
