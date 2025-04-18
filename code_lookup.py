from flask import request, Blueprint

from db_model import TeamSubmittedCode, Code, WrongCode, TeamArrived, TeamSolved, ArrivalCode, SolutionCode
from helpers import render, admin_required

code_lookup = Blueprint('code_lookup', __name__, template_folder='templates', static_folder='static')


@code_lookup.route('/code_lookup', methods=("GET", "POST"))
@admin_required
def lookup():
    """
    Page for looking up teams that have used a specific code.
    """
    results = []
    search_code = ""

    if request.method == "POST":
        search_code = request.form.get("code", "").strip()
        if search_code:
            submitted_codes = TeamSubmittedCode.query\
                .join(Code)\
                .filter(Code.code == search_code)\
                .all()
            arrival_codes = TeamArrived.query\
                .join(ArrivalCode)\
                .filter(ArrivalCode.code == search_code)\
                .all()
            solution_codes = TeamSolved.query\
                .join(SolutionCode)\
                .filter(SolutionCode.code == search_code)\
                .all()
            wrong_codes = WrongCode.query \
                .filter_by(code=search_code) \
                .all()

            results = submitted_codes + wrong_codes + arrival_codes + solution_codes
            results = sorted(results, key=lambda e: e.timestamp, reverse=True)

    return render("code_lookup.html", results=results, search_code=search_code, fluid=True)
