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
    return redirect(url_for('results'))

@app.route("/results", methods=["GET"])
def results():
    race_status = rhracestatusrepo.get_latest_entry()
    results = rhresultsrepo.get_latest_entry()
    heats = rhheatsrepo.get_latest_entry()
    pilots = rhpilotsrepo.get_latest_entry()
    frequency = rhfrequencyrepo.get_latest_entry()

    current_heat = converter.current_heat(race_status, heats)
    current_pilots = converter.current_pilots(race_status, heats, pilots, frequency)
    pilot_results = converter.pilot_results(results, heats, pilots)
    pilots_progression = converter.pilots_progression(results, pilots)

    return render_template(
        "results.html",
        current_heat=current_heat,
        current_pilots=current_pilots,
        pilot_results=pilot_results,
        pilots_progression=pilots_progression
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

