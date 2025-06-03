from flask import Flask, redirect, render_template, request, session, url_for, jsonify, flash ,Response
import pandas as pd
import plotly.express as px
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from functools import wraps
from sklearn.preprocessing import StandardScaler, normalize
from math import log
from scipy.stats import boxcox
from sklearn.preprocessing import LabelEncoder
import plotly
from dashApp import create_cm_dash, create_missing_dash_application, update_cm_dash, update_dash_app
from dashApp.statistics import create_stats_dash, update_stats_dash
from sklearn.linear_model import LinearRegression
import json
from pycaret.classification import setup, compare_models, evaluate_model, pull, load_model, save_model,create_model
from sklearn.linear_model import LinearRegression 
from sklearn.ensemble import RandomForestRegressor
import numpy as np                                
from sklearn.tree import DecisionTreeRegressor    
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor, BaggingRegressor, GradientBoostingRegressor, RandomForestClassifier
from lightgbm import LGBMRegressor              
import io
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from pandas.plotting import scatter_matrix

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'secretkey'


df = None


dash_app1 = create_missing_dash_application(app)
dash_app2 = create_cm_dash(app)
dash_app3 = create_stats_dash(app)



db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DB')
}


def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return redirect(url_for('login'))

 
@app.route('/login', methods=['GET', 'POST'])
def login(): 
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM login WHERE username = %s AND passwrd = %s', (username, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = 'Logged in successfully!'
                return redirect(url_for('dataPreview'))
            else:
                msg = 'Incorrect username / password!'
            cursor.close()
            connection.close()
        else:  
            msg = 'Could not connect to the database.'
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register(): 
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        re_password = request.form['re_password']
        email = request.form['email']

        if password != re_password:
            msg = 'Passwords do not match!'
        else:
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute('INSERT INTO login (username, passwrd, email) VALUES (%s, %s, %s)',
                               (username, password, email))
                connection.commit()
                cursor.close()
                connection.close()
                msg = 'You have successfully registered!'
                return render_template('login.html', msg=msg)
            else:
                msg = 'Could not connect to the database.'

    return render_template('register.html', msg=msg)


@app.route('/logout')
def logout():
    
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('preprocess_recommendation_shown', None)

    
    return redirect(url_for('login'))


