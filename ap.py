from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Rule-based Mulank and Life Path compatibility scores (0-100 scale for simplicity)
rule_based_compatibility = {
    (1, 1): 85, (1, 2): 60, (1, 3): 70, (1, 4): 50, (1, 5): 90, (1, 6): 75, (1, 7): 60, (1, 8): 65, (1, 9): 80,
    (2, 1): 60, (2, 2): 85, (2, 3): 65, (2, 4): 75, (2, 5): 60, (2, 6): 70, (2, 7): 88, (2, 8): 55, (2, 9): 65,
    (3, 1): 70, (3, 2): 65, (3, 3): 85, (3, 4): 60, (3, 5): 75, (3, 6): 80, (3, 7): 65, (3, 8): 55, (3, 9): 92,
    (4, 1): 50, (4, 2): 75, (4, 3): 60, (4, 4): 85, (4, 5): 65, (4, 6): 70, (4, 7): 60, (4, 8): 80, (4, 9): 55,
    (5, 1): 90, (5, 2): 60, (5, 3): 75, (5, 4): 65, (5, 5): 85, (5, 6): 75, (5, 7): 70, (5, 8): 60, (5, 9): 80,
    (6, 1): 75, (6, 2): 70, (6, 3): 80, (6, 4): 70, (6, 5): 75, (6, 6): 85, (6, 7): 65, (6, 8): 60, (6, 9): 70,
    (7, 1): 60, (7, 2): 88, (7, 3): 65, (7, 4): 60, (7, 5): 70, (7, 6): 65, (7, 7): 85, (7, 8): 55, (7, 9): 65,
    (8, 1): 65, (8, 2): 55, (8, 3): 55, (8, 4): 80, (8, 5): 60, (8, 6): 60, (8, 7): 55, (8, 8): 85, (8, 9): 70,
    (9, 1): 80, (9, 2): 65, (9, 3): 92, (9, 4): 55, (9, 5): 80, (9, 6): 70, (9, 7): 65, (9, 8): 70, (9, 9): 85
}
rule_based_life_path_compatibility = {
    (1, 1): 80, (1, 2): 70, (1, 3): 75, (1, 4): 65, (1, 5): 85, (1, 6): 78, (1, 7): 60, (1, 8): 68, (1, 9): 73,
    (2, 1): 70, (2, 2): 85, (2, 3): 68, (2, 4): 75, (2, 5): 65, (2, 6): 80, (2, 7): 88, (2, 8): 60, (2, 9): 66,
    (3, 1): 75, (3, 2): 68, (3, 3): 85, (3, 4): 70, (3, 5): 80, (3, 6): 77, (3, 7): 66, (3, 8): 58, (3, 9): 90,
    (4, 1): 65, (4, 2): 75, (4, 3): 70, (4, 4): 85, (4, 5): 67, (4, 6): 78, (4, 7): 68, (4, 8): 82, (4, 9): 60,
    (5, 1): 85, (5, 2): 65, (5, 3): 80, (5, 4): 67, (5, 5): 85, (5, 6): 75, (5, 7): 72, (5, 8): 68, (5, 9): 80,
    (6, 1): 78, (6, 2): 80, (6, 3): 77, (6, 4): 78, (6, 5): 75, (6, 6): 85, (6, 7): 65, (6, 8): 70, (6, 9): 72,
    (7, 1): 60, (7, 2): 88, (7, 3): 66, (7, 4): 68, (7, 5): 72, (7, 6): 65, (7, 7): 85, (7, 8): 60, (7, 9): 68,
    (8, 1): 68, (8, 2): 60, (8, 3): 58, (8, 4): 82, (8, 5): 68, (8, 6): 70, (8, 7): 60, (8, 8): 85, (8, 9): 74,
    (9, 1): 73, (9, 2): 66, (9, 3): 90, (9, 4): 60, (9, 5): 80, (9, 6): 72, (9, 7): 68, (9, 8): 74, (9, 9): 85
}

# Weightage for various components
weights = {
    'sun_sign': 0.3,
    'north_chart': 0.2,
    'south_chart': 0.2,
    'mulank': 0.3,
    'life_path': 0.2
}

def calculate_mulank(dob):
    return sum(int(d) for d in dob.strftime('%d')) % 9 or 9


def calculate_life_path(dob):
    return sum(int(d) for d in dob.strftime('%Y%m%d')) % 9 or 9

def get_freeastro_data(person):
    response = requests.post("https://api.freeastroapi.com/compatibility", json=person)
    return response.json() if response.status_code == 200 else {}

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dob1 = datetime.strptime(request.form['dob1'], '%Y-%m-%d')
        dob2 = datetime.strptime(request.form['dob2'], '%Y-%m-%d')

        sun_sign1 = request.form['sun_sign1']
        sun_sign2 = request.form['sun_sign2']

        # Mulank and Life Path Calculation
        m1 = calculate_mulank(dob1)
        m2 = calculate_mulank(dob2)
        l1 = calculate_life_path(dob1)
        l2 = calculate_life_path(dob2)

        # Rule-based score (fallback to 50 if not predefined)
        mulank_score = rule_based_compatibility.get((m1, m2), 50)
        life_path_score = rule_based_life_path_compatibility.get((l1, l2), 50)

        # API Call to get astrological data (Mocked structure)
        astro_data = get_freeastro_data({
            "person1": {"sun_sign": sun_sign1},
            "person2": {"sun_sign": sun_sign2}
        })

        sun_score = astro_data.get("sun_sign_compatibility", 50)
        north_score = astro_data.get("north_chart_compatibility", 50)
        south_score = astro_data.get("south_chart_compatibility", 50)

        # Weighted compatibility
        final_score = round((
            sun_score * weights['sun_sign'] +
            north_score * weights['north_chart'] +
            south_score * weights['south_chart'] +
            mulank_score * weights['mulank'] +
            life_path_score * weights['life_path']
        ), 2)

        return render_template("result.html", score=final_score)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)




