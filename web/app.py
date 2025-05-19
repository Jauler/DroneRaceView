from flask import Flask, render_template, redirect, url_for
from flask import Flask, render_template, redirect, url_for, Response
from storage import RHClassesRepository, RHFrequencyRepository, RHPilotsRepository, RHRaceStatusRepository, init_db, RHResultsRepository, RHHeatsRepository, RHFormatsRepository

import converters.results_converter as results_converter
import converters.rounds_converter as rounds_converter
import converters.pilot_info_converter as pilot_info_converter

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
rhformatsrepo = RHFormatsRepository()

init_db()

def authenticate():
    return Response(
        'Unauthorized access. Provide valid credentials.\n',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

@app.route("/")
def index():
    return redirect(url_for('heats'))

@app.route("/results", methods=["GET"])
def results():
    results = rhresultsrepo.get_latest_entry()
    classes = rhclassesrepo.get_latest_entry()
    pilots = rhpilotsrepo.get_latest_entry()
    formats = rhformatsrepo.get_latest_entry()

    results = results_converter.results(results, pilots, classes, formats)

    return render_template(
        "results.html",
        results=results,
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
    pilot_info = pilot_info_converter.pilot_result(results, heats, pilots, pilot_id)
    pilot_lap_times = pilot_info_converter.pilot_lap_times(results, pilot_id)
    pilot_rounds = pilot_info_converter.pilot_rounds(results, heats, pilot_id)

    return render_template(
        "pilot.html",
        pilot=pilot_info,
        pilot_lap_times=pilot_lap_times,
        pilot_rounds=pilot_rounds
    )


@app.route("/heats")
def heats():
    classes = rhclassesrepo.get_latest_entry()
    results = rhresultsrepo.get_latest_entry()
    heats = rhheatsrepo.get_latest_entry()
    pilots = rhpilotsrepo.get_latest_entry()
    frequency = rhfrequencyrepo.get_latest_entry()

    rounds = rounds_converter.rounds(results, heats, classes, pilots, frequency)

    return render_template("heats.html", rounds=rounds)

if __name__ == "__main__":
    app.run(debug=True)