@app.route('/dataPreview')
#@login_required
def dataPreview():
    return render_template('dataPreview.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    global df  
    global df_copy
    if 'file' not in request.files:
        return jsonify(error="No file part")

    file = request.files['file']
    if file.filename == '':
        return jsonify(error="No selected file")

    if file and file.filename.endswith('.csv'):
        try:
            
            df = pd.read_csv(file.stream, encoding='utf-8')
            df_copy=df.copy(deep=True)
        except UnicodeDecodeError:
           
            try:
                df = pd.read_csv(file.stream, encoding='latin-1')
            except Exception as e:
                return jsonify(error=f"Error reading CSV file: {str(e)}")
        update_dash_app(dash_app1,df)
        update_cm_dash(dash_app2,df)
        update_stats_dash(dash_app3,df)

       
        table_html = df.head(50).to_html(classes='data-table', header="true", index=False)
        return jsonify(full_table=table_html, filename=file.filename)

    return jsonify(error="Invalid file type")


@app.route('/dashboard')
#@login_required
def dashboard():
    global df

    if df is None:
        return redirect(url_for('dataPreview')) 

    
    if 'preprocess_recommendation_shown' not in session:
        flash('Preprocessing is recommended for better results!', 'info')
        session['preprocess_recommendation_shown'] = True

    
    highlight_preprocess = True

    
    columns_info = []
    for col in df.columns:
        col_info = {
            'name': col,
            'num_rows': len(df[col]),  
            'dtype': str(df[col].dtype)  
        }
        columns_info.append(col_info)

    
    initial_column = None
    initial_viz = None
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            initial_column = col
            
            #abs_col_values = df[initial_column].abs()
            fig = px.scatter(df, x=df.index, y=initial_column, #size=abs_col_values,
                             hover_name=df.index, log_y=True)
            fig.update_layout(height=600)  # Set initial height
            initial_viz = fig.to_html(full_html=False, default_height=400)
            break
#, size_max=60
    return render_template('dashboard.html', columns_info=columns_info,
                           highlight_preprocess=highlight_preprocess, initial_viz=initial_viz,
                           initial_column=initial_column)

@app.route('/get_visualization', methods=['POST'])
def get_visualization():
    global df

    if df is None or df.empty:
        return redirect(url_for('dataPreview'))  
    
    column_name = request.form.get('column')
    if not column_name:
        return jsonify({'error': 'No column specified'})
    
    if column_name not in df.columns:
        return jsonify({'error': f'Column {column_name} does not exist in the dataframe'})
    
    try:
        
        abs_col_values = df[column_name].abs()

        
        fig = px.scatter(df, y=column_name, x=df.index, #size=abs_col_values, 
                         hover_name=df.index, log_x=True, size_max=60)
        fig.update_layout(height=600)
        viz_html = fig.to_html(full_html=False, default_height=400)
        return jsonify({'visualization': viz_html})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/duplicates/', methods=['GET', 'POST'])
def duplicates():
    global df
    
    
    if df is None or df.empty:
        return redirect(url_for('dataPreview'))

    columns = df.columns.tolist()
    duplicates_info = {}
    selected_columns = []
    total_duplicates = 0
    new_df_html = None

    if request.method == 'POST':
        selected_columns = request.form.getlist('columns')
        action = request.form.get('action')

        if selected_columns:
            duplicate_rows = df[df.duplicated(subset=selected_columns, keep=False)]
            total_duplicates = duplicate_rows.shape[0]

            if action == 'show_duplicates':
                duplicates_info = duplicate_rows.groupby(selected_columns).size().to_dict()

            elif action == 'remove_duplicates':
                keep_option = request.form.get('keep', 'first')
                new_df = df.copy(deep=True)

                if keep_option == 'none':
                    new_df = new_df[~new_df.duplicated(subset=selected_columns, keep=False)]
                else:
                    new_df.drop_duplicates(subset=selected_columns, keep=keep_option, inplace=True)

                new_df_html = new_df.head(50).to_html(classes='data-table', header="true", index=False)
                df = new_df  

    return render_template('duplicates.html', columns=columns, duplicates_info=duplicates_info,
                           selected_columns=selected_columns, total_duplicates=total_duplicates,
                           new_df_html=new_df_html)


@app.route('/transformations', methods=['GET', 'POST'])
def transformations():
    global df
    global df_copy
    if df is None or df.empty:
        return redirect(url_for('dataPreview'))

    
    temp_df = df.copy(deep=True)
    original_df = df_copy.copy(deep=True)

    
    log_transformation_checked = session.get('log_transformation_checked', False)
    box_cox_transformation_checked = session.get('box_cox_transformation_checked', False)  
    standardization_checked = session.get('standardization_checked', False)
    normalization_checked = session.get('normalization_checked', False)
    selected_one_hot_column = session.get('selected_one_hot_column', '')
    selected_label_column = session.get('selected_label_column', '')

    if request.method == 'POST':
        
        log_transformation_checked = 'log_transformation' in request.form
        box_cox_transformation_checked = 'box_cox_transformation' in request.form
        standardization_checked = 'standardization' in request.form              
        normalization_checked = 'normalization' in request.form
        selected_one_hot_column = request.form.get('one_hot_column')
        selected_label_column = request.form.get('label_column')

        
        session['log_transformation_checked'] = log_transformation_checked
        session['box_cox_transformation_checked'] = box_cox_transformation_checked
        session['standardization_checked'] = standardization_checked
        session['normalization_checked'] = normalization_checked
        session['selected_one_hot_column'] = selected_one_hot_column
        session['selected_label_column'] = selected_label_column

        
        if log_transformation_checked: 
            for col in temp_df.columns:
                if pd.api.types.is_numeric_dtype(temp_df[col]):
                    temp_df[col] = temp_df[col].apply(lambda x: log(x) if x > 0 else 0)

        if box_cox_transformation_checked:  
            for col in temp_df.columns:     
                if pd.api.types.is_numeric_dtype(temp_df[col]) and (temp_df[col] > 0).all():
                    try:                   
                        temp_df[col], _ = boxcox(temp_df[col])                                  
                    except ValueError as e:                                                     
                        print(f"Could not apply Box-Cox transformation to column {col}: {e}") 

        if standardization_checked:
            scaler = StandardScaler()
            for col in temp_df.columns:
                if pd.api.types.is_numeric_dtype(temp_df[col]):
                    temp_df[col] = scaler.fit_transform(temp_df[[col]])

        if normalization_checked:      
            for col in temp_df.columns:
                if pd.api.types.is_numeric_dtype(temp_df[col]):   # Check if column is numeric
                    if temp_df[col].isnull().any():    # check if there are null 
                        median_value = temp_df[col].median()
                        temp_df[col].fillna(median_value, inplace=True)
                        flash(f"NaN values in '{col}' were replaced with median ({median_value}).", "info")
        
                    temp_df[[col]] = normalize(temp_df[[col]], axis=0)    
                else:
                    flash("Contains NaN Values")
                

        if selected_one_hot_column:
            temp_df = pd.get_dummies(temp_df, columns=[selected_one_hot_column])

        if selected_label_column:
            le = LabelEncoder()
            temp_df[selected_label_column] = le.fit_transform(temp_df[selected_label_column])

        
        if not log_transformation_checked and not box_cox_transformation_checked and not standardization_checked \
                and not normalization_checked and not selected_one_hot_column and not selected_label_column:
            temp_df = original_df.copy(deep=True)

        
        df = temp_df
        update_dash_app(dash_app1,df)
        update_cm_dash(dash_app2,df)
        update_stats_dash(dash_app3,df)
    
    table_html = temp_df.head(50).to_html(classes='data-table', header="true", index=False)

    return render_template('transformations.html', df=table_html,
                           log_transformation_checked=log_transformation_checked,
                           box_cox_transformation_checked=box_cox_transformation_checked,
                           standardization_checked=standardization_checked,
                           normalization_checked=normalization_checked,
                           selected_one_hot_column=selected_one_hot_column,
                           selected_label_column=selected_label_column,
                           columns=temp_df.columns)

@app.route('/charts', methods=['GET', 'POST'])
def charts():
    global df  

    if df is None or df.empty:
        return redirect(url_for('dataPreview'))  
    columns = df.columns.tolist()
    return render_template('charts.html', columns=columns)


@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    global df
    
    data = request.get_json()
    x_axis = data.get('x_axis')
    y_axis = data.get('y_axis')
    chart_type = data.get('chart_type')

    print(f"Received data: x_axis={x_axis}, y_axis={y_axis}, chart_type={chart_type}")

    if df is None or x_axis not in df.columns or y_axis not in df.columns:
        return jsonify({'error': 'Invalid columns selected'})

    try:
        if chart_type == 'line':
            fig = px.line(df, x=x_axis, y=y_axis, title=f'{y_axis} vs {x_axis}')
        elif chart_type == 'bar':
            fig = px.bar(df, x=x_axis, y=y_axis, title=f'{y_axis} vs {x_axis}')
        elif chart_type == 'scatter':
            fig = px.scatter(df, x=x_axis, y=y_axis, title=f'{y_axis} vs {x_axis}')
        elif chart_type == 'heatmap':
            fig = px.density_heatmap(df, x=x_axis, y=y_axis, title=f'{y_axis} vs {x_axis} (Heatmap)')

        graph_json = fig.to_json()  
        return jsonify({'data': graph_json})  
    except Exception as e:
        return jsonify({'error': str(e)})





@app.route('/correlation', methods=['GET', 'POST'])
def correlation():
    if df is None or df.empty:
        return redirect(url_for('dataPreview'))  
    return redirect('/correlationmatrix/')


@app.route('/missingvalues', methods=['GET', 'POST'])
def missingvalues():
    if df is None or df.empty:
        return redirect(url_for('dataPreview')) 
    return redirect('/missingvalue/')


@app.route('/describe', methods=['GET', 'POST'])
def describe():
    if df is None or df.empty:
        return redirect(url_for('dataPreview'))  
    return redirect('/statistics/')

@app.route('/regression', methods=['GET'])
def regression():
    global df
    if df is None or df.empty:
        return redirect(url_for('dataPreview')) 
    columns = df.select_dtypes(include='number').columns.tolist()
    return render_template('regression.html', columns=columns)

@app.route('/run_regression', methods=['POST'])
def run_regression():
    global df

    try:
        if df is None or df.empty:
            return jsonify({'error': 'No data available. Please upload a dataset.'})

        dependent_variable = request.form['dependent_variable']
        independent_variables = request.form.getlist('independent_variable')
        regression_model = request.form['regression_model']

        if not dependent_variable or not independent_variables or not regression_model:
            return jsonify({'error': 'Please provide all required inputs (dependent variable, independent variables, and regression model).'})

        X = df[independent_variables]
        y = df[dependent_variable]

        model = None
        model_type = 'linear'
        if regression_model == 'linear_regression':
            model = LinearRegression()
        elif regression_model == 'decision_tree':
            model = DecisionTreeRegressor()
            model_type = 'tree'
        elif regression_model == 'random_forest':
            model = RandomForestRegressor()
            model_type = 'ensemble'
        elif regression_model == 'adaboost':
            model = AdaBoostRegressor()
            model_type = 'ensemble'
        elif regression_model == 'bagging':
            base_model = DecisionTreeRegressor()
            model = BaggingRegressor(base_model)
            model_type = 'ensemble'
        elif regression_model == 'gradient_boosting':
            model = GradientBoostingRegressor()
            model_type = 'ensemble'
        elif regression_model == 'lightgbm':
            model = LGBMRegressor()
            model_type = 'ensemble'
        else:
            return jsonify({'error': 'Invalid regression model selected'})

        model.fit(X, y)

        plot_data = {}
        pair_plot_data = {}
        correlation_heatmap_data = {}

        if len(independent_variables) == 1:
            x_values = df[independent_variables[0]]
            fig = px.scatter(x=x_values, y=model.predict(X), labels={'x': independent_variables[0], 'y': 'Predicted'})
            plot_data = json.loads(fig.to_json())
        else:
            pair_plot = px.scatter_matrix(df, dimensions=independent_variables, color=dependent_variable)
            correlation_heatmap = px.imshow(df[independent_variables + [dependent_variable]].corr(), text_auto=True)
            pair_plot_data = json.loads(pair_plot.to_json())
            correlation_heatmap_data = json.loads(correlation_heatmap.to_json())

        result = {}
        if model_type == 'linear':
            result['intercept'] = round(model.intercept_, 2)
            result['coefficients'] = [round(coef, 2) for coef in model.coef_]
        elif model_type in ['tree', 'ensemble']:
            if hasattr(model, 'feature_importances_'):
                result['feature_importances'] = [round(importance, 2) for importance in model.feature_importances_]
            elif hasattr(model, 'base_estimator_') and hasattr(model.base_estimator_, 'feature_importances_'):
                result['feature_importances'] = [round(importance, 2) for importance in model.base_estimator_.feature_importances_]
            else:
                return jsonify({'error': 'Model does not support feature importances.'})

        result.update({
            'plot_data': plot_data,
            'pair_plot_data': pair_plot_data,
            'correlation_heatmap_data': correlation_heatmap_data
        })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/featureimportance', methods=['GET', 'POST'])
def featureimportance():
    global df

    if df is None or df.empty:
        print("Redirecting to dataPreview: df is None or empty")
        return redirect(url_for('dataPreview'))  # Redirect if no dataset is uploaded

    setup_df = df.copy()
    target_column = None
    model_type = None
    feature_importances_html = None
    columns = setup_df.columns.tolist()  # Keep columns list for rendering dropdown options

    if request.method == 'POST':
        target_column = request.form.get('target_column')
        model_type = request.form.get('model_type')

        print(f"Selected target column: {target_column}")
        print(f"Selected model type: {model_type}")

        if target_column and target_column in setup_df.columns:
            try:
                numeric_df = setup_df.select_dtypes(include=[np.number])
                if target_column not in numeric_df.columns:
                    numeric_df[target_column] = setup_df[target_column]

                X = numeric_df.drop(columns=[target_column])
                y = numeric_df[target_column]

                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)

                if model_type == 'random_forest':
                    model = RandomForestRegressor()
                elif model_type == 'linear_regression':
                    model = LinearRegression()
                else:
                    raise ValueError("Invalid model type selected")

                model.fit(X_scaled, y)
                if model_type == 'random_forest':
                    importances = model.feature_importances_
                elif model_type == 'linear_regression':
                    importances = np.abs(model.coef_)

                feature_importances = pd.DataFrame({
                    'Feature': X.columns,
                    'Importance': [round(imp, 2) for imp in importances]
                }).sort_values(by='Importance', ascending=False)

                feature_importances_html = feature_importances.to_html(classes='data-table', header="true", index=False)
                session['feature_importances_html'] = feature_importances_html

            except Exception as e:
                print(f"Error occurred: {e}")
                flash(f"An error occurred: {e}", 'danger')

    feature_importances_html = session.get('feature_importances_html', None)

    return render_template('featureimportance.html', 
                           columns=columns,  
                           feature_importances_html=feature_importances_html, 
                           target_column=target_column, 
                           model_type=model_type)

    
