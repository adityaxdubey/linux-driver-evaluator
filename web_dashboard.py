from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """api endpoint for code evaluation"""
    code = request.json.get('code', '')
    model_type = request.json.get('model', 'mock')
    
    # integrate with your existing evaluation system
    from src.evaluator.enhanced_evaluator import EnhancedDriverEvaluator
    evaluator = EnhancedDriverEvaluator()
    
    prompt_info = {'id': 'web_submission', 'timestamp': datetime.now().isoformat()}
    result = evaluator.comprehensive_evaluation(code, prompt_info)
    
    return jsonify(result)

@app.route('/api/history')
def api_history():
    """get evaluation history"""
    history = []
    if os.path.exists('results'):
        for filename in os.listdir('results'):
            if filename.endswith('.json'):
                with open(f'results/{filename}', 'r') as f:
                    data = json.load(f)
                    history.append({
                        'filename': filename,
                        'score': data.get('enhanced_score', 0),
                        'timestamp': data.get('metadata', {}).get('timestamp', '')
                    })
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
