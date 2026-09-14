import os

from flask import (
    Flask,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.puzzle_generator import PuzzleGenerator


app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static",
)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "the-33rd-key-local-development",
)

generator = PuzzleGenerator(seed=330033)


def normalize_answer(answer):
    return " ".join(answer.strip().upper().split())


@app.route("/", methods=["GET", "POST"])
def home():

    if "spread" not in session:
        session["spread"] = 1

    if "solved" not in session:
        session["solved"] = []

    if "clues" not in session:
        session["clues"] = {}

    if "turn_pending" not in session:
        session["turn_pending"] = False

    spread = session["spread"]
    puzzle = generator.generate(spread)

    if request.method == "POST":

        action = request.form.get("action", "answer")

        if action == "clue":

            clues = session["clues"]
            key = str(spread)

            clue_level = clues.get(key, 0)
            hints = puzzle["hints"]

            if clue_level >= len(hints):
                flash("No further clues remain, maestro.")
            else:
                flash(hints[clue_level])

                clues[key] = clue_level + 1
                session["clues"] = clues

            return redirect(url_for("home"))

        submitted = normalize_answer(
            request.form.get("answer", "")
        )

        valid_answers = {
            normalize_answer(answer)
            for answer in puzzle["answers"]
        }

        if not submitted:

            flash("A key must first be offered.")

        elif submitted in valid_answers:

            solved = session["solved"]

            if spread not in solved:
                solved.append(spread)

            session["solved"] = solved
            session["turn_pending"] = True

            flash("THE KEY TURNS.")

            return redirect(url_for("home"))

        else:

            flash("THE KEY DOES NOT TURN.")

    return render_template(
        "index.html",
        puzzle=puzzle,
        spread=spread,
        turn_pending=session.get("turn_pending", False),
    )


@app.route("/advance", methods=["POST"])
def advance():

    if session.get("turn_pending"):

        session["spread"] = session.get("spread", 1) + 1
        session["turn_pending"] = False

    return redirect(url_for("home"))


@app.route("/forward", methods=["POST"])
def forward():

    spread = session.get("spread", 1)
    solved = session.get("solved", [])

    # Published rule:
    # a previously solved spread may be revisited and
    # turned forward without solving it again.
    if spread in solved:

        session["spread"] = spread + 1
        session["turn_pending"] = False

        next_spread = session["spread"]
        puzzle = generator.generate(next_spread)

        response = make_response(
            render_template(
                "index.html",
                puzzle=puzzle,
                spread=next_spread,
                turn_pending=False,
            )
        )

        response.headers["X-Page-Turn-Allowed"] = "true"

        return response

    # The newest unsolved puzzle is the boundary.
    flash("THE PAGE WILL NOT TURN.")

    puzzle = generator.generate(spread)

    response = make_response(
        render_template(
            "index.html",
            puzzle=puzzle,
            spread=spread,
            turn_pending=False,
        )
    )

    response.headers["X-Page-Turn-Allowed"] = "false"

    return response


@app.route("/back", methods=["POST"])
def back():

    spread = session.get("spread", 1)

    if spread > 1:
        session["spread"] = spread - 1

    session["turn_pending"] = False

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