@app.route('/comparativeanalysis', methods=['GET', 'POST'])
def comparativeanalysis():
    global df

    if df is None or df.empty:
        print("Redirecting to dataPreview: df is None or empty")
        return redirect(url_for('dataPreview'))  # Redirect if no dataset is uploaded

    setup_df = df.copy()
    target_column = None
    evaluate_model_html = None  # To store the evaluate_model output

    if request.method == 'POST':
        target_column = request.form.get('target_column')

        print(f"Selected target column: {target_column}")

        if target_column and target_column in setup_df.columns:
            try:
                print("Setting up PyCaret for regression")
                from pycaret.regression import setup, compare_models, pull, save_model
                
                setup(data=setup_df, target=target_column, verbose=False)
                
                print("Comparing models")
                best_model = compare_models()
                results_df = pull()
                
                print("Saving the best model")
                save_model(best_model, 'best_model')

                results_html = results_df.to_html(classes='data-table', header="true", index=False)
                session['results_html'] = results_html

                print("Results HTML:")
                return render_template('companalysis.html', target_column=target_column,
                                       columns=setup_df.columns.tolist(),
                                       results_html=results_html, evaluate_model_html=evaluate_model_html)

            except Exception as e:
                print(f"Error occurred: {e}")
                flash(f"An error occurred: {e}", 'danger')

    columns = df.columns.tolist()
    print("Columns available for selection:")
    print(columns)

    results_html = session.get('results_html', None)

    return render_template('companalysis.html', columns=columns, results_html=results_html)

