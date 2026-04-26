import os
import csv
import io
import json
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, Response, jsonify
from werkzeug.utils import secure_filename

from app.modules.validation import validate_csv_file, REQUIRED_COLUMNS
from app.modules.engine import DecisionEngine
from app.modules.database import (
    save_evaluation_run,
    get_evaluation_runs,
    get_run_results,
    get_classification_summary,
    get_dashboard_stats,
)

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'csv'}
RECORDS_PER_PAGE = 20


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _normalize_results(results: list) -> list:
    """Ensure every result dict uses 'score' (not 'total_score') for consistency."""
    for r in results:
        if 'total_score' in r and 'score' not in r:
            r['score'] = r['total_score']
    return results


def _score_distribution(results: list) -> dict:
    """Bucket scores into ranges for the histogram chart."""
    buckets = {
        'Negative': 0,
        '0–9': 0,
        '10–19': 0,
        '20–29': 0,
        '30–39': 0,
        '40–49': 0,
        '50–59': 0,
        '60+': 0,
    }
    for r in results:
        s = r.get('score', r.get('total_score', 0))
        if s < 0:
            buckets['Negative'] += 1
        elif s < 10:
            buckets['0–9'] += 1
        elif s < 20:
            buckets['10–19'] += 1
        elif s < 30:
            buckets['20–29'] += 1
        elif s < 40:
            buckets['30–39'] += 1
        elif s < 50:
            buckets['40–49'] += 1
        elif s < 60:
            buckets['50–59'] += 1
        else:
            buckets['60+'] += 1
    return buckets


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@main.route('/')
def index():
    """Home dashboard — system-wide stats and recent runs."""
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)


@main.route('/upload-form')
def upload_form():
    """Dedicated upload page."""
    return render_template('upload.html', required_columns=REQUIRED_COLUMNS)


@main.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and processing."""
    if 'file' not in request.files:
        flash('No file selected. Please choose a CSV file to upload.', 'error')
        return redirect(url_for('main.upload_form'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected. Please choose a CSV file to upload.', 'error')
        return redirect(url_for('main.upload_form'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a CSV file.', 'error')
        return redirect(url_for('main.upload_form'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    is_valid, df, errors = validate_csv_file(filepath)

    if not is_valid:
        for error in errors:
            flash(f'{error.error_type}: {error.message} {error.details or ""}', 'error')
        os.remove(filepath)
        return redirect(url_for('main.upload_form'))

    engine = DecisionEngine()
    results, metrics = engine.evaluate_dataset(df)

    results_data = _normalize_results([result.to_dict() for result in results])
    rules_summary = engine.get_rules_summary()
    metrics_data = metrics.to_dict()

    run_id = save_evaluation_run(filename, results_data, metrics_data)
    classification_summary = get_classification_summary(run_id)
    score_dist = _score_distribution(results_data)

    total_records = len(results_data)
    os.remove(filepath)

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
        score_dist=score_dist,
        metrics=metrics_data,
        page=page,
        total_pages=total_pages,
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

    all_results = _normalize_results(run_data['results'])
    score_dist = _score_distribution(all_results)

    page = request.args.get('page', 1, type=int)
    total_records = run_data['total_records']
    start_idx = (page - 1) * RECORDS_PER_PAGE
    end_idx = start_idx + RECORDS_PER_PAGE
    paginated_results = all_results[start_idx:end_idx]
    total_pages = (total_records + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE

    return render_template(
        'results.html',
        results=paginated_results,
        all_results=all_results,
        rules=rules,
        total_records=total_records,
        filename=run_data['filename'],
        run_id=run_id,
        classification_summary=classification_summary,
        score_dist=score_dist,
        metrics=run_data.get('metrics'),
        is_historical=True,
        page=page,
        total_pages=total_pages,
    )


@main.route('/export/<int:run_id>')
def export_csv(run_id):
    """Export evaluation results to CSV file."""
    run_data = get_run_results(run_id)

    if not run_data:
        flash('Evaluation run not found.', 'error')
        return redirect(url_for('main.view_history'))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Record_ID', 'Score', 'Classification', 'Explanation'])

    for result in run_data['results']:
        writer.writerow([
            result['record_id'],
            result.get('score', result.get('total_score')),
            result['classification'],
            result['explanation'].replace('\n', ' | '),
        ])

    output.seek(0)
    filename = f"evaluation_results_{run_id}.csv"

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@main.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """
    REST API endpoint — evaluate records from a JSON payload.

    Request body:
        {
            "records": [
                {"Record_ID": "R001", "Tenure": 24, "Late_Payments": 0, "Revenue": 5500}
            ]
        }

    Response:
        {
            "status": "success",
            "total_records": 1,
            "results": [...],
            "metrics": {...}
        }
    """
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

    data = request.get_json()

    if 'records' not in data or not isinstance(data['records'], list):
        return jsonify({
            'status': 'error',
            'message': 'Request body must contain a "records" array',
        }), 400

    records = data['records']
    if len(records) == 0:
        return jsonify({'status': 'error', 'message': '"records" array cannot be empty'}), 400

    # Validate required columns
    required = {'Record_ID', 'Tenure', 'Late_Payments', 'Revenue'}
    for i, record in enumerate(records):
        missing = required - set(record.keys())
        if missing:
            return jsonify({
                'status': 'error',
                'message': f'Record at index {i} is missing fields: {", ".join(sorted(missing))}',
            }), 400

    # Evaluate
    import time
    engine = DecisionEngine()
    start = time.perf_counter()
    results = [engine.evaluate_record(rec) for rec in records]
    elapsed_ms = (time.perf_counter() - start) * 1000

    return jsonify({
        'status': 'success',
        'total_records': len(results),
        'results': [
            {
                'record_id': r.record_id,
                'score': r.total_score,
                'classification': r.classification,
                'triggered_rules': [
                    {'name': rule['name'], 'weight': rule['weight']}
                    for rule in r.triggered_rules
                ],
                'explanation': r.explanation,
            }
            for r in results
        ],
        'metrics': {
            'runtime_ms': round(elapsed_ms, 2),
            'records_per_second': round(len(results) / (elapsed_ms / 1000), 1) if elapsed_ms > 0 else 0,
        },
    })


@main.route('/api/runs', methods=['GET'])
def api_runs():
    """REST API — return all evaluation runs as JSON."""
    runs = get_evaluation_runs()
    return jsonify({'status': 'success', 'runs': runs})


@main.route('/api/runs/<int:run_id>', methods=['GET'])
def api_run_detail(run_id):
    """REST API — return results for a specific run as JSON."""
    run_data = get_run_results(run_id)
    if not run_data:
        return jsonify({'status': 'error', 'message': f'Run {run_id} not found'}), 404
    return jsonify({'status': 'success', 'run': run_data})
