import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename

from app.modules.validation import validate_csv_file, REQUIRED_COLUMNS
from app.modules.engine import DecisionEngine

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/')
def index():
    """Render the upload page."""
    return render_template('upload.html', required_columns=REQUIRED_COLUMNS)


@main.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and processing."""
    if 'file' not in request.files:
        flash('No file selected. Please choose a CSV file to upload.', 'error')
        return redirect(url_for('main.index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected. Please choose a CSV file to upload.', 'error')
        return redirect(url_for('main.index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a CSV file.', 'error')
        return redirect(url_for('main.index'))
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    is_valid, df, errors = validate_csv_file(filepath)
    
    if not is_valid:
        for error in errors:
            flash(f'{error.error_type}: {error.message} {error.details or ""}', 'error')
        os.remove(filepath)
        return redirect(url_for('main.index'))
    
    engine = DecisionEngine()
    results = engine.evaluate_dataset(df)
    
    results_data = [result.to_dict() for result in results]
    rules_summary = engine.get_rules_summary()
    
    total_records = len(results_data)
    
    os.remove(filepath)
    
    return render_template(
        'results.html',
        results=results_data,
        rules=rules_summary,
        total_records=total_records,
        filename=filename
    )


@main.route('/rules')
def view_rules():
    """Display the configured decision rules."""
    engine = DecisionEngine()
    rules = engine.get_rules_summary()
    return render_template('rules.html', rules=rules)
