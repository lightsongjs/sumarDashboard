from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import csv
import os

# Increase CSV field size limit to handle large fields
csv.field_size_limit(10000000)

app = Flask(__name__, static_folder='ticket_commenter_static')
CORS(app)

CSV_FILE = 'tickets.csv'

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
    print("Starting server on http://localhost:5000")
    app.run(debug=True, port=5000)