@app.route('/export_data', methods=['GET'])
def export_data():
    global df
    
    if df is None:
        flash('No dataset available to export!', 'error')     
        return redirect(url_for('dashboard'))
    
    # Create a CSV file in memory
    output = io.StringIO()
    df.to_csv(output, index=False) 
    
    # Set up response headers
    response = Response(
        output.getvalue(),
        headers={
            "Content-Disposition": "attachment; filename=dataset.csv",
            "Content-Type": "text/csv"
        }
    )
    
    return response

@app.route('/predict', methods=['POST'])
def predict():
    global df
    
    data = request.form.to_dict()
    dependent_variable = data.get('prediction_column')
    independent_variables = request.form.getlist('independent_columns')
    input_values = list(map(float, data.get('prediction_input').split(',')))

    if df is None or dependent_variable not in df.columns or not all(var in df.columns for var in independent_variables):
        return jsonify(error="Invalid columns selected")

    try:
        X = df[independent_variables].values
        y = df[dependent_variable].values

        model = LinearRegression()
        model.fit(X, y)

        predicted_value = model.predict([input_values])[0]

        # Calculate metrics 
        r2 = r2_score(y, model.predict(X))
        mse = mean_squared_error(y, model.predict(X))
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(y, model.predict(X))

        return jsonify(   
            prediction=predicted_value,
            r2=r2,    
            mse=mse,  
            rmse=rmse,  
            mape=mape 
        )

    except Exception as e:
        return jsonify(error=str(e))
    
