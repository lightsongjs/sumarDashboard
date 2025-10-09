from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import csv
import os

# Increase CSV field size limit to handle large fields
csv.field_size_limit(10000000)

app = Flask(__name__, static_folder='ticket_commenter_static')
CORS(app)

CSV_FILE = 'tickets.csv'

# Global cache for filter options (loaded at startup)
FILTER_OPTIONS_CACHE = {}

def read_tickets():
    """Citește toate ticketele din CSV"""
    tickets = []
    if not os.path.exists(CSV_FILE):
        return tickets

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(row)
    return tickets

def write_tickets(tickets):
    """Scrie toate ticketele înapoi în CSV"""
    if not tickets:
        return

    fieldnames = list(tickets[0].keys())

    with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tickets)

def load_filter_options():
    """Încarcă opțiunile de filtrare din CSV la startup (cache)"""
    tickets = read_tickets()

    # Coloanele care sunt folosite ca filtre
    filter_columns = ['mailbox_name', 'tip', 'area', 'sentiment', 'urgency', 'platform', 'integration']

    filter_options = {}

    for column in filter_columns:
        values = set()
        for ticket in tickets:
            value = ticket.get(column, '')
            # Include doar valori non-empty și diferite de '-'
            if value and value.strip() and value.strip() != '-':
                values.add(value.strip())

        # Convertește la listă sortată
        filter_options[column] = sorted(list(values))

    return filter_options

@app.route('/')
def index():
    """Servește pagina principală"""
    return send_from_directory('ticket_commenter_static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Servește fișiere statice"""
    return send_from_directory('ticket_commenter_static', path)

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """API: Returnează toate ticketele"""
    tickets = read_tickets()
    return jsonify(tickets)

@app.route('/api/filter-options', methods=['GET'])
def get_filter_options():
    """API: Returnează opțiunile unice pentru fiecare filtru din cache"""
    return jsonify(FILTER_OPTIONS_CACHE)

@app.route('/api/tickets/<int:index>/comment', methods=['POST'])
def update_comment(index):
    """API: Updatează comentariul pentru un ticket"""
    data = request.json
    comment = data.get('comment', '')

    tickets = read_tickets()

    if index < 0 or index >= len(tickets):
        return jsonify({'error': 'Invalid ticket index'}), 400

    # Updatează comentariul
    tickets[index]['Comments'] = comment

    # Salvează înapoi în CSV
    write_tickets(tickets)

    return jsonify({'success': True, 'comment': comment})

if __name__ == '__main__':
    print("Loading filter options into cache...")
    FILTER_OPTIONS_CACHE = load_filter_options()
    print(f"Cached {len(FILTER_OPTIONS_CACHE)} filter columns")
    print("Starting server on http://localhost:5000")
    app.run(debug=True, port=5000)
