import os
import csv
import io
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, Response
from werkzeug.utils import secure_filename

from app.modules.validation import validate_csv_file, REQUIRED_COLUMNS
from app.modules.engine import DecisionEngine
from app.modules.database import (
    save_evaluation_run, 
    get_evaluation_runs, 
    get_run_results,
    get_classification_summary
)

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'csv'}
RECORDS_PER_PAGE = 20


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
    results, metrics = engine.evaluate_dataset(df)
    
    results_data = [result.to_dict() for result in results]
    rules_summary = engine.get_rules_summary()
    metrics_data = metrics.to_dict()
    
    run_id = save_evaluation_run(filename, results_data, metrics_data)
    
    classification_summary = get_classification_summary(run_id)
    
    total_records = len(results_data)
    
    os.remove(filepath)
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    start_idx = (page - 1) * RECORDS_PER_PAGE
    end_idx = start_idx + RECORDS_PER_PAGE
    paginated_results = results_data[start_idx:end_idx]
    total_pages = (total_records + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE
    
    return render_template(
        'results.html',
        results=paginated_results,
        all_results=results_data,
        rules=rules_summary,
        total_records=total_records,
        filename=filename,
        run_id=run_id,
        classification_summary=classification_summary,
        metrics=metrics_data,
        page=page,
        total_pages=total_pages
    )


@main.route('/rules')
def view_rules():
    """Display the configured decision rules."""
    engine = DecisionEngine()
    rules = engine.get_rules_summary()
    thresholds = engine.get_classification_thresholds()
    return render_template('rules.html', rules=rules, thresholds=thresholds)


@main.route('/history')
def view_history():
    """Display previous evaluation runs."""
    runs = get_evaluation_runs()
    return render_template('history.html', runs=runs)


@main.route('/history/<int:run_id>')
def view_run(run_id):
    """View results from a specific evaluation run."""
    run_data = get_run_results(run_id)
    
    if not run_data:
        flash('Evaluation run not found.', 'error')
        return redirect(url_for('main.view_history'))
    
    classification_summary = get_classification_summary(run_id)
    
    engine = DecisionEngine()
    rules = engine.get_rules_summary()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    total_records = run_data['total_records']
    start_idx = (page - 1) * RECORDS_PER_PAGE
    end_idx = start_idx + RECORDS_PER_PAGE
    paginated_results = run_data['results'][start_idx:end_idx]
    total_pages = (total_records + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE
    
    return render_template(
        'results.html',
        results=paginated_results,
        rules=rules,
        total_records=total_records,
        filename=run_data['filename'],
        run_id=run_id,
        classification_summary=classification_summary,
        metrics=run_data.get('metrics'),
        is_historical=True,
        page=page,
        total_pages=total_pages
    )


@main.route('/export/<int:run_id>')
def export_csv(run_id):
    """Export evaluation results to CSV file."""
    run_data = get_run_results(run_id)
    
    if not run_data:
        flash('Evaluation run not found.', 'error')
        return redirect(url_for('main.view_history'))
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Record_ID', 'Score', 'Classification', 'Explanation'])
    
    # Write data rows
    for result in run_data['results']:
        writer.writerow([
            result['record_id'],
            result['score'],
            result['classification'],
            result['explanation'].replace('\n', ' | ')
        ])
    
    # Create response
    output.seek(0)
    filename = f"evaluation_results_{run_id}.csv"
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