def generate_report(df):
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
            
            
        # Label encode all object columns
        df_encoded = df.copy()
        for col in df_encoded.select_dtypes(include=['object']).columns:
            df_encoded[col] = LabelEncoder().fit_transform(df_encoded[col].astype(str))

        
        # 1. Correlation Matrix
        plt.figure(figsize=(10, 8))
        corr = df.corr(numeric_only=True)
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title("Correlation Matrix")
        pdf.savefig()
        plt.close()
        
        # 2. Pair Plot
        
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if not numeric_df.empty:
            pairplot_fig = sns.pairplot(numeric_df)
            pairplot_fig.fig.suptitle("Pair Plot", y=1.02)
            pdf.savefig(pairplot_fig.fig)
            plt.close()
        


      
        # 3. Feature Importance (for classification)
        # Drop rows with NaNs and encode labels
        clean_df = df_encoded.dropna()
        if clean_df.shape[1] >= 2:
            target = clean_df.columns[-1]  # Use last column as target
            X = clean_df.drop(columns=[target])
            y = clean_df[target]

            model = RandomForestClassifier()
            model.fit(X, y)
            importances = model.feature_importances_
            feature_names = X.columns
            importance_df = pd.DataFrame({
                'Feature': feature_names,
                'Importance Score': importances
            }).sort_values(by='Importance Score', ascending=False)

            # Plot table
            fig, ax = plt.subplots(figsize=(10, len(importance_df) * 0.4 + 1))
            ax.axis('off')
            table = ax.table(cellText=importance_df.values,
                             colLabels=importance_df.columns,
                             loc='center',
                             cellLoc='left')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.2)
            plt.title("Feature Importance Table", fontsize=14, pad=10)
            pdf.savefig()
            plt.close()
    
    pdf_buffer.seek(0)
    return pdf_buffer

@app.route('/download_report', methods=['GET'])
def download_report():
    global df

    if df is None or df.empty:
        flash('No data available to generate the report.', 'error')
        return redirect(url_for('dashboard'))

    pdf_buffer = generate_report(df)

    return Response(
        pdf_buffer,
        mimetype='application/pdf',
        headers={
            "Content-Disposition": "attachment; filename=eda_report.pdf",
            "Content-Type": "application/pdf"
        }
    )




# Run application         
if __name__ == '__main__':
    app.run(debug=True)    

#D:\EY-Suite\EY-Suite\EDA-Visualization-Suite\Visual Suite>"C:\Program Files\Python39\python.exe" app.py
#venv\Scripts\activate
#deactivate
#  & "C:\Program Files\Python39\python.exe" "app.py"                                           
# cd + Tab to toggle   + line above



