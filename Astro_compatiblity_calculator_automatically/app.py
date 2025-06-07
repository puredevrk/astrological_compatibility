from flask import Flask, render_template, request
import csv
from datetime import datetime

app = Flask(__name__)

# Load nakshatra compatibility data from CSV
nakshatra_compatibility = {}
with open('nakhatra_data.txt', mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        if len(row) < 3:
            continue  # Skip malformed or empty rows
        key = (row[0].strip(), row[1].strip())
        try:
            nakshatra_compatibility[key] = float(row[2].strip())
        except ValueError:
            continue  # Skip if compatibility is not a valid float


# Rule-based Mulank compatibility scores
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
def calculate_life_path(dob):
    return sum(int(d) for d in dob.strftime('%Y%m%d')) % 9 or 9
# Zodiac sign compatibility scores (example)
sun_signs = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

compatibility_values = [
    [50, 38, 83, 42, 97, 63, 85, 50, 93, 47, 78, 67],
    [38, 65, 33, 97, 73, 90, 65, 88, 30, 98, 58, 85],
    [83, 33, 60, 65, 88, 68, 90, 28, 60, 68, 85, 53],
    [42, 97, 65, 75, 35, 90, 43, 94, 53, 83, 27, 98],
    [97, 73, 88, 35, 90, 45, 35, 97, 58, 93, 35, 88],
    [63, 90, 68, 90, 65, 68, 75, 35, 48, 95, 68, 88],
    [85, 65, 90, 43, 35, 68, 75, 35, 73, 55, 90, 88],
    [50, 88, 28, 94, 97, 35, 35, 88, 80, 28, 95, 97],
    [93, 30, 60, 53, 58, 48, 73, 80, 45, 60, 90, 63],
    [47, 98, 68, 83, 93, 95, 55, 28, 60, 75, 68, 88],
    [78, 58, 85, 27, 35, 68, 90, 95, 90, 68, 45, 60],
    [67, 85, 53, 98, 88, 88, 88, 97, 63, 88, 45, 60],
]

sun_sign_compatibility = {}
for i, sign1 in enumerate(sun_signs):
    for j, sign2 in enumerate(sun_signs):
        sun_sign_compatibility[(sign1, sign2)] = compatibility_values[i][j]


# Updated weights
weights = {
    'sun_sign': 0.3,
    'nakshatra': 0.4,
    'mulank': 0.2,
    'life_path': 0.1
}


def calculate_mulank(dob):
    return sum(int(d) for d in dob.strftime('%d')) % 9 or 9

def calculate_sun_sign(dob):
    day = dob.day
    month = dob.month
    zodiac = [
        ((1, 20), "Capricorn"), ((2, 19), "Aquarius"), ((3, 20), "Pisces"),
        ((4, 20), "Aries"), ((5, 21), "Taurus"), ((6, 21), "Gemini"),
        ((7, 23), "Cancer"), ((8, 23), "Leo"), ((9, 23), "Virgo"),
        ((10, 23), "Libra"), ((11, 22), "Scorpio"), ((12, 22), "Sagittarius"),
        ((12, 31), "Capricorn")
    ]
    for i, ((m, d), sign) in enumerate(zodiac):
        if (month == m and day <= d) or (month == m - 1 and day > zodiac[i - 1][0][1]):
            return sign
    return "Capricorn"

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        dob1 = datetime.strptime(request.form['dob1'], '%Y-%m-%d')
        dob2 = datetime.strptime(request.form['dob2'], '%Y-%m-%d')
        nak1 = request.form['nakshatra1']
        nak2 = request.form['nakshatra2']

        m1 = calculate_mulank(dob1)
        m2 = calculate_mulank(dob2)
        mulank_score = rule_based_compatibility.get((m1, m2), 50)
        l1 = calculate_life_path(dob1)
        l2 = calculate_life_path(dob2)
        life_path_score = rule_based_life_path_compatibility.get((l1, l2), 50)
        sign1 = calculate_sun_sign(dob1)
        sign2 = calculate_sun_sign(dob2)
        sun_score = sun_sign_compatibility.get((sign1, sign2), 50)

        nak_score = nakshatra_compatibility.get((nak1, nak2), 50)

        final_score = round(
            sun_score * weights['sun_sign'] +
            nak_score * weights['nakshatra'] +
            mulank_score * weights['mulank'] +
            life_path_score * weights['life_path'], 2
        )

        return render_template("result.html",
                       score=final_score,
                       nakshatra1=nak1,
                       nakshatra2=nak2,
                       sun_sign1=sign1,
                       sun_sign2=sign2,
                       mulank1=m1,
                       mulank2=m2,
                       life_path1=l1,
                       life_path2=l2)


    return render_template("index.html")

if __name__ == "__main__":
    app.run()
