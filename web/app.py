from flask import Flask, render_template, redirect, url_for
from flask import Flask, render_template, redirect, url_for, Response
from storage import RHClassesRepository, RHFrequencyRepository, RHPilotsRepository, RHRaceStatusRepository, init_db, RHResultsRepository, RHHeatsRepository
import converter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Repository instances
rhclassesrepo = RHClassesRepository()
rhpilotsrepo = RHPilotsRepository()
rhresultsrepo = RHResultsRepository()
rhheatsrepo = RHHeatsRepository()
rhracestatusrepo = RHRaceStatusRepository()
rhfrequencyrepo = RHFrequencyRepository()

init_db()

def authenticate():
    return Response(
        'Unauthorized access. Provide valid credentials.\n',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

@app.route("/")
def index():
    return redirect(url_for('race'))

@app.route("/race", methods=["GET"])
def race():
    race_status = rhracestatusrepo.get_latest_entry()
    heats = rhheatsrepo.get_latest_entry()
    frequency = rhfrequencyrepo.get_latest_entry()
    pilots = rhpilotsrepo.get_latest_entry()

    current_heat = converter.current_heat(race_status, heats)
    current_pilots = converter.current_pilots(race_status, heats, pilots, frequency)

    return render_template(
        "race.html",
        current_heat=current_heat,
        current_pilots=current_pilots
    )

@app.route("/results", methods=["GET"])
def results():
    results = rhresultsrepo.get_latest_entry()
    heats = rhheatsrepo.get_latest_entry()
    pilots = rhpilotsrepo.get_latest_entry()

    pilot_results = converter.pilot_results(results, heats, pilots)
    pilots_progression = converter.pilots_progression(results, pilots)

    return render_template(
        "results.html",
        pilot_results=pilot_results,
        pilots_progression=[p.dict() for p in pilots_progression]
    )

@app.route("/pilot/<int:pilot_id>", methods=["GET"])
def pilot(pilot_id):
    # get pilot list
    pilots = rhpilotsrepo.get_latest_entry()
    if not pilots or not any(p.pilot_id == pilot_id for p in pilots.pilots):
        return render_template("pilot_not_found.html")

    # get results
    heats = rhheatsrepo.get_latest_entry()
    results = rhresultsrepo.get_latest_entry()

    # Get pilot info
    pilot_info = converter.pilot_result(results, heats, pilots, pilot_id)

    lap_times = [
        {"lap": 1, "round": "Round 1", "time": 22.1},
        {"lap": 2, "round": "Round 1", "time": 21.7},
        {"lap": 1, "round": "Round 2", "time": 20.4},
        {"lap": 2, "round": "Round 2", "time": 20.1},
        {"lap": 3, "round": "Round 2", "time": 19.8},
    ]

    # Organize laps by round
    from collections import defaultdict
    laps_by_round = defaultdict(list)
    for lap in lap_times:
        laps_by_round[lap["round"]].append(lap)

    return render_template(
        "pilot.html",
        pilot=pilot_info,
        lap_times=lap_times,
        laps_by_round=laps_by_round
    )


@app.route("/heats")
def heats():
    classes = rhclassesrepo.get_latest_entry()
    results = rhresultsrepo.get_latest_entry()
    heats = rhheatsrepo.get_latest_entry()
    pilots = rhpilotsrepo.get_latest_entry()
    frequency = rhfrequencyrepo.get_latest_entry()

    rounds = converter.rounds(results, heats, classes, pilots, frequency)

    return render_template("heats.html", rounds=rounds)

if __name__ == "__main__":
    app.run(debug=True)

